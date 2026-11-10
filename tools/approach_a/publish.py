"""Reviewed projection of the Approach A feature matrix, prepared for the M13 release builder.

Builds one versioned, allowlisted JSON payload from a frozen snapshot of the
assessment dataset (DDD I12 CellExport: cells pass as reviewed data, never
regraded). Publication itself is handled by the existing GitHub Pages workflow,
which uploads dashboard/. This module only prepares what may be placed there.

Two modes:

  accepted  the complete selected manifest must pass structural validation
            (including independent review of every cell), otherwise nothing is
            written. Output goes under dashboard/feature-matrix/data/.
  preview   local draft view. Pending, unreviewed and blocked cells are kept and
            labeled with their workflow state and blocking codes. Output goes
            under assessment/preview/ and is never allowed inside dashboard/,
            because the whole of dashboard/ is the Pages upload root.

The public payload has no names and no roster IDs (see pubcheck.py). Identity
stays in the Approach A dataset and the Git history that recorded it.

The authoritative dataset is read, never modified: validation runs on a scratch
copy, because validate.run writes a report and appends to the work log.
Standard library only.
"""
import json
import os
import shutil
import subprocess
import tempfile

from . import model
from . import pubcheck
from . import review
from . import store as st
from . import validate
from .pubcheck import MODES, SCHEMA  # noqa: F401  (re-exported)

EXPORT_VERSION = '2'
SNAPSHOT_FILES = ('catalog.json', 'manifest.json', 'cells.json', 'sources.json', 'reviews.json', 'people.json')
BOUND_FILES = SNAPSHOT_FILES

DASHBOARD = os.path.join(st.REPO, 'dashboard')
OUT_DIR = os.path.join(DASHBOARD, 'feature-matrix', 'data')
PREVIEW_DIR = os.path.join(st.DEFAULT_ROOT, 'preview')
DEFAULT_OUT = {'accepted': os.path.join(OUT_DIR, 'matrix.json'),
               'preview': os.path.join(PREVIEW_DIR, 'matrix.preview.json')}

# Public field allowlists. Anything not listed here is not exported.
PROFILE_FIELDS = ('id', 'tool', 'tool_key', 'surface', 'surface_label', 'category_tags', 'version', 'modes',
                  'platforms', 'account_and_tier', 'exclusions', 'included_components',
                  'interface_and_execution_location', 'instructions_and_permissions', 'model_support',
                  'documentation_base', 'source_access_date', 'boundary_state')
CELL_FIELDS = ('feature_id', 'profile_id', 'status', 'assessment_state', 'supported_scope', 'unsupported_scope',
               'unestablished_scope', 'required_setup', 'activation_state', 'evidence_basis', 'evidence_refs',
               'gap_reason', 'control_mechanism', 'constraints', 'limitations', 'assessment_date')
EVIDENCE_FIELDS = ('id', 'publisher', 'page_title', 'url', 'section', 'surface', 'quote', 'claim_summary',
                   'access_date', 'page_sha256', 'version_or_update')

LIMITATIONS = [
    'Documentation-only assessment of official public documentation; no tool was installed, run or tested.',
    'Each finding describes documented support within the stated profile boundary, version and access date.',
    '"Not established from documentation" means the reviewed sources are silent, ambiguous or conflicting. '
    'It is not a score of zero and not evidence of absence.',
    '"Quotation matched to source" means the quoted text was found in the cited section. '
    'It does not by itself verify the capability.',
    'Statuses describe different dimensions of support and are not an ordinal score. '
    'No capability total or ranking is produced.',
    'Documentary findings are separate from benchmark results and are never combined with them.',
]


class PublishError(ValueError):
    pass


def _inside(path, base):
    path, base = os.path.realpath(path), os.path.realpath(base)
    return path == base or path.startswith(base + os.sep)


