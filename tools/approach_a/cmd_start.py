"""`start`: select the tool from candidates, propose and confirm the profile boundary."""
from . import model
from . import store as st
from . import ui


def choose_tool(store, args):
    cands = {c['tool_key']: c for c in store.candidates()}
    if not cands:
        raise SystemExit('No candidate documentation sets in %s/candidates' % store.root)
    keys = sorted(cands)
    default = 'antigravity' if 'antigravity' in cands else keys[0]
    ui.heading('Step 1. Select the tool to assess')
    ui.table([(k, cands[k]['tool'], cands[k]['docs']['base_url'], ', '.join(sorted(cands[k]['surfaces'])))
              for k in keys], ['key', 'tool', 'official documentation', 'prepared surfaces'])
    print('  Tools without a prepared candidate can still be assessed: add a candidate file with the official\n'
          '  documentation base URL. Their cells stay pending until research is done (an honest partial result).')
    key = ui.ask('Tool', default=args.tool or default, choices=keys,
                 assume=(args.tool or default) if args.yes else None)
    return cands[key]


def propose(cand, args):
    surfaces = sorted(cand['surfaces'])
    ui.heading('Step 2. Proposed profile boundary (from official documentation; not yet confirmed)')
    surface = ui.ask('Surface', default=args.surface or cand.get('default_surface') or surfaces[0],
                     choices=surfaces, assume=(args.surface or cand.get('default_surface')) if args.yes else None)
    p = model.profile_from_candidate(cand, surface)
    v = p['version']
    ui.wrap('Profile ID', p['id'])
    ui.wrap('Tool / surface', '%s / %s' % (p['tool'], p['surface_label']))
    ui.wrap('Category tags', ', '.join('MATRIX:' + t for t in p['category_tags']))
    ui.wrap('Version', '%s (%s)' % (v.get('value') or 'unversioned', v.get('kind', '')))
    ui.wrap('Documentation dates', v.get('documentation_note', ''))
    ui.wrap('Modes', p['modes'])
    ui.wrap('Platforms', p['platforms'])
    ui.wrap('Account and tier', p['account_and_tier'])
    ui.wrap('Interface / execution', p['interface_and_execution_location'])
    ui.wrap('Exclusions', p['exclusions'])
    return p


def run(store, args):
    if not store.exists('manifest.json'):
        store.init_from()
        ui.ok('Initialized an empty dataset at %s' % store.root)
    people = store.people()
    cand = choose_tool(store, args)
    p = propose(cand, args)
    manifest = store.load('manifest.json')
    existing = next((x for x in manifest['profiles'] if x['id'] == p['id']), None)
    if existing and existing.get('confirmed_by'):
        ui.warn('Profile %s is already confirmed in manifest version %s. Use `research` or `resume`.'
                % (p['id'], manifest['manifest_version']))
        return 0
    if args.rehearsal:
        if existing:
            ui.warn('Profile %s is already proposed (rehearsal). Use `research --rehearsal`.' % p['id'])
            return 0
        model.add_profile(store, dict(p, boundary_state='proposed', source_access_date=st.today()),
                          'agent-rehearsal')
        ui.warn('REHEARSAL: %s added as a PROPOSED boundary (no one confirmed it). Cells drafted now are '
                'rehearsal drafts; `start` without --rehearsal records the real confirmation.' % p['id'])
        if args.research:
            from . import cmd_research
            return cmd_research.run(store, args, only=[p['id']])
        return 0
    ui.heading('Step 3. Adjust and confirm the boundary before research')
    if not args.yes:
        tier = ui.ask('Account and tier for this assessment (Enter keeps the proposal)', default='keep')
        if tier != 'keep':
            p['account_and_tier'] = tier
        extra = ui.ask('Additional exclusions, separated by ";" (Enter for none)', default='')
        p['exclusions'] = p['exclusions'] + [x.strip() for x in extra.split(';') if x.strip()]
    print('  Confirming records who accepted this boundary. It is not the manifest approval; an approver\n'
          '  (%s) must approve the manifest version before any cell can be accepted.'
          % ', '.join(x['name'] for x in people.values() if 'approver' in x['roles']))
    if args.yes and not args.operator:
        raise ValueError('--yes requires --operator <roster id>')
    who = ui.ask('Your roster id', choices=list(people), assume=args.operator if args.yes else None)
    if who not in people:
        raise ValueError('operator %r is not on the roster (%s); manifest unchanged' % (who, ', '.join(people)))
    if ui.ask('Confirm this profile boundary', default='n', choices=['y', 'n'], assume='y' if args.yes else None) != 'y':
        ui.warn('Not confirmed; manifest unchanged.')
        store.log('profile_proposed_not_confirmed', actor=who, profile_id=p['id'])
        return 1
    p.update({'confirmed_by': who, 'confirmed_at': st.now(), 'source_access_date': st.today(),
              'boundary_state': 'confirmed'})
    m = model.confirm_profile(store, p, who) if existing else model.add_profile(store, p, who)
    ui.ok('%s %s in manifest version %d (P = %d, %d cells).' % (
        'Confirmed' if existing else 'Added', p['id'], m['manifest_version'], len(m['profiles']), 18 * len(m['profiles'])))
    ui.warn('Manifest version %d is NOT approved. Approve with: assess approve --approver <id>' % m['manifest_version'])
    if args.research:
        from . import cmd_research
        return cmd_research.run(store, args, only=[p['id']])
    print('\n  Next: python3 -m tools.approach_a research --profile %s' % p['id'])
    return 0
