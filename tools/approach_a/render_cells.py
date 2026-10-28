"""Markdown for the 18 x P matrix, cell records, reviews and the validation report."""
from . import model

BANNER = ('> Documentation-only assessment (SRS Requirement 5). Statuses describe what official '
          'documentation says; they are not measured effectiveness, scores or rankings.\n\n')
SHORT = {'Built in': 'Built in', 'Configuration or extension required': 'Config/extension',
         'Custom implementation required': 'Custom impl.', 'Unavailable': 'Unavailable',
         model.NE: 'Not established'}


def esc(s):
    return str(s if s is not None else '').replace('|', '\\|').replace('\n', ' ')


def label(cell, rv):
    if cell['assessment_state'] == 'pending':
        return 'Pending research'
    s = SHORT.get(cell['status'], cell['status'])
    if rv and not rv['stale'] and rv['decision'] == 'agree':
        return s + ' (reviewed)'
    return s + ' (unreviewed draft)'


def matrix_md(cat, manifest, cells, current):
    ids = [p['id'] for p in manifest['profiles']]
    out = ['# Approach A feature matrix (18 x P)\n', BANNER,
           'P = %d (%s). One cell per feature/profile pair. "Pending research" is not a finding; '
           '"Not established" is a completed finding that the documentation does not establish support or absence '
           '(never a zero). Drafts are agent-assisted until a named author and an independent reviewer sign off.\n' % (
               len(ids), ', '.join(ids) or 'no profiles'),
           '| Feature | Name | ' + ' | '.join(ids) + ' |',
           '| --- | --- |' + ' --- |' * len(ids)]
    for f in cat['features']:
        row = ['MATRIX:%s' % f['id'], f['name']]
        for pid in ids:
            cid = model.cell_id(f['id'], pid)
            row.append('[%s](cells/%s/%s.md)' % (label(cells[cid], current.get(cid)), pid, f['id'])
                       if cid in cells else 'MISSING')
        out.append('| ' + ' | '.join(row) + ' |')
    out += ['', 'Status meanings (matrix specification):', '']
    out += ['- **%s**: %s' % (s['name'], s['meaning']) for s in cat['statuses']]
    return '\n'.join(out) + '\n'


def reviews_md(reviews, cells, current, people):
    name = lambda pid: people.get(pid, {}).get('name', pid or '-')
    out = ['# Review and disagreement records\n',
           'Independent team-member review (SRS Spec 5.3). The automated evidence-challenge pass is not a review.\n',
           '| Cell | Author | Reviewer | Decision | Disposition | State | Reviewed at | Note |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in reviews:
        cur = current.get(r['cell_id'])
        state = ('stale' if cur['stale'] else 'current') if cur and cur['reviewed_at'] == r['reviewed_at'] else 'superseded'
        out.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['cell_id'], name(cells.get(r['cell_id'], {}).get('author')), name(r['reviewer']),
            r['decision'], r.get('disposition') or '-', state, r['reviewed_at'], esc(r['note'])))
    if not reviews:
        out.append('| (none recorded) | | | | | | | |')
    return '\n'.join(out) + '\n'


def validation_md(rep):
    out = ['# Validation report\n', '**Result: %s**\n' % rep['result'],
           'Generated %s. Manifest version %s, P = %d, expected cells %d, present %d. Cell states: %s.\n' % (
               rep['generated_at'], rep['manifest_version'], rep['P'], rep['expected_cells'], rep['present_cells'],
               ', '.join('%s %d' % kv for kv in rep['cell_states'].items())),
           '## Limits\n'] + ['- ' + x for x in rep['limits']]
    out += ['\n## Issues by code\n', '| Code | Count |', '| --- | --- |']
    out += ['| %s | %d |' % kv for kv in rep['counts_by_code'].items()] or ['| none | 0 |']
    out += ['\n## Issues\n', '| Code | Where | Message |', '| --- | --- | --- |']
    out += ['| %s | %s | %s |' % (i['code'], i['where'] or '-', esc(i['message'])) for i in rep['issues']]
    return '\n'.join(out) + '\n'
