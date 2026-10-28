"""Model-assisted brief drafting (SRS Spec 5.4.2 as amended Oct. 22).

For each feature of a profile, the model receives only excerpts of official
documentation pages already fetched by source discovery, and returns a brief
in the same format as a hand-prepared one (status, scope, page/section/quote
evidence). The brief is saved under <dataset>/drafts/<profile>/Fxx.json with
its provenance. It is not a finding: the research agent then re-fetches each
cited page and keeps only quotes found inside the cited section, the challenge
pass flags it, and a named author plus an independent reviewer must accept it.
Nothing here installs, runs or tests an assessed tool.
"""
import json
import os
import re

from . import azure
from . import pages
from . import store as st

# Release notes describe changes, not current behavior; they are down-weighted and capped.
MAX_RELEASE_NOTES = 2

STOP = set('about across after also and are being between both can does each for from have how into its may '
           'more not only other over per such than that the their them then there these this those through '
           'use used uses using when where whether which while with within without your'.split())

SYSTEM = """You draft one feature-matrix brief from official documentation excerpts.
Rules:
- Use only the excerpts provided. Do not use outside knowledge. Do not guess.
- Every evidence quote must be copied verbatim from a single excerpt (8 to 30 words, no ellipses), and
  its "page" and "section" must be copied exactly from that excerpt's header.
- Status must be one of: "Built in", "Configuration or extension required", "Custom implementation required",
  "Unavailable", "Not established from documentation".
- "Unavailable" only when an excerpt explicitly says the capability is unsupported.
- "Custom implementation required" only when an excerpt explicitly describes implementation work.
- If the excerpts are silent, ambiguous or conflicting, use "Not established from documentation", set
  evidence_basis to "documentation_gap" or "documentation_conflict", write a specific gap_reason naming what
  the excerpts do and do not say, and cite the closest relevant passages as evidence.
- Only describe the assessed product surface. Ignore passages about other surfaces.
- Do not judge quality, rank or score.
Return one JSON object with exactly these keys:
{"feature_id": str, "status": str, "evidence_basis": "documented_support"|"documented_absence"|
"documentation_gap"|"documentation_conflict", "gap_reason": str|null, "supported_scope": str,
"unsupported_scope": [str], "unestablished_scope": [str], "required_setup": str,
"activation_state": "default"|"optional"|"policy-dependent"|"not established",
"control_mechanism": "enforced"|"instruction-based"|"mixed"|"not established", "constraints": [str],
"evidence": [{"page": str, "section": str, "quote": str, "claim": str}]}
Use at most 4 evidence items."""


def drafts_dir(store, profile_id):
    return store.path('drafts', profile_id)


def load_drafts(store, profile_id):
    out, d = {}, drafts_dir(store, profile_id)
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if re.match(r'F\d\d\.json$', name):
                with open(os.path.join(d, name), encoding='utf-8') as f:
                    b = json.load(f)
                out[b['feature_id']] = b
    return out


def terms(feature):
    words = re.findall(r'[a-z][a-z-]{3,}', ' '.join(
        (feature['name'], feature['capability'], feature['examine'])).lower())
    return {w.rstrip('s') for w in words if w not in STOP}


def own_sections(text):
    """(path, own body) for every heading: the body runs to the next heading of any level."""
    secs = pages.sections(text)
    heads = [m.start() for m in pages.HEADING.finditer(text)]
    out = []
    for i, s in enumerate(secs):
        end = heads[i + 1] if i + 1 < len(heads) else len(text)
        out.append((s['path'], text[s['body_start']:end].strip()))
    return out


def on_surface(path, labels, surface):
    for title in reversed(path):
        key = pages.surface_key(title, labels)
        if key:
            return key == surface
    return True


def page_id_of(url, docs):
    return url.replace(docs['base_url'], '').strip('/') or url


def select_excerpts(index, urls, docs, surface, feature, budget, per_section=1800):
    """Highest-scoring same-surface sections across the profile's pages, within a character budget."""
    want, labels, scored = terms(feature), docs.get('surface_labels', {}), []
    for url in urls:
        text, rec = index.text.get(url), index.data['pages'].get(url, {})
        if not text or rec.get('status') != 'ok':
            continue
        if rec.get('available_on') and surface not in rec['available_on']:
            continue
        for path, body in own_sections(text):
            if len(body) < 40 or not on_surface(path, labels, surface):
                continue
            title_words = re.findall(r'[a-z][a-z-]{3,}', ' '.join(path).lower())
            body_l = body.lower()
            score = 3 * sum(1 for w in want if any(t.startswith(w) for t in title_words)) + \
                sum(1 for w in want if w in body_l)
            if score:
                release = 'changelog' in url or 'release' in url
                scored.append((score / 2.0 if release else score, release, page_id_of(url, docs),
                               ' > '.join(path), body[:per_section]))
    scored.sort(key=lambda x: (-x[0], x[2], x[3]))
    chosen, used, releases = [], 0, 0
    for _, release, page_id, section, body in scored:
        if release and releases >= MAX_RELEASE_NOTES:
            continue
        if used + len(body) <= budget:
            chosen.append({'page': page_id, 'section': section, 'text': body})
            used += len(body)
            releases += release
    return chosen


