"""`research`: source discovery, research agents, challenge pass, artifacts, validation."""
from . import challenge
from . import model
from . import render
from . import research
from . import sources as src
from . import ui
from . import validate


def run(store, args, only=None):
    manifest = store.load('manifest.json')
    wanted = only or args.profile or model.profile_ids(manifest)
    profiles = [p for p in manifest['profiles'] if p['id'] in wanted]
    if not profiles:
        ui.fail('No matching profiles in the manifest. Run `start` first.')
        return 2
    unconfirmed = [p['id'] for p in profiles if not p.get('confirmed_by')]
    if unconfirmed and not getattr(args, 'rehearsal', False):
        ui.fail('Boundary not confirmed for %s. Confirm it with `start` before research '
                '(or pass --rehearsal for a labeled practice run).' % ', '.join(unconfirmed))
        return 2
    if unconfirmed:
        ui.warn('REHEARSAL run on proposed boundaries: %s' % ', '.join(unconfirmed))
    cands = {c['tool_key']: c for c in store.candidates()}
    operator = getattr(args, 'operator', None) or 'cli'
    store.log('research_started', actor=operator, profiles=[p['id'] for p in profiles],
              offline=bool(getattr(args, 'offline', False)), rehearsal=bool(unconfirmed))
    index = src.SourceIndex(store, offline=getattr(args, 'offline', False), refresh=getattr(args, 'refresh', False))

    for p in profiles:
        cand = cands.get(p.get('tool_key'))
        if not cand:
            ui.warn('%s: no candidate documentation set; its cells stay pending.' % p['id'])
            continue
        seeds = cand['surfaces'][p['surface']].get('seed_pages', [])
        ui.phase('discovery', '%s (%s)' % (p['id'], cand['docs']['base_url']))
        seen, ok = src.discover(index, cand['docs'], seeds, getattr(args, 'crawl_limit', 40), ui.progress)
        index.save()
        store.log('sources_discovered', actor=operator, profile_id=p['id'], pages=len(seen), ok=ok)
        (ui.ok if ok == len(seen) else ui.warn)('%d of %d pages available' % (ok, len(seen)))

    ui.phase('assess', 'one research agent per profile, sharing one source index')
    results = research.run_agents(store, index, cands, profiles, operator, ui.progress)
    for pid, r in results.items():
        store.log('research_agent_finished', actor='research-agent:' + pid, **{k: v for k, v in r.items() if k != 'features'})
        ui.ok('%s: %d drafted, %d still pending, %d kept, %d citation(s) rejected'
              % (pid, r['drafted'], r['left_pending'], r['kept'], r['rejected_quotes']))

    ui.phase('challenge')
    s = challenge.run(store, ui.progress, operator)
    (ui.ok if not s['blocking'] else ui.warn)('%d cells checked, %d blocking flag(s), %d warning(s): %s'
                                              % (s['checked'], s['blocking'], s['warnings'], s['by_type'] or 'none'))

    ui.phase('render')
    rep = validate.run(store)
    files = render.run(store)
    ui.progress('render', len(files), len(files), '%d files under %s/out' % (len(files), store.root))

    ui.phase('validate')
    from . import cmd_misc
    cmd_misc.print_validation(rep, brief=True)
    return 0
