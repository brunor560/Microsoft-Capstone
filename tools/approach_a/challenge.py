"""Evidence-challenge pass: automated scrutiny of drafted cells.

Flags (it does not decide):
  unsupported_claim     affirmative or absence status without a verified reference
  surface_transfer      a reference whose section belongs to another product surface,
                        or a page that does not list the profile's surface
  page_changed          the cited page changed after the evidence was recorded
  source_conflict       the cell itself records a documentation conflict
  scope_gap_basis       Not established cell without a real gap reason or gap basis
This pass is not the independent team-member review required by SRS Spec 5.3.
"""
from . import model
from . import store as st

AFFIRMATIVE = ('Built in', 'Configuration or extension required',
               'Custom implementation required', 'Unavailable')


def challenge_cell(cell, profile, index_data):
    flags = []
    surface = profile['surface']
    entries = index_data['entries']
    verified = [entries[r] for r in cell.get('evidence_refs', []) if r in entries]
    if cell['status'] in AFFIRMATIVE and not any(e.get('check') == 'verified' for e in verified):
        flags.append({'type': 'unsupported_claim', 'severity': 'block',
                      'detail': 'Status %r has no verified official reference' % cell['status']})
    for e in verified:
        s = e.get('surface') or 'unspecified'
        if s.startswith('page:'):
            listed = s[5:].split('+')
            if surface not in listed:
                flags.append({'type': 'surface_transfer', 'severity': 'block', 'ref': e['id'],
                              'detail': 'Page lists %s; profile surface is %s' % (s[5:], surface)})
            elif len(listed) > 1:
                flags.append({'type': 'shared_page', 'severity': 'note', 'ref': e['id'],
                              'detail': 'Section is not surface-specific; page applies to %s' % s[5:]})
        elif s == 'unspecified':
            flags.append({'type': 'surface_unconfirmed', 'severity': 'warn', 'ref': e['id'],
                          'detail': 'Neither the section nor the page names a product surface'})
        elif s != surface:
            flags.append({'type': 'surface_transfer', 'severity': 'block', 'ref': e['id'],
                          'detail': 'Cited section belongs to %s; profile surface is %s' % (s, surface)})
        page = index_data['pages'].get(e['url'], {})
        if page.get('sha256') and page['sha256'] != e.get('page_sha256'):
            flags.append({'type': 'page_changed', 'severity': 'warn', 'ref': e['id'],
                          'detail': 'Page content changed after this evidence was recorded'})
        if 'changelog' in e['url']:
            flags.append({'type': 'release_note_source', 'severity': 'note', 'ref': e['id'],
                          'detail': 'Release notes describe a change; confirm in the main documentation'})
    if cell.get('evidence_basis') == 'documentation_conflict' or any(
            'conflict' in c.lower() for c in cell.get('constraints', [])):
        flags.append({'type': 'source_conflict', 'severity': 'warn',
                      'detail': 'Cell records conflicting documentation; reviewer must confirm disposition'})
    if cell['status'] == model.NE:
        gr = (cell.get('gap_reason') or '').strip().lower()
        if not gr or gr.startswith('assessment pending'):
            flags.append({'type': 'scope_gap_basis', 'severity': 'block',
                          'detail': 'Not established needs a specific gap or conflict reason'})
    if cell.get('rejected_citations'):
        flags.append({'type': 'rejected_citation', 'severity': 'warn',
                      'detail': '%d brief citation(s) failed verification' % len(cell['rejected_citations'])})
    return flags


def run(store, progress, operator):
    manifest = store.load('manifest.json')
    profiles = {p['id']: p for p in manifest['profiles']}
    data = store.load('cells.json')
    index_data = store.load('sources.json')
    todo = [c for c in data['cells'].values()
            if c['profile_id'] in profiles and c['assessment_state'] != 'pending']
    summary = {'checked': 0, 'blocking': 0, 'warnings': 0, 'by_type': {}}
    for n, cell in enumerate(sorted(todo, key=lambda c: (c['profile_id'], c['feature_id'])), 1):
        flags = challenge_cell(cell, profiles[cell['profile_id']], index_data)
        cell['challenge'] = {'at': st.now(), 'by': 'evidence-challenge pass (automated)',
                             'flags': flags, 'note': 'Automated check; not a team-member review'}
        if cell['assessment_state'] == 'drafted':
            cell['assessment_state'] = 'challenged'
        blocking = sum(f['severity'] == 'block' for f in flags)
        warns = sum(f['severity'] == 'warn' for f in flags)
        summary['checked'] += 1
        summary['blocking'] += blocking
        summary['warnings'] += warns
        for f in flags:
            summary['by_type'][f['type']] = summary['by_type'].get(f['type'], 0) + 1
        progress('challenge', n, len(todo), '%s %s  %s' % (
            cell['profile_id'], cell['feature_id'],
            ', '.join(sorted({f['type'] for f in flags if f['severity'] != 'note'})) or 'no blocking or warning flags'))
    store.save('cells.json', data)
    store.log('challenge_pass', actor=operator, **summary)
    return summary
