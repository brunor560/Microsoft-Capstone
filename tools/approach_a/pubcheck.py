"""Checks on the public feature-matrix payload (see publish.py).

The public payload carries no names and no roster IDs: it records only that a
named author exists and that an independent review was made. Standard library
only.
"""
import json
import re
from urllib.parse import urlparse

from . import model

SCHEMA = 'approach-a/publication/1'
EMPTY_SCHEMA = 'approach-a/publication-empty/1'
EMPTY_MESSAGE = 'No reviewed assessment published yet.'
MODES = ('accepted', 'preview')
SCORE_KEYS = ('score', 'rank', 'ranking', 'weight', 'points', 'rating')
IDENTITY_KEYS = ('people', 'roster', 'reviewer', 'reviewer_id', 'approver', 'approver_id', 'author_id',
                 'confirmed_by')


def empty_marker():
    """The deliberate "nothing reviewed yet" data file (distinct from a missing file)."""
    return {'schema': EMPTY_SCHEMA, 'message': EMPTY_MESSAGE}


def safe_url(url):
    u = urlparse(url or '')
    return u.scheme == 'https' and bool(u.netloc)


def walk(obj):
    """Yield (key, value) for every dict entry and (None, value) for every list item."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield None, v
            yield from walk(v)


def leaks(payload, roster):
    """Roster IDs or names appearing anywhere in the payload (whole words, case-insensitive)."""
    terms = set()
    for pid, person in roster.items():
        terms.add(pid)
        if person.get('name'):
            terms.add(person['name'])
    found = []
    for term in sorted(terms):
        rx = re.compile(r'(?<!\w)%s(?!\w)' % re.escape(term), re.I)
        if any(isinstance(v, str) and rx.search(v) for _, v in walk(payload)):
            found.append('roster identity %r appears in the payload' % term)
    return found


def _structure(p, bad):
    statuses = {s['name'] for s in p['catalog']['statuses']}
    feats = [f['id'] for f in p['catalog']['features']]
    pids = [x['id'] for x in p['profiles']]
    if len(feats) != 18 or len(statuses) != 5:
        bad.append('catalog must define 18 features and 5 statuses')
    if not pids:
        bad.append('no profiles (P = 0)')
    if len(set(pids)) != len(pids):
        bad.append('duplicate profile ids')
    got = [(c['profile_id'], c['feature_id']) for c in p['cells']]
    if len(got) != len(set(got)) or set(got) != {(pid, f) for pid in pids for f in feats}:
        bad.append('cells do not cover exactly 18 x P feature/profile pairs')
    for e in p['evidence']:
        if not safe_url(e.get('url')):
            bad.append('evidence %s has an unsafe or missing URL' % e.get('id'))
    keys = {k.lower() for k, _ in walk(p) if isinstance(k, str)}
    for k in sorted(keys & set(SCORE_KEYS)):
        bad.append('score or rank field %r is not allowed' % k)
    for k in sorted(keys & set(IDENTITY_KEYS)):
        bad.append('identity field %r is not allowed in the public payload' % k)
    return statuses


def _accepted_cell(c, cid, statuses, evidence, bad):
    if c.get('status') not in statuses:
        bad.append('%s: unknown status %r' % (cid, c.get('status')))
    if c.get('assessment_state') == 'pending':
        bad.append('%s: pending cell in an accepted release' % cid)
    for r in c.get('evidence_refs', []):
        if r not in evidence:
            bad.append('%s: dangling evidence %s' % (cid, r))
        elif not evidence[r].get('quotation_matched'):
            bad.append('%s: evidence %s quotation not matched' % (cid, r))
    rv = c.get('review')
    if not rv or rv.get('stale') or rv.get('decision') != 'agree':
        bad.append('%s: no current agreeing review' % cid)
    elif not c.get('author') or not rv.get('independent'):
        bad.append('%s: missing author or review is not independent' % cid)
    elif rv.get('cell_sha256') != c.get('cell_sha256'):
        bad.append('%s: review does not match the exported cell' % cid)


def check_payload(p):
    """Publication-specific checks on the payload itself. Returns a list of problems."""
    if not isinstance(p, dict) or p.get('schema') != SCHEMA:
        return ['unsupported schema %r' % (p.get('schema') if isinstance(p, dict) else None)]
    bad = []
    rel = p.get('release', {})
    mode = rel.get('publication_mode')
    if mode not in MODES:
        bad.append('unknown publication mode %r' % mode)
    statuses = _structure(p, bad)
    evidence = {e['id']: e for e in p['evidence']}
    for c in p['cells']:
        cid = model.cell_id(c['feature_id'], c['profile_id'])
        if c.get('author') not in (None, {'recorded': True}):
            bad.append('%s: author must carry no identity' % cid)
        if mode == 'accepted':
            _accepted_cell(c, cid, statuses, evidence, bad)
    if mode == 'accepted' and not rel.get('approval'):
        bad.append('accepted release has no manifest approval')
    if mode == 'accepted' and not rel.get('accepted'):
        bad.append('accepted release was not validated as accepted')
    return bad


def check_public_file(obj, roster=None):
    """Check the content of dashboard/feature-matrix/data/matrix.json.

    It must be the deliberate empty marker or an accepted payload without
    identities. A preview payload is never publishable. Returns a list of problems.
    """
    if isinstance(obj, dict) and obj.get('schema') == EMPTY_SCHEMA:
        if obj != empty_marker():
            return ['empty marker must be exactly %s' % json.dumps(empty_marker())]
        return []
    bad = check_payload(obj)
    if not bad and obj['release']['publication_mode'] != 'accepted':
        bad.append('only an accepted payload may be published; this is %r' % obj['release']['publication_mode'])
    if roster and isinstance(obj, dict):
        bad += leaks(obj, roster)
    return bad
