"""Research agent (one per profile).

The agent does not invent findings. It turns agent-drafted briefs (one JSON
file per feature, written from official pages) into cell records, but only
after fetching each cited page and confirming every quote appears inside the
section it cites. Features without a verified brief stay pending. The
evidence-challenge pass (challenge.py) runs afterwards. Neither is a team review.
"""
import glob
import json
import os
import threading

from . import model
from . import pages
from . import sources as src
from . import store as st

AFFIRMATIVE = ('Built in', 'Configuration or extension required', 'Custom implementation required')


def load_briefs(cand, surface):
    briefs = {}
    for f in sorted(glob.glob(os.path.join(cand['_dir'], 'briefs', surface, 'F*.json'))):
        with open(f, encoding='utf-8') as fh:
            b = json.load(fh)
        briefs[b['feature_id']] = b
    return briefs


def apply_brief(cell, brief, refs, rejected, profile_id, operator):
    status = brief['status']
    basis = brief.get('evidence_basis') or (
        'documented_support' if status in AFFIRMATIVE else
        'documented_absence' if status == 'Unavailable' else 'documentation_gap')
    cell.update({
        'status': status, 'assessment_state': 'drafted', 'evidence_basis': basis,
        'evidence_refs': refs, 'gap_reason': brief.get('gap_reason'),
        'supported_scope': brief.get('supported_scope', 'Not established'),
        'unsupported_scope': brief.get('unsupported_scope', []),
        'unestablished_scope': brief.get('unestablished_scope', []),
        'required_setup': brief.get('required_setup', 'Not established'),
        'activation_state': brief.get('activation_state', 'not established'),
        'control_mechanism': brief.get('control_mechanism', 'not established'),
        'constraints': brief.get('constraints', []),
        'drafted_by': 'agent', 'assessment_date': st.today(), 'author': None,
        'rejected_citations': rejected, 'challenge': None,
    })
    model.touch(cell, 'drafted', by='research-agent:' + profile_id, operator=operator,
                verified_refs=refs, rejected=len(rejected))


class ResearchAgent:
    def __init__(self, store, index, cand, profile, operator, progress, lock):
        self.store, self.index, self.cand, self.profile = store, index, cand, profile
        self.operator, self.progress, self.lock = operator, progress, lock
        self.docs = cand['docs']
        self.result = {'drafted': 0, 'left_pending': 0, 'kept': 0, 'rejected_quotes': 0, 'features': {}}

    def say(self, n, total, fid, msg, key=None):
        if key:
            self.result['features'][fid] = msg
        self.progress('assess', n, total, '%s %s  %s' % (self.profile['id'], fid, msg))

    def verify(self, brief):
        refs, rejected = [], []
        for ev in brief['evidence']:
            url = src.doc_url(self.docs, ev['page'])
            with self.lock:
                rec, text, _ = self.index.page(url, self.docs)
            if rec.get('status') != 'ok':
                rejected.append('%s: page %s' % (ev['page'], rec.get('status')))
                continue
            check = pages.locate(text, ev['section'], ev['quote'],
                                 self.docs.get('surface_labels', {}), rec.get('available_on', []))
            if check['status'] != 'verified':
                rejected.append('%s / %s: %s' % (ev['page'], ev['section'], check['status']))
                continue
            with self.lock:
                refs.append(self.index.evidence(url, ev['section'], ev['quote'], check, rec,
                                                ev.get('claim') or brief.get('supported_scope', '')[:240]))
        return refs, rejected

    def run(self, cells, features):
        briefs = load_briefs(self.cand, self.profile['surface'])
        total = len(features)
        for n, f in enumerate(features, 1):
            fid = f['id']
            cell = cells[model.cell_id(fid, self.profile['id'])]
            if cell['assessment_state'] == 'reviewed' or cell.get('author'):
                self.result['kept'] += 1
                self.say(n, total, fid, 'kept (%s; human-owned)' % cell['assessment_state'])
                continue
            brief = briefs.get(fid)
            if not brief:
                self.result['left_pending'] += 1
                self.say(n, total, fid, 'pending: no researched brief for this feature', key=True)
                continue
            refs, rejected = self.verify(brief)
            self.result['rejected_quotes'] += len(rejected)
            if not refs:
                self.result['left_pending'] += 1
                self.say(n, total, fid, 'pending: no citation could be verified', key=True)
                continue
            apply_brief(cell, brief, refs, rejected, self.profile['id'], self.operator)
            self.result['drafted'] += 1
            self.say(n, total, fid, '%s (%d verified ref%s%s)' % (
                brief['status'], len(refs), '' if len(refs) == 1 else 's',
                ', %d rejected' % len(rejected) if rejected else ''), key=True)
        return self.result


class Stopped(Exception):
    """Raised when the operator interrupts or an agent fails; completed cells are kept."""


def run_agents(store, index, candidates, profiles, operator, progress):
    """One research agent per profile, in parallel threads sharing one source index.

    Each drafted cell is complete on its own, so on interruption or agent
    failure the cells finished so far are saved and the run stops before the
    challenge pass and validation; `resume` re-runs it.
    """
    data = store.load('cells.json')
    cells = data['cells']
    features = store.catalog()['features']
    lock, stop = threading.Lock(), threading.Event()
    agents, threads, errors = [], [], {}

    def guarded(agent):
        def stepped(phase, n, total, msg):
            if stop.is_set():
                raise Stopped('stop requested')
            progress(phase, n, total, msg)
        agent.progress = stepped
        try:
            agent.run(cells, features)
        except BaseException as e:  # noqa: B902 - reported to the main thread
            errors[agent.profile['id']] = e
            stop.set()

    for p in profiles:
        cand = candidates.get(p.get('tool_key'))
        if not cand:
            store.log('research_skipped', actor=operator, profile_id=p['id'],
                      reason='no candidate documentation set for this tool')
            continue
        a = ResearchAgent(store, index, cand, p, operator, progress, lock)
        agents.append(a)
        threads.append(threading.Thread(target=guarded, args=(a,), name=p['id'], daemon=True))
    for t in threads:
        t.start()
    try:
        while any(t.is_alive() for t in threads):
            for t in threads:
                t.join(timeout=0.2)
    except KeyboardInterrupt as e:
        stop.set()
        errors.setdefault('operator', e)
        for t in threads:
            t.join(timeout=5)
    with lock:
        store.save('cells.json', data)
        index.save()
    if errors:
        cause = next((e for e in errors.values() if not isinstance(e, Stopped)), None)
        store.log('research_stopped', actor=operator,
                  reason={k: '%s: %s' % (type(v).__name__, v) for k, v in errors.items()},
                  kept_drafts=sum(a.result['drafted'] for a in agents))
        if isinstance(cause, KeyboardInterrupt) or cause is None:
            raise KeyboardInterrupt
        raise Stopped('research agent failed: %s: %s' % (type(cause).__name__, cause))
    return {a.profile['id']: a.result for a in agents}