def fit(feature, profile, excerpts, max_tokens):
    """Drop the lowest-ranked excerpts until the whole prompt fits the input-token limit."""
    excerpts = list(excerpts)
    while excerpts and azure.estimate_tokens(
            ''.join(m['content'] for m in messages(feature, profile, excerpts))) > max_tokens:
        excerpts.pop()
    return excerpts


def messages(feature, profile, excerpts):
    blocks = ['[page: %s] [section: %s]\n%s' % (e['page'], e['section'], e['text']) for e in excerpts]
    user = ('Assessed profile: %s (%s, surface %s). Exclusions: %s.\n'
            'Feature %s "%s": %s\nExamine: %s\n\nExcerpts:\n\n%s'
            % (profile['id'], profile['tool'], profile.get('surface_label', profile['surface']),
               '; '.join(profile.get('exclusions') or []) or 'none',
               feature['id'], feature['name'], feature['capability'], feature['examine'],
               '\n\n---\n\n'.join(blocks)))
    return [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}]


def excerpt_budget(lim):
    """Characters of excerpts that keep the whole prompt under the input-token limit."""
    return max(0, (lim['max_input_tokens_per_request'] - azure.estimate_tokens(SYSTEM) - 250) * 4)


def check_brief(raw, feature_id, catalog, excerpts):
    """Parse and validate a model response against the brief format.

    Returns (brief, problems). brief is None when the response is unusable.
    Evidence pointing outside the excerpts is dropped (never fetched).
    """
    try:
        b = json.loads(raw)
    except ValueError:
        return None, ['response is not valid JSON']
    if not isinstance(b, dict):
        return None, ['response is not a JSON object']
    problems = []
    statuses = [s['name'] for s in catalog['statuses']]
    enums = {'evidence_basis': catalog['evidence_basis'], 'activation_state': catalog['activation_state'],
             'control_mechanism': catalog['control_mechanism']}
    if b.get('feature_id') != feature_id:
        problems.append('feature_id %r does not match %s' % (b.get('feature_id'), feature_id))
    if b.get('status') not in statuses:
        return None, problems + ['unknown status %r' % b.get('status')]
    for k, allowed in enums.items():
        if b.get(k) not in allowed:
            problems.append('%s %r replaced with a default' % (k, b.get(k)))
            b[k] = None if k == 'evidence_basis' else 'not established'
    for k in ('supported_scope', 'required_setup'):
        if not isinstance(b.get(k), str) or not b[k].strip():
            b[k] = 'Not established'
    for k in ('unsupported_scope', 'unestablished_scope', 'constraints'):
        b[k] = [str(x) for x in b.get(k) or [] if str(x).strip()] if isinstance(b.get(k), list) else []
    if b['status'] == catalog['not_established']:
        if b['evidence_basis'] not in ('documentation_gap', 'documentation_conflict'):
            b['evidence_basis'] = 'documentation_gap'
        if not (b.get('gap_reason') or '').strip():
            return None, problems + ['Not established without a gap reason']
    else:
        b['gap_reason'] = None
    known = {(e['page'], e['section']) for e in excerpts}
    pages_ok = {e['page'] for e in excerpts}
    evidence = []
    for ev in (b.get('evidence') or [])[:4]:
        if not isinstance(ev, dict) or not all(isinstance(ev.get(k), str) and ev[k].strip()
                                               for k in ('page', 'section', 'quote')):
            problems.append('malformed evidence item dropped')
        elif ev['page'] not in pages_ok:
            problems.append('evidence page %r is not one of the excerpts; dropped' % ev['page'][:80])
        else:
            if (ev['page'], ev['section']) not in known:
                problems.append('section %r not an excerpt header; kept for verification' % ev['section'][:80])
            evidence.append({'page': ev['page'], 'section': ev['section'], 'quote': ev['quote'][:400],
                             'claim': str(ev.get('claim') or '')[:240]})
    if not evidence:
        return None, problems + ['no usable evidence']
    keep = ('status', 'evidence_basis', 'gap_reason', 'supported_scope', 'unsupported_scope',
            'unestablished_scope', 'required_setup', 'activation_state', 'control_mechanism', 'constraints')
    brief = {'feature_id': feature_id}
    brief.update({k: b.get(k) for k in keep})
    brief['evidence'] = evidence
    return brief, problems


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    os.replace(tmp, path)


