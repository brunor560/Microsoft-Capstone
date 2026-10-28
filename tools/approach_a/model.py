"""Manifest profiles and cell records."""
from . import store as st

NE = 'Not established from documentation'
REQUIRED_PROFILE_FIELDS = ('id', 'tool', 'surface', 'surface_label', 'category_tags',
                           'version', 'modes', 'platforms', 'account_and_tier',
                           'exclusions', 'source_access_date')


def cell_id(feature_id, profile_id):
    return '%s/%s' % (profile_id, feature_id)


def pending_cell(feature_id, profile_id):
    """Initial cell. Its NE status is a placeholder, not a finding.

    assessment_state 'pending' keeps it apart from a completed "Not
    established from documentation" finding; the validator never accepts a
    pending cell, and "Assessment pending" is not accepted as a gap reason.
    """
    return {
        'feature_id': feature_id, 'profile_id': profile_id,
        'status': NE, 'assessment_state': 'pending',
        'supported_scope': 'Not established', 'unsupported_scope': [],
        'unestablished_scope': [], 'required_setup': 'Not established',
        'activation_state': 'not established', 'evidence_basis': None,
        'evidence_refs': [], 'gap_reason': None,
        'control_mechanism': 'not established', 'constraints': [],
        'limitations': 'Documentation-only assessment; runtime behavior is not evaluated',
        'author': None, 'drafted_by': None, 'assessment_date': None,
        'challenge': None, 'history': [],
    }


def profile_from_candidate(cand, surface_key, overrides=None):
    s = cand['surfaces'][surface_key]
    p = {
        'id': s['profile_id'], 'tool': cand['tool'], 'tool_key': cand['tool_key'],
        'surface': surface_key, 'surface_label': s['label'],
        'category_tags': s['category_tags'], 'version': s['version'],
        'modes': s['modes'], 'platforms': s['platforms'],
        'account_and_tier': s['account_and_tier'], 'exclusions': s['exclusions'],
        'included_components': s['included_components'],
        'interface_and_execution_location': s['interface_and_execution_location'],
        'instructions_and_permissions': s['instructions_and_permissions'],
        'model_support': s['model_support'],
        'documentation_base': cand['docs']['base_url'],
        'source_access_date': None, 'confirmed_by': None, 'confirmed_at': None,
    }
    p.update(overrides or {})
    return p


def add_profile(store, profile, actor):
    """Add a confirmed profile: bump the manifest version, clear approval, seed 18 pending cells."""
    manifest = store.load('manifest.json')
    if not profile.get('id') or not profile.get('tool'):
        raise ValueError('PROFILE_INVALID: unnamed profile')
    if any(p['id'] == profile['id'] for p in manifest['profiles']):
        raise ValueError('PROFILE_INVALID: duplicate profile id %s' % profile['id'])
    manifest['profiles'].append(profile)
    manifest['manifest_version'] = int(manifest.get('manifest_version') or 0) + 1
    had_approval = manifest.get('approval') is not None
    manifest['approval'] = None
    store.save('manifest.json', manifest)
    cells = store.load('cells.json')
    for f in store.catalog()['features']:
        cells['cells'].setdefault(cell_id(f['id'], profile['id']), pending_cell(f['id'], profile['id']))
    store.save('cells.json', cells)
    store.log('profile_confirmed', actor=actor, profile_id=profile['id'],
              manifest_version=manifest['manifest_version'],
              approval_cleared=had_approval, cells_seeded=len(store.catalog()['features']))
    return manifest


def confirm_profile(store, profile, actor):
    """Replace a proposed (rehearsal) profile with the confirmed boundary.

    Bumps the manifest version and clears approval. Rehearsal drafts are kept
    but lose any author, so a person must take responsibility for them again.
    """
    manifest = store.load('manifest.json')
    idx = next(i for i, p in enumerate(manifest['profiles']) if p['id'] == profile['id'])
    manifest['profiles'][idx] = profile
    manifest['manifest_version'] = int(manifest.get('manifest_version') or 0) + 1
    manifest['approval'] = None
    store.save('manifest.json', manifest)
    data = store.load('cells.json')
    for c in data['cells'].values():
        if c['profile_id'] == profile['id'] and c['assessment_state'] != 'pending':
            c['author'] = None
            touch(c, 'boundary_confirmed', by=actor, note='rehearsal draft carried into the confirmed boundary')
    store.save('cells.json', data)
    store.log('profile_confirmed', actor=actor, profile_id=profile['id'],
              manifest_version=manifest['manifest_version'], replaced='proposed rehearsal boundary')
    return manifest


def profile_ids(manifest):
    return [p['id'] for p in manifest.get('profiles', [])]


def counts(cells, profile_id=None):
    out = {'pending': 0, 'drafted': 0, 'challenged': 0, 'reviewed': 0}
    for c in cells.values():
        if profile_id and c['profile_id'] != profile_id:
            continue
        out[c['assessment_state']] = out.get(c['assessment_state'], 0) + 1
    return out


def touch(cell, event, **details):
    entry = {'at': st.now(), 'event': event}
    entry.update(details)
    cell.setdefault('history', []).append(entry)
