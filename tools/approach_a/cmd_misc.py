"""`status` and `show` (read-only views), and the shared validation printout."""
from . import model
from . import review
from . import ui


def print_validation(rep, brief=False):
    (ui.ok if rep['accepted'] else ui.fail)('%s  (P = %d, %d of %d cells present; states: %s)' % (
        rep['result'], rep['P'], rep['present_cells'], rep['expected_cells'],
        ', '.join('%s %d' % kv for kv in rep['cell_states'].items())))
    if rep['counts_by_code']:
        ui.table(sorted(rep['counts_by_code'].items(), key=lambda kv: -kv[1]), ['blocking code', 'count'])
    if not brief:
        for i in rep['issues'][:40]:
            print('  %-22s %-24s %s' % (i['code'], i['where'] or '-', i['message']))
        if len(rep['issues']) > 40:
            print('  ... %d more in validation_report.json' % (len(rep['issues']) - 40))
    print('  Limits: ' + ' '.join(rep['limits'][:2]))


def status(store, args):
    manifest = store.load('manifest.json')
    cells = store.load('cells.json')['cells']
    srcs = store.load('sources.json')
    cur = review.current(store, cells)
    a = manifest.get('approval')
    ui.heading('Approach A dataset: %s' % store.root)
    print('  Manifest version %s, P = %d, expected cells %d, approval: %s' % (
        manifest.get('manifest_version'), len(manifest['profiles']), 18 * len(manifest['profiles']),
        'approved by %s' % a['approver'] if a else 'NOT APPROVED'))
    print('  Source index: %d pages, %d evidence entries' % (len(srcs['pages']), len(srcs['entries'])))
    rows = []
    for p in manifest['profiles']:
        k = model.counts(cells, p['id'])
        mine = [c for cid, c in cells.items() if c['profile_id'] == p['id']]
        reviewed = sum(1 for c in mine if cur.get(model.cell_id(c['feature_id'], p['id']), {}).get('decision') == 'agree'
                       and not cur[model.cell_id(c['feature_id'], p['id'])]['stale'])
        flagged = sum(1 for c in mine if any(f['severity'] == 'block' for f in (c.get('challenge') or {}).get('flags', [])))
        rows.append((p['id'], k['pending'], k['drafted'], k['challenged'], flagged,
                     sum(1 for c in mine if c.get('author')), reviewed))
    ui.table(rows, ['profile', 'pending', 'drafted', 'challenged', 'blocking flags', 'authored', 'reviewed (current)'])
    if store.exists('validation_report.json'):
        rep = store.load('validation_report.json')
        print('  Last validation (%s): %s, %d blocking issue(s)' % (rep['generated_at'], rep['result'], rep['blocking_count']))
    log = store.worklog()
    if log:
        print('  Last activity: %s %s by %s' % (log[-1]['ts'], log[-1]['event'], log[-1]['actor']))
    return 0


def show(store, args):
    cat = {f['id']: f for f in store.catalog()['features']}
    fid = args.feature.upper().replace('MATRIX:', '')
    if fid not in cat:
        raise SystemExit('Unknown feature %s (F01-F18)' % args.feature)
    manifest = store.load('manifest.json')
    pids = args.profile or model.profile_ids(manifest)
    cells = store.load('cells.json')['cells']
    entries = store.load('sources.json')['entries']
    people = store.people()
    cur = review.current(store, cells)
    f = cat[fid]
    ui.heading('MATRIX:%s %s  (%s)' % (fid, f['name'], f['area']))
    ui.wrap('Capability', f['capability'])
    for pid in pids:
        cid = model.cell_id(fid, pid)
        c = cells.get(cid)
        print()
        if not c:
            ui.fail('%s: no cell (coverage error)' % cid)
            continue
        pend = c['assessment_state'] == 'pending'
        ui.wrap('Profile', pid)
        ui.wrap('Finding', 'PENDING RESEARCH (placeholder; not a finding)' if pend else c['status'])
        ui.wrap('State', c['assessment_state'] + ('' if pend else ' / drafted by %s' % c.get('drafted_by')))
        if pend:
            continue
        ui.wrap('Supported', c.get('supported_scope'))
        ui.wrap('Unsupported', c.get('unsupported_scope'))
        ui.wrap('Unestablished', c.get('unestablished_scope'))
        if c.get('gap_reason'):
            ui.wrap('Gap reason', c['gap_reason'])
        ui.wrap('Setup / activation', '%s / %s' % (c.get('required_setup'), c.get('activation_state')))
        ui.wrap('Control mechanism', c.get('control_mechanism'))
        ui.wrap('Uncertainties', c.get('constraints'))
        for r in c.get('evidence_refs', []):
            e = entries.get(r, {})
            ui.wrap('Source MATRIX:%s' % r, '%s | %s | %s | accessed %s | %s | "%s"' % (
                e.get('page_title'), e.get('section'), e.get('url'), e.get('access_date'), e.get('check'), e.get('quote')))
        for fl in (c.get('challenge') or {}).get('flags', []):
            ui.wrap('Challenge [%s]' % fl['severity'], '%s: %s' % (fl['type'], fl['detail']))
        rv = cur.get(cid)
        ui.wrap('Author', people.get(c.get('author'), {}).get('name', 'none (required before review)'))
        ui.wrap('Review', 'none (independent team-member review required)' if not rv else '%s by %s%s%s' % (
            rv['decision'], people.get(rv['reviewer'], {}).get('name', rv['reviewer']),
            ' (%s)' % rv['disposition'] if rv.get('disposition') else '', ' STALE' if rv['stale'] else ''))
    return 0
