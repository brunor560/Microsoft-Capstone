"""Individual validation checks used by validate.run (cell checks in cellchecks.py)."""
from . import model
from . import review
from . import store as st
from .cellchecks import cell  # noqa: F401  (re-exported for validate.run)


class Context:
    def __init__(self, store):
        self.store = store
        self.cat = store.catalog()
        self.statuses = {s['name'] for s in self.cat['statuses']}
        self.feats = [f['id'] for f in self.cat['features']]
        self.manifest = store.load('manifest.json')
        self.cells = store.load('cells.json')['cells']
        self.entries = store.load('sources.json')['entries']
        self.people = store.people()
        self.ids = [p.get('id') for p in self.manifest.get('profiles', [])]
        self.reviews = review.current(store, self.cells)


def catalog(ctx, add):
    if len(ctx.feats) != 18 or len(ctx.cat['categories']) != 7 or len(ctx.statuses) != 5:
        add('CATALOG_INVALID', 'block', 'Catalog must have 18 features, 7 categories and 5 statuses')


def manifest(ctx, add):
    profiles, ids, people = ctx.manifest.get('profiles', []), ctx.ids, ctx.people
    if not profiles:
        add('INPUT_INCOMPLETE', 'block', 'Manifest lists no profiles (P = 0); an empty manifest cannot pass')
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        add('PROFILE_INVALID', 'block', 'Duplicate profile IDs: %s' % dups)
    for p in profiles:
        where = 'manifest:%s' % p.get('id')
        missing = [k for k in model.REQUIRED_PROFILE_FIELDS if p.get(k) in (None, '', [])]
        if missing:
            add('PROFILE_INVALID', 'block', 'Missing required profile fields: %s' % ', '.join(missing), where)
        if p.get('confirmed_by') and p['confirmed_by'] not in people:
            add('PROFILE_INVALID', 'block', 'Boundary confirmed by someone not on the roster', where)
        if not p.get('confirmed_by'):
            add('BOUNDARY_UNCONFIRMED', 'block', 'Profile boundary is only proposed; confirm it with `start`', where)
        v = p.get('version') or {}
        if not v.get('value') and not v.get('documentation_note'):
            add('PROFILE_INVALID', 'block', 'No tool version and no unversioned explanation', where)
    appr = ctx.manifest.get('approval')
    if not appr:
        add('APPROVAL_MISSING', 'block', 'Manifest version %s is not approved' % ctx.manifest.get('manifest_version'))
        return
    person = people.get(appr.get('approver'))
    if not person or 'approver' not in person.get('roles', []):
        add('APPROVAL_INVALID', 'block', 'Approver is not a roster member with the approver role')
    if appr.get('manifest_sha256') != st.manifest_hash(ctx.manifest):
        add('APPROVAL_STALE', 'block', 'Manifest changed after approval (hash mismatch); re-approve')


def coverage(ctx, add):
    expected = {model.cell_id(f, p) for p in ctx.ids for f in ctx.feats}
    present = set(ctx.cells)
    for cid in sorted(expected - present):
        add('CELL_MISSING', 'block', 'No cell for this feature/profile pair', cid)
    for cid in sorted(present - expected):
        add('CELL_UNEXPECTED', 'block', 'Cell does not match an approved feature/profile pair', cid)
    for cid, c in ctx.cells.items():
        if cid != model.cell_id(c.get('feature_id'), c.get('profile_id')):
            add('CELL_INVALID', 'block', 'Cell key does not match its feature/profile fields', cid)
    return expected
