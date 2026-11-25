"""Read-only, offline review packets. No decisions, fetches or generated data writes."""
from . import challenge, fetch, pages, review, sources, store as st, validate
from .render_cell import cell_md


def context(store, entry):
    text, _ = fetch.PageCache(store).get(sources.page_key(entry['url']))
    if entry.get('page_html_sha256'):
        from .refresh import historical
        archived = historical(store, entry)
        if archived is not None:
            text = archived['text']
    if text is None:
        return 'Context unavailable locally; open the source link and inspect the cited section.'
    if st.sha256(text.encode('utf-8')) != entry.get('page_sha256'):
        return 'Cached page differs from cited snapshot; open the source link and resolve the version.'
    # Show the entire cited section, including its nested headings, without
    # manufacturing surrounding prose when an exact snapshot is unavailable.
    path = entry['section'].split(' > ')
    for section in pages.sections(text):
        if section['path'] == path:
            return text[section['body_start']:section['end']].strip()
    return 'Cited section unavailable in cached snapshot; inspect the source link.'


def build(store, pid):
    manifest = store.load('manifest.json')
    profile = next((p for p in manifest['profiles'] if p['id'] == pid), None)
    if profile is None:
        raise ValueError('Unknown profile: %s' % pid)
    cells = store.load('cells.json')['cells']
    index = store.load('sources.json')
    people = store.people()
    current = review.current(store, cells)
    findings = [c for c in cells.values() if c['profile_id'] == pid]
    def concerns(c):
        flags = challenge.challenge_cell(c, profile, index) + (c.get('challenge') or {}).get('flags', [])
        reasons = []
        if c.get('evidence_basis') == 'documentation_conflict' or any(
                f['type'] in ('surface_transfer', 'source_conflict') for f in flags):
            reasons.append('surface/source conflict')
        if c.get('evidence_basis') == 'documented_absence' or c['status'] == 'Unavailable' or c.get('unsupported_scope'):
            reasons.append('explicit absence claim')
        if c.get('unestablished_scope') or c.get('gap_reason') or any(
                f['type'] == 'surface_unconfirmed' for f in flags):
            reasons.append('scope ambiguity')
        return reasons
    priorities = {'surface/source conflict': 0, 'explicit absence claim': 1, 'scope ambiguity': 2}
    findings.sort(key=lambda c: (min((priorities[r] for r in concerns(c)), default=3), c['feature_id']))
    out = ['# Review packet: %s' % pid, 'Read-only draft review aid; no human decisions recorded.',
           'Dataset: %s' % store.root, 'Manifest version: %s; SHA-256: %s' % (
               manifest['manifest_version'], st.manifest_hash(manifest))]
    for field in ('tool', 'surface', 'surface_label', 'account_and_tier', 'platforms', 'modes',
                  'exclusions', 'version', 'boundary_state', 'confirmed_by'):
        out.append('%s: %s' % (field, profile.get(field, 'not recorded')))
    out += ['', '## Review first: conflicts, explicit absence and scope ambiguities']
    out += ['- %s: %s' % (c['feature_id'], ', '.join(concerns(c))) for c in findings if concerns(c)] or ['None flagged.']
    issues = [i for i in validate.inspect(store)['issues'] if
              not i.get('where') or i['where'] == 'manifest:' + pid or i['where'].startswith(pid + '/')]
    out += ['', '## Current profile, cell and manifest blockers']
    out += ['- %s %s: %s' % (i['where'], i['code'], i['message']) for i in issues] or ['None.']
    grouped = {}
    for c in findings:
        for ref in c.get('evidence_refs', []):
            e = index['entries'].get(ref)
            key = (e['url'], e['section'], e['quote']) if e else ('missing', ref, '')
            group = grouped.setdefault(key, {'entry': e, 'refs': set(), 'cells': set()})
            group['refs'].add(ref)
            group['cells'].add(c['feature_id'])
    out += ['', '## Shared passages and source context']
    for group in sorted(grouped.values(), key=lambda g: (-len(g['cells']), sorted(g['refs']))):
        e = group['entry']
        out += ['', '### %s — used by %s' % (', '.join(sorted(group['refs'])), ', '.join(sorted(group['cells'])))]
        if e is None:
            out.append('Missing evidence entry.')
            continue
        out += ['[%s](%s)' % (e['page_title'], e['url']),
                'Section: %s; surface: %s; accessed: %s; quote check: %s' % (
                    e['section'], e.get('surface'), e.get('access_date'), e.get('check')),
                'Claim summary (assessor): %s' % e.get('claim_summary', 'not recorded'),
                'Quoted passage: %s' % e['quote'], 'Source context (cached cited section):', context(store, e)]
    features = {f['id']: f for f in store.catalog()['features']}
    out += ['', '## Findings (priority items first)']
    for c in findings:
        detail = cell_md(features[c['feature_id']], profile, c, index, people, current.get(
            '%s/%s' % (pid, c['feature_id'])))
        # Passages above are shared; keep each finding linked by stable evidence IDs.
        start = detail.index('\n## Evidence\n')
        end = detail.index('\n## Evidence-challenge pass', start)
        detail = detail[:start] + '\nEvidence: ' + ', '.join(c.get('evidence_refs', [])) + '\n' + detail[end:]
        out += [detail, 'Current challenge flags (recomputed, not saved): %s' % challenge.challenge_cell(c, profile, index)]
        rv = current.get('%s/%s' % (pid, c['feature_id']))
        out.append('Current cell SHA-256: %s; recorded review SHA-256: %s' % (
            st.cell_hash(c), rv['cell_sha256'] if rv else 'none'))
    return '\n\n'.join(out) + '\n'


def run(store, args):
    profiles = args.profile or [p['id'] for p in store.load('manifest.json')['profiles']]
    for pid in profiles:
        print(build(store, pid))
    return 0
