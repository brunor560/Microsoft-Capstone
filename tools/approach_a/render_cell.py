"""Markdown for one detailed cell record."""
from .render_cells import BANNER, esc


def cell_md(feature, profile, cell, sources, people, rv):
    def name(pid):
        return people.get(pid, {}).get('name', pid) if pid else 'none'

    pend = cell['assessment_state'] == 'pending'
    out = ['# MATRIX:%s %s / %s\n' % (feature['id'], feature['name'], profile['id']), BANNER,
           '**Capability:** %s\n' % feature['capability'], '**Examine:** %s\n' % feature['examine'],
           '| Field | Value |', '| --- | --- |']
    rows = [('Status', 'Pending research (placeholder; not a finding)' if pend else cell['status']),
            ('Assessment state', cell['assessment_state']),
            ('Evidence basis', cell.get('evidence_basis')),
            ('Supported scope', cell.get('supported_scope')),
            ('Unsupported scope', '; '.join(cell.get('unsupported_scope') or []) or 'none recorded'),
            ('Unestablished scope', '; '.join(cell.get('unestablished_scope') or []) or 'none recorded'),
            ('Gap or conflict reason', cell.get('gap_reason') or '-'),
            ('Required setup', cell.get('required_setup')),
            ('Activation', cell.get('activation_state')),
            ('Control mechanism', cell.get('control_mechanism')),
            ('Constraints and uncertainties', '; '.join(cell.get('constraints') or []) or 'none recorded'),
            ('Limitations', cell.get('limitations')),
            ('Drafted by', cell.get('drafted_by') or '-'),
            ('Author (responsible person)', name(cell.get('author'))),
            ('Assessment date', cell.get('assessment_date') or '-')]
    out += ['| %s | %s |' % (k, esc(v)) for k, v in rows]
    out.append('\n## Evidence\n')
    if not cell.get('evidence_refs'):
        out.append('No evidence recorded.')
    for r in cell.get('evidence_refs', []):
        e = sources['entries'].get(r)
        if not e:
            out.append('- MATRIX:%s (missing from the source index)' % r)
            continue
        out.append('- **MATRIX:%s** [%s](%s), section "%s" (surface: %s), accessed %s, check: %s. Quote: "%s"' % (
            r, e['page_title'], e['url'], e['section'], e['surface'], e['access_date'], e['check'], e['quote']))
    if cell.get('rejected_citations'):
        out.append('\nCitations rejected by verification: ' + '; '.join(cell['rejected_citations']))
    ch = cell.get('challenge')
    out.append('\n## Evidence-challenge pass (automated; not a team review)\n')
    if not ch:
        out.append('Not run.')
    else:
        out += ['- [%s] %s: %s%s' % (f['severity'], f['type'], f['detail'],
                                     ' (MATRIX:%s)' % f['ref'] if f.get('ref') else '')
                for f in ch['flags']] or ['- No flags.']
    out.append('\n## Independent review\n')
    if not rv:
        out.append('No review recorded. Acceptance requires a roster member other than the author.')
    else:
        out.append('%s by %s at %s%s. Note: %s%s' % (
            rv['decision'], name(rv['reviewer']), rv['reviewed_at'],
            '; disposition: %s' % rv['disposition'] if rv.get('disposition') else '', rv['note'],
            ' **(stale: the cell changed after this review)**' if rv['stale'] else ''))
    return '\n'.join(out) + '\n'