def _git(*args):
    try:
        r = subprocess.run(('git',) + args, cwd=st.REPO, capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def resolve_out(mode, out=None, allow_other_out=False):
    """Choose and police the output path. Drafts never go near the Pages upload root."""
    path = os.path.abspath(out or DEFAULT_OUT[mode])
    if mode == 'preview' and _inside(path, DASHBOARD):
        raise PublishError('preview output must stay outside dashboard/ (the whole directory is the Pages upload '
                           'root); default: %s' % DEFAULT_OUT['preview'])
    if mode == 'accepted' and not allow_other_out and not _inside(path, OUT_DIR):
        raise PublishError('accepted output belongs under %s (use --allow-other-out for a scratch location)' % OUT_DIR)
    return path


def snapshot(store):
    """Read the dataset once into memory, so every later step sees the same bytes."""
    raw = {}
    for name in SNAPSHOT_FILES:
        p = store.path(name)
        if not os.path.exists(p):
            raise PublishError('missing dataset file: %s' % p)
        with open(p, 'rb') as f:
            raw[name] = f.read()
    return raw


def provenance(raw, dataset_root=None, requested_commit=None):
    """Verify bytes at their actual repository path, not an unrelated clean HEAD.

    Local projections may have unverified provenance. Public writes may not.
    Neither a caller-supplied SHA nor a caller-supplied dirty flag is proof.
    """
    result = {'source_commit': None, 'source_dirty': True, 'source_verified': False,
              'requested_source_commit': requested_commit, 'source_dataset_path': None}
    if dataset_root is None or not _inside(dataset_root, st.REPO):
        return result
    root = os.path.realpath(dataset_root)
    relative = os.path.relpath(root, os.path.realpath(st.REPO)).replace(os.sep, '/')
    result['source_dataset_path'] = relative
    commit = _git('rev-parse', '--verify', '--end-of-options', (requested_commit or 'HEAD') + '^{commit}')
    if not commit:
        return result
    result['source_commit'] = commit
    for name in BOUND_FILES:
        path = os.path.join(root, name)
        if not _inside(path, st.REPO):
            return result
        repo_path = (relative + '/' + name) if relative != '.' else name
        try:
            with open(path, 'rb') as f:
                if f.read() != raw[name]:
                    return result
            for spec in (commit + ':' + repo_path, ':' + repo_path):
                # Binary comparison: JSON whitespace and final newlines count.
                r = subprocess.run(('git', 'show', spec), cwd=st.REPO,
                                   capture_output=True, timeout=20)
                if r.returncode or r.stdout != raw[name]:
                    return result
        except (OSError, subprocess.SubprocessError):
            return result
    result.update(source_dirty=False, source_verified=True)
    return result


def _rejection(report):
    blocking = [i for i in report['issues'] if i['severity'] == 'block']
    lines = ['dataset is not accepted: %d blocking finding(s); nothing was written' % len(blocking)]
    for code, n in sorted(report['counts_by_code'].items()):
        lines.append('  %s x%d' % (code, n))
    lines.append('Use --mode preview for a labeled local draft view.')
    return '\n'.join(lines)


def build(raw, mode='accepted', source_commit=None, source_dirty=None, dataset_root=None):
    """Return the publication payload for a snapshot. Raises PublishError if it cannot be published."""
    if mode not in MODES:
        raise PublishError('mode must be one of: %s' % ', '.join(MODES))
    tmp = tempfile.mkdtemp(prefix='aa-publish-')
    try:
        for name, data in raw.items():
            with open(os.path.join(tmp, name), 'wb') as f:
                f.write(data)
        scratch = st.Store(tmp)
        report = validate.run(scratch)  # writes only into the scratch copy
        if mode == 'accepted' and not report['accepted']:
            raise PublishError(_rejection(report))
        # source_dirty is retained for API compatibility, never trusted as proof.
        origin = provenance(raw, dataset_root, source_commit)
        payload = _project(scratch, raw, report, mode, origin)
        roster = scratch.people()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    problems = pubcheck.check_payload(payload) + pubcheck.leaks(payload, roster)
    if problems:
        raise PublishError('publication payload is invalid:\n  ' + '\n  '.join(problems))
    return payload


def _cell(c, rv, entries, blocking, profile):
    """One public cell. Author/reviewer identity is compared here, then dropped."""
    rec = {k: c.get(k) for k in CELL_FIELDS}
    rec['cell_sha256'] = st.cell_hash(c)
    rec['author'] = {'recorded': True} if c.get('author') else None
    rec['review'] = None if not rv else {
        'decision': rv['decision'], 'disposition': rv.get('disposition'),
        'reviewed_at': rv['reviewed_at'], 'cell_sha256': rv['cell_sha256'], 'stale': rv['stale'],
        'independent': bool(c.get('author')) and rv['reviewer'] != c['author'],
        'binding_version': rv.get('binding_version'),
        'evidence_sha256': rv.get('evidence_sha256'), 'profile_sha256': rv.get('profile_sha256')}
    rec['evidence_sha256'] = st.sha256({r: entries.get(r) for r in c.get('evidence_refs', [])})
    rec['profile_sha256'] = st.sha256(profile)
    rec['blocking_codes'] = blocking
    return rec


def _cells(store, cat, manifest, report, mode):
    cells, entries = store.load('cells.json')['cells'], store.load('sources.json')['entries']
    reviews = review.current(store, cells)
    blocking = {}
    for i in report['issues']:
        if i['severity'] == 'block' and i.get('where'):
            blocking.setdefault(i['where'], set()).add(i['code'])
    out, used = [], []
    for p in manifest.get('profiles', []):
        for f in cat['features']:
            cid = model.cell_id(f['id'], p['id'])
            c = cells.get(cid)
            if c is None:
                if mode == 'accepted':
                    raise PublishError('missing cell %s' % cid)
                out.append({'feature_id': f['id'], 'profile_id': p['id'], 'status': None,
                            'assessment_state': 'missing', 'evidence_refs': [], 'author': None,
                            'review': None, 'blocking_codes': ['CELL_MISSING']})
                continue
            out.append(_cell(c, reviews.get(cid), entries, sorted(blocking.get(cid, ())), p))
            used += [r for r in c.get('evidence_refs', []) if r not in used]
    if mode == 'accepted':
        for rec in out:
            rec.pop('blocking_codes', None)
    evidence = []
    for r in sorted(used):
        e = entries.get(r)
        if e:
            item = {k: e.get(k) for k in EVIDENCE_FIELDS}
            item['quotation_matched'] = e.get('check') == 'verified'
            evidence.append(item)
    return out, evidence



def _project(store, raw, report, mode, origin):
    cat, manifest = store.catalog(), store.load('manifest.json')
    cells, evidence = _cells(store, cat, manifest, report, mode)
    approval = manifest.get('approval')
    hashes = {n: st.sha256(raw[n]) for n in BOUND_FILES}
    key = st.sha256({'files': hashes, 'export_version': EXPORT_VERSION, 'mode': mode})
    return {
        'schema': SCHEMA,
        'release': {
            'release_id': 'mx-' + key[:12], 'publication_mode': mode,
            'accepted': bool(report['accepted']), 'generated_at': st.now(),
            'export_version': EXPORT_VERSION, **origin, 'source_file_sha256': hashes,
            'manifest_version': manifest.get('manifest_version'),
            'manifest_sha256': st.manifest_hash(manifest),
            'approval': None if not approval else {
                'approved_at': approval.get('approved_at'),
                'manifest_sha256': approval.get('manifest_sha256')},
            'validation': {'blocking_count': report['blocking_count'],
                           'counts_by_code': report['counts_by_code'],
                           'cell_states': report['cell_states']},
        },
        'catalog': {
            'features': [{k: f.get(k) for k in ('id', 'area', 'name', 'capability', 'examine')}
                         for f in cat['features']],
            'categories': [{k: c.get(k) for k in ('id', 'name', 'description', 'example')}
                           for c in cat['categories']],
            'statuses': [{'name': s['name'], 'meaning': s['meaning']} for s in cat['statuses']],
            'activation_states': cat['activation_state'], 'control_mechanisms': cat['control_mechanism'],
            'evidence_bases': cat['evidence_basis'], 'assessment_states': cat['assessment_states'],
        },
        'profiles': [{k: p.get(k) for k in PROFILE_FIELDS if k in p} for p in manifest.get('profiles', [])],
        'cells': cells,
        'evidence': evidence,
        'limitations': LIMITATIONS,
    }


def write(payload, out):
    """Write to a temp file, re-check what was written, then promote it atomically."""
    out = os.path.abspath(out)
    if _inside(out, DASHBOARD):
        rel = payload['release']
        if (rel.get('publication_mode') != 'accepted' or not rel.get('source_verified') or
                rel.get('source_dirty') is not False or not rel.get('source_commit') or
                rel.get('source_dataset_path') is None):
            raise PublishError('Public export requires a matching committed dataset snapshot at its repository path; '
                               'commit the reviewed inputs first, or use --allow-other-out --out outside dashboard/ for local inspection')
        dataset_path = os.path.join(st.REPO, rel.get('source_dataset_path') or '')
        raw = snapshot(st.Store(dataset_path))
        if ({n: st.sha256(raw[n]) for n in BOUND_FILES} != rel.get('source_file_sha256') or
                not provenance(raw, dataset_path, rel.get('source_commit'))['source_verified']):
            raise PublishError('Public export provenance no longer matches the committed inputs; nothing written')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(out), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write('\n')
        with open(tmp, encoding='utf-8') as f:
            check = pubcheck.check_public_file if _inside(out, DASHBOARD) else pubcheck.check_payload
            problems = check(json.load(f))
        if problems:
            raise PublishError('written payload failed validation:\n  ' + '\n  '.join(problems))
        os.replace(tmp, out)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return out


def run(store, args):
    """CLI handler: export-publication."""
    mode = args.mode
    out = resolve_out(mode, args.out, args.allow_other_out)
    raw = snapshot(store)
    payload = build(raw, mode, args.source_commit, dataset_root=store.root)
    if _inside(out, DASHBOARD) and not provenance(
            raw, store.root, payload['release']['source_commit'])['source_verified']:
        raise PublishError('Public export requires all reviewed inputs committed at the selected dataset path '
                           'and matching the claimed commit; nothing written. Use --allow-other-out --out '
                           'outside dashboard/ for local inspection.')
    write(payload, out)
    rel = payload['release']
    print('%s payload %s written to %s' % (mode, rel['release_id'], out))
    print('  profiles: %d, cells: %d, evidence: %d, blocking findings in snapshot: %d'
          % (len(payload['profiles']), len(payload['cells']), len(payload['evidence']),
             rel['validation']['blocking_count']))
    if mode == 'preview':
        print('  PREVIEW ONLY: draft findings are not accepted results. Do not publish this file.')
    return 0

