"""`research`: source discovery, optional model drafting, research agents, challenge pass,
artifacts, validation."""
from . import azure
from . import challenge
from . import drafting
from . import model
from . import render
from . import research
from . import sources as src
from . import ui
from . import validate


OPT_OUT = 'Run with --no-draft to use prepared briefs and saved drafts only.'


def draft_client(store, args, operator):
    """Build the Azure client when drafting is on (the default in drafting.json).

    Returns (client, error): client is None when drafting is off; error is a
    message when drafting is on but Azure cannot be used, and the command must
    stop. Nothing is logged and no request is sent before this succeeds.
    """
    config = azure.load_config()
    if azure.draft_mode(args, config) != 'azure':
        return None, None
    if getattr(args, 'offline', False):
        return None, 'Drafting with Azure is on, but --offline allows no network requests. ' + OPT_OUT
    env_file = azure.env_file_for(args, config)
    try:
        conn = azure.connection(config, env_file=env_file)
    except (ValueError, FileNotFoundError) as e:
        return None, 'Azure is not available: %s. %s' % (e, OPT_OUT)
    overrides = {'max_requests_per_run': getattr(args, 'max_requests', None),
                 'max_tokens_per_run': getattr(args, 'token_budget', None),
                 'max_cost_usd_per_run': getattr(args, 'max_cost', None)}
    ledger = azure.Ledger(config, azure.spend_ledger_path(config), overrides)
    lim = ledger.lim
    ui.phase('draft', 'deployment %s on %s (prompt %s)' % (conn.deployment, conn.host, config['prompt_version']))
    ui.ok('Limits: %d requests, %d tokens and $%.2f per run; $%.2f total (already recorded: $%.4f); '
          '%d requests and %d tokens per minute' % (
              lim['max_requests_per_run'], lim['max_tokens_per_run'], lim['max_cost_usd_per_run'],
              lim['max_cost_usd_total'], ledger.prior, lim['requests_per_minute'], lim['tokens_per_minute']))
    store.log('model_drafting_configured', actor=operator, limits=lim, prompt_version=config['prompt_version'],
              prior_spend_usd=round(ledger.prior, 4), **conn.describe())
    return azure.Client(conn, config, ledger, notify=lambda m: print('        ' + m, flush=True)), None


def run_drafting(store, index, cands, profiles, discovered, client, args, operator):
    """Draft missing briefs per profile; return {profile_id: drafts} for the research agents."""
    out = {}
    for p in profiles:
        cand = cands.get(p.get('tool_key'))
        if not cand or p['id'] not in discovered:
            continue
        ui.phase('draft', '%s: one request per feature, sequential' % p['id'])
        r = drafting.draft_profile(store, index, cand, p, discovered[p['id']], client, ui.progress,
                                   operator, redraft=getattr(args, 'redraft', False))
        store.log('model_drafting_finished', actor='drafting:' + p['id'], usage=client.ledger.summary(), **r)
        (ui.ok if not r['stopped'] else ui.warn)(
            '%s: %d drafted, %d already drafted or human-owned, %d rejected, %d failed, %d without excerpts%s'
            % (p['id'], r['drafted'], r['skipped'], r['rejected'], r['failed'], r['no_excerpts'],
               '; STOPPED (%s)' % r['stopped'] if r['stopped'] else ''))
        out[p['id']] = drafting.load_drafts(store, p['id'])
    s = client.ledger.summary()
    ui.ok('Azure usage this run: %d request(s), %d input + %d output tokens, about $%.4f '
          '(cumulative $%.4f of $%.2f cap)' % (s['requests'], s['input_tokens'], s['output_tokens'],
                                               s['estimated_cost_usd'], s['cumulative_cost_usd'], s['cap_usd']))
    return out


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
    client, error = draft_client(store, args, operator)
    if error:
        ui.fail(error)
        store.log('research_refused', actor=operator, reason='azure_unavailable', detail=error)
        return 2
    store.log('research_started', actor=operator, profiles=[p['id'] for p in profiles],
              offline=bool(getattr(args, 'offline', False)), rehearsal=bool(unconfirmed),
              drafting='azure' if client else 'off')
    index = src.SourceIndex(store, offline=getattr(args, 'offline', False), refresh=getattr(args, 'refresh', False))

    discovered = {}
    for p in profiles:
        cand = cands.get(p.get('tool_key'))
        if not cand:
            ui.warn('%s: no candidate documentation set; its cells stay pending.' % p['id'])
            continue
        seeds = cand['surfaces'][p['surface']].get('seed_pages', [])
        ui.phase('discovery', '%s (%s)' % (p['id'], cand['docs']['base_url']))
        seen, ok = src.discover(index, cand['docs'], seeds, getattr(args, 'crawl_limit', 40), ui.progress)
        index.save()
        discovered[p['id']] = seen
        store.log('sources_discovered', actor=operator, profile_id=p['id'], pages=len(seen), ok=ok)
        (ui.ok if ok == len(seen) else ui.warn)('%d of %d pages available' % (ok, len(seen)))

    if client:
        try:
            briefs = run_drafting(store, index, cands, profiles, discovered, client, args, operator)
        except azure.Unavailable as e:
            index.save()
            store.log('research_stopped', actor=operator, reason='azure_unavailable', detail=str(e),
                      usage=client.ledger.summary())
            ui.fail('Azure is not available: %s' % e)
            ui.fail('Stopped before assessment. Drafts saved so far are kept; continue with `resume` once Azure '
                    'responds. ' + OPT_OUT)
            return 2
    else:
        # Model drafts saved by an earlier --draft run are reused; others use prepared briefs.
        briefs = {p['id']: drafting.load_drafts(store, p['id']) for p in profiles
                  if drafting.load_drafts(store, p['id'])}

    ui.phase('assess', 'one research agent per profile, sharing one source index')
    results = research.run_agents(store, index, cands, profiles, operator, ui.progress, briefs)
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