def draft_profile(store, index, cand, profile, urls, client, progress, operator, redraft=False):
    """Draft missing briefs for one profile, one request per feature, sequentially.

    Resumable: a feature with a saved draft (or a saved rejection, unless
    redraft) is skipped, and so is a cell a person already owns. A request error
    for one feature (for example HTTP 400) leaves it pending and moves on; a
    limit stops drafting for the run; azure.Unavailable (refused credentials,
    no response, 429/5xx after retries) is raised so the command stops with an
    error. Drafts saved before that are kept. Returns a summary dict.
    """
    catalog, features = store.catalog(), store.catalog()['features']
    cells = store.load('cells.json')['cells']
    d = drafts_dir(store, profile['id'])
    lim = client.ledger.lim
    budget = excerpt_budget(lim)
    res = {'drafted': 0, 'skipped': 0, 'rejected': 0, 'failed': 0, 'no_excerpts': 0, 'stopped': None}
    conn = client.conn.describe()
    for n, f in enumerate(features, 1):
        fid = f['id']
        target, rejected = os.path.join(d, fid + '.json'), os.path.join(d, fid + '.rejected.json')
        cell = cells.get('%s/%s' % (profile['id'], fid), {})
        if cell.get('author') or cell.get('assessment_state') == 'reviewed':
            res['skipped'] += 1
            progress('draft', n, len(features), '%s %s  kept (human-owned cell)' % (profile['id'], fid))
            continue
        if os.path.exists(target) or (os.path.exists(rejected) and not redraft):
            res['skipped'] += 1
            progress('draft', n, len(features), '%s %s  already drafted in an earlier run' % (profile['id'], fid))
            continue
        if res['stopped']:
            progress('draft', n, len(features), '%s %s  pending (drafting stopped)' % (profile['id'], fid))
            continue
        excerpts = fit(f, profile, select_excerpts(index, urls, cand['docs'], profile['surface'], f, budget),
                       lim['max_input_tokens_per_request'])
        if not excerpts:
            res['no_excerpts'] += 1
            store.log('model_draft_skipped', actor=operator, profile_id=profile['id'], feature_id=fid,
                      reason='no same-surface documentation section matched the feature terms')
            progress('draft', n, len(features), '%s %s  pending: no matching sections' % (profile['id'], fid))
            continue
        label = '%s/%s' % (profile['id'], fid)
        try:
            out = client.chat(messages(f, profile, excerpts), label)
        except azure.LimitReached as e:
            res['stopped'] = 'limit: %s' % e
            store.log('model_limit_reached', actor=operator, profile_id=profile['id'], feature_id=fid,
                      detail=str(e), usage=client.ledger.summary())
            progress('draft', n, len(features), '%s %s  pending: %s' % (profile['id'], fid, e))
            continue
        except azure.Unavailable as e:
            store.log('model_request_failed', actor=operator, profile_id=profile['id'], feature_id=fid,
                      detail=str(e), attempts=getattr(e, 'attempts', []), stops_run=True, **conn)
            raise
        except azure.ModelError as e:
            res['failed'] += 1
            store.log('model_request_failed', actor=operator, profile_id=profile['id'], feature_id=fid,
                      detail=str(e), attempts=getattr(e, 'attempts', []), **conn)
            progress('draft', n, len(features), '%s %s  pending: request failed' % (profile['id'], fid))
            continue
        brief, problems = check_brief(out['content'], fid, catalog, excerpts)
        if out['finish_reason'] not in ('stop', None):
            problems.append('finish_reason %s' % out['finish_reason'])
            if out['finish_reason'] in ('length', 'content_filter'):
                brief = None
        prov = dict(conn, model=out['model'], prompt_version=client.config['prompt_version'],
                    request_id=out['request_id'], usage=out['usage'], estimated_cost_usd=out['cost_usd'],
                    attempts=len(out['attempts']), drafted_at=st.now(), operator=operator,
                    excerpts=[{'page': e['page'], 'section': e['section']} for e in excerpts],
                    response_problems=problems)
        store.log('model_request', actor='drafting:' + profile['id'], feature_id=fid, outcome='ok',
                  accepted_as_draft=brief is not None, **{k: v for k, v in prov.items() if k != 'excerpts'})
        if brief is None:
            res['rejected'] += 1
            _write(rejected, {'feature_id': fid, 'rejected': problems, 'provenance': prov})
            progress('draft', n, len(features), '%s %s  pending: response rejected (%s)'
                     % (profile['id'], fid, '; '.join(problems)[:80]))
            continue
        brief.update({'drafted_by': 'model:azure-openai/%s' % conn['deployment'], 'provenance': prov})
        _write(target, brief)
        if os.path.exists(rejected):
            os.remove(rejected)
        res['drafted'] += 1
        progress('draft', n, len(features), '%s %s  draft: %s (%d citation%s, %d tokens, $%.4f)' % (
            profile['id'], fid, brief['status'], len(brief['evidence']), '' if len(brief['evidence']) == 1 else 's',
            out['usage']['input_tokens'] + out['usage']['output_tokens'], out['cost_usd']))
    return res
