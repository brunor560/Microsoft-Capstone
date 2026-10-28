"""Manifest approval, cell authorship and independent team-member review.

These records are human decisions. The CLI only accepts roster IDs and never
fills in a person. It cannot authenticate who is typing: provenance comes from
the commit that adds the record.
"""
from . import model
from . import store as st

DISPOSITIONS = ('author_revised', 'reviewer_withdrew', 'escalated')


def _person(store, pid, role):
    people = store.people()
    if pid not in people:
        raise ValueError('%r is not on the roster (assessment/people.json)' % pid)
    if role and role not in people[pid].get('roles', []):
        raise ValueError('%s does not have the %s role' % (people[pid]['name'], role))
    return people[pid]


def approve(store, approver_id):
    _person(store, approver_id, 'approver')
    manifest = store.load('manifest.json')
    if not manifest['profiles']:
        raise ValueError('INPUT_INCOMPLETE: the manifest has no profiles to approve')
    for p in manifest['profiles']:
        if not p.get('confirmed_by'):
            raise ValueError('INPUT_INCOMPLETE: profile %s has no confirmed boundary' % p['id'])
    manifest['approval'] = {
        'approver': approver_id, 'approved_at': st.now(),
        'manifest_version': manifest['manifest_version'],
        'manifest_sha256': st.manifest_hash(manifest),
        'reference': 'Recorded with `assess approve`; provenance is the commit that adds it',
    }
    store.save('manifest.json', manifest)
    store.log('manifest_approved', actor=approver_id,
              manifest_version=manifest['manifest_version'],
              manifest_sha256=manifest['approval']['manifest_sha256'])
    return manifest


def set_author(store, cid, author_id):
    _person(store, author_id, None)
    cells = store.load('cells.json')
    cell = cells['cells'].get(cid)
    if cell is None:
        raise ValueError('no such cell: %s' % cid)
    if cell['assessment_state'] == 'pending':
        raise ValueError('%s is still pending research; there is nothing to take responsibility for' % cid)
    cell['author'] = author_id
    model.touch(cell, 'author_set', author=author_id)
    store.save('cells.json', cells)
    store.log('author_set', actor=author_id, cell_id=cid)


def record(store, cid, reviewer_id, decision, note, disposition=None):
    _person(store, reviewer_id, 'reviewer')
    cells = store.load('cells.json')
    cell = cells['cells'].get(cid)
    if cell is None:
        raise ValueError('no such cell: %s' % cid)
    if cell['assessment_state'] == 'pending':
        raise ValueError('%s is still pending research; nothing to review' % cid)
    if not cell.get('author'):
        raise ValueError('%s has no named human author; run `assess author` first' % cid)
    if cell['author'] == reviewer_id:
        raise ValueError('REVIEW_MISSING: self-review is not independent (%s authored %s)' % (reviewer_id, cid))
    if decision not in ('agree', 'disagree'):
        raise ValueError('decision must be agree or disagree')
    if decision == 'disagree' and disposition is not None and disposition not in DISPOSITIONS:
        raise ValueError('disposition must be one of: ' + ', '.join(DISPOSITIONS))
    if not note or not note.strip():
        raise ValueError('a review note is required')
    reviews = store.load('reviews.json')
    rec = {'cell_id': cid, 'reviewer': reviewer_id, 'decision': decision, 'note': note.strip(),
           'disposition': disposition if decision == 'disagree' else None,
           'cell_sha256': st.cell_hash(cell), 'reviewed_at': st.now()}
    reviews['reviews'].append(rec)
    store.save('reviews.json', reviews)
    if decision == 'agree':
        cell['assessment_state'] = 'reviewed'
    elif cell['assessment_state'] == 'reviewed':
        cell['assessment_state'] = 'challenged'  # a disagreement reopens the cell
    model.touch(cell, 'review_recorded', reviewer=reviewer_id, decision=decision)
    store.save('cells.json', cells)
    store.log('review_recorded', actor=reviewer_id, cell_id=cid, decision=decision,
              disposition=rec['disposition'])
    return rec


def current(store, cells):
    """Latest review per cell; stale when the cell's substance changed afterwards."""
    latest = {}
    for r in store.load('reviews.json')['reviews']:
        latest[r['cell_id']] = r
    return {cid: dict(r, stale=(cid not in cells or st.cell_hash(cells[cid]) != r['cell_sha256']))
            for cid, r in latest.items()}
