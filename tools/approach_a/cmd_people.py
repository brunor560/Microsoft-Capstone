"""Human-decision commands: approve, author, review; plus validate, render, resume, init."""
from . import cmd_misc
from . import model
from . import render
from . import review
from . import ui
from . import validate


def _cells(args, store):
    manifest = store.load('manifest.json')
    pids = args.profile or model.profile_ids(manifest)
    feats = [f.upper() for f in args.feature] if args.feature else [f['id'] for f in store.catalog()['features']]
    return [model.cell_id(f, p) for p in pids for f in feats]


def approve(store, args):
    m = review.approve(store, args.approver)
    ui.ok('Manifest version %d approved by %s (SHA-256 %s...). Any later manifest change clears this approval.'
          % (m['manifest_version'], args.approver, m['approval']['manifest_sha256'][:12]))
    return 0


def author(store, args):
    failed = 0
    for cid in _cells(args, store):
        try:
            review.set_author(store, cid, args.author)
            ui.ok('%s author: %s' % (cid, args.author))
        except ValueError as e:
            failed += 1
            ui.warn(str(e))
    return 1 if failed else 0


def do_review(store, args):
    failed = 0
    for cid in _cells(args, store):
        try:
            review.record(store, cid, args.reviewer, args.decision, args.note, args.disposition)
            ui.ok('%s %s by %s' % (cid, args.decision, args.reviewer))
        except ValueError as e:
            failed += 1
            ui.fail(str(e))
    return 1 if failed else 0


def do_validate(store, args):
    rep = validate.run(store)
    render.run(store)
    cmd_misc.print_validation(rep, brief=args.brief)
    return 0 if rep['accepted'] else 1


def do_render(store, args):
    files = render.run(store)
    ui.ok('%d files written under %s/out' % (len(files), store.root))
    return 0


def resume(store, args):
    """Continue where the last session stopped: unresearched cells, then checks."""
    if not store.exists('manifest.json'):
        ui.fail('No dataset at %s; run `start`.' % store.root)
        return 2
    cmd_misc.status(store, args)
    cells = store.load('cells.json')['cells']
    k = model.counts(cells)
    log = store.worklog()
    started = [i for i, e in enumerate(log) if e['event'] == 'research_started']
    done = [i for i, e in enumerate(log) if e['event'] == 'validated']
    never_ran = bool(cells) and not started
    interrupted = bool(started) and (not done or done[-1] < started[-1])
    if interrupted:
        ui.warn('The research run started at %s stopped before validation; resuming it.' % log[started[-1]]['ts'])
    if never_ran or interrupted or k['drafted']:
        from . import cmd_research
        return cmd_research.run(store, args)
    if k['pending']:
        ui.warn('%d cell(s) remain pending: no researched brief exists for them yet. They are not findings.'
                % k['pending'])
    ui.ok('Nothing automated is left to resume. Remaining work is human: author, review and approval.')
    return do_validate(store, args)


def init(store, args):
    store.init_from(force=args.force)
    ui.ok('Initialized an empty dataset at %s (catalog, roster and candidates copied; no profiles).' % store.root)
    return 0
