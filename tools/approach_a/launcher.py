"""Small guided front door to the existing workbench handlers (stdlib only)."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

from . import azure, cmd_blockers, cmd_misc, cmd_research, cmd_start, packet, preview_server, publish
from . import research, store as st, ui, validate
from . import __main__ as cli


def selection_file():
    # Checkout-local, ignored, and outside the authoritative dataset.
    return Path(st.REPO) / '.matrix-data.json'


def saved_selection():
    path = selection_file()
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding='utf-8'))['path']
    if not isinstance(value, str) or not os.path.isabs(value):
        raise ValueError('Invalid local dataset selection; use ./matrix use --clear')
    return value


def resolve_dataset(explicit=None):
    if explicit:
        return str(Path(explicit).expanduser().resolve())
    if os.environ.get('APPROACH_A_DATA'):
        return str(Path(os.environ['APPROACH_A_DATA']).expanduser().resolve())
    saved = saved_selection()
    if saved:
        if not Path(saved).is_dir():
            raise ValueError('Saved dataset is missing: %s. Use ./matrix use --clear or --data PATH.' % saved)
        return str(Path(saved).resolve())
    return str(Path(st.DEFAULT_ROOT).resolve())


def use(argv, explicit=None):
    parser = argparse.ArgumentParser(prog='./matrix use')
    parser.add_argument('path', nargs='?')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--show', action='store_true')
    group.add_argument('--clear', action='store_true')
    args = parser.parse_args(argv)
    if args.path and (args.show or args.clear):
        parser.error('choose a path, --show, or --clear')
    if args.clear:
        selection_file().unlink(missing_ok=True)
        print('Local dataset selection cleared.')
    elif args.path:
        root = Path(args.path).expanduser().resolve()
        if not root.is_dir():
            raise ValueError('Dataset directory does not exist: %s' % root)
        fd, temporary = tempfile.mkstemp(dir=st.REPO, prefix='.matrix-selection-')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as output:
                json.dump({'path': str(root)}, output)
                output.write('\n')
            os.replace(temporary, selection_file())
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        print('Saved dataset: %s' % root)
    else:
        saved = saved_selection()
        print('Saved dataset: %s%s' % (saved or '(none)',
              ' (MISSING)' if saved and not Path(saved).is_dir() else ''))
    print('Resolved dataset: %s' % resolve_dataset(explicit))
    return 0


def review_counts(store):
    counts = Counter()
    for issue in cmd_blockers.blockers(store):
        if issue['code'] in cmd_blockers.REVIEW_CODES:
            # Multiple review blockers must count one cell only.
            counts[issue['where']] = 1
    profiles = Counter()
    for cid in counts:
        profiles[cid.rsplit('/', 1)[0]] += 1
    return profiles


def review_queue(store, argv):
    parser = argparse.ArgumentParser(prog='./matrix review')
    parser.add_argument('--profile')
    parser.add_argument('--operator')
    args = parser.parse_args(argv)
    counts = review_counts(store)
    if not counts:
        print('No outstanding cell reviews. Use ./matrix blockers for author, boundary or approval issues.')
        return 0
    if args.profile and args.profile not in counts:
        raise ValueError('No outstanding reviews for profile: %s' % args.profile)
    selected = args.profile or (next(iter(counts)) if len(counts) == 1 else cmd_blockers.choose(
        'Profiles needing review', [(pid, '%d remaining cell review(s)' % count) for pid, count in counts.items()]))
    print(packet.build(store, selected))
    print('Record responsible authors first if needed: ./matrix blockers --profile %s --code AUTHOR_MISSING' % selected)
    walker = cmd_blockers.Walker(store, args.operator)
    for code in sorted(cmd_blockers.REVIEW_CODES):
        walker.walk(selected, code)
    cmd_blockers.inventory(store)
    return 0


def confirm_research(args):
    config = azure.load_config()
    if azure.draft_mode(args, config) != 'azure':
        print('Model-assisted drafting: off (prepared briefs and saved drafts only).')
        return True
    if args.offline:
        raise ValueError('Azure drafting cannot run offline. Use --no-draft.')
    conn = azure.connection(config, env_file=azure.env_file_for(args, config))
    overrides = {'max_requests_per_run': args.max_requests, 'max_tokens_per_run': args.token_budget,
                 'max_cost_usd_per_run': args.max_cost}
    ledger = azure.Ledger(config, azure.spend_ledger_path(config), overrides)
    print('Paid drafting: Azure deployment %s on %s; API %s. Returned model version is recorded when available.'
          % (conn.deployment, conn.host, conn.api_version))
    ui.wrap('Configured budget', ledger.lim)
    print('Estimated spending already recorded: $%.4f (prices are estimates).' % ledger.prior)
    return cmd_blockers.ask('Start research with these paid drafting limits?', default='n', choices=['y', 'n']) == 'y'


def start(store, argv):
    args = cli.parser().parse_args(['start', *argv])
    if args.yes or args.rehearsal:
        raise ValueError('Guided start requires human boundary confirmation; use the module CLI for scripted/rehearsal setup.')
    before = {p['id']: p for p in store.load('manifest.json')['profiles']}
    args.research = False  # Offer only after the boundary has been explicitly confirmed.
    result = cmd_start.run(store, args)
    if result:
        return result
    changed = [p['id'] for p in store.load('manifest.json')['profiles']
               if p.get('confirmed_by') and p != before.get(p['id'])]
    if changed and cmd_blockers.ask('Start research now?', default='n', choices=['y', 'n']) == 'y':
        if confirm_research(args):
            return cmd_research.run(store, args, only=changed)
    return 0


def preview(store, argv):
    parser = argparse.ArgumentParser(prog='./matrix preview')
    parser.add_argument('--port', type=int, default=4174)
    args = parser.parse_args(argv)
    result = publish.run(store, SimpleNamespace(mode='preview', out=None, allow_other_out=False, source_commit=None))
    if result:
        return result
    print('Draft preview: http://127.0.0.1:%d/feature-matrix/?preview=matrix.preview.json' % args.port, flush=True)
    return preview_server.run(store, args)


def home(store, interactive):
    exists = store.exists('manifest.json')
    actions = [('start', 'Start / add a profile (confirm its boundary)')]
    if exists:
        cmd_misc.status(store, SimpleNamespace())
        report = validate.inspect(store)
        cells = store.load('cells.json')['cells']
        if any(c['assessment_state'] in ('pending', 'drafted') for c in cells.values()):
            actions.append(('resume', 'Resume research'))
        if review_counts(store):
            actions.append(('review', 'Review findings and exceptions'))
        if store.load('manifest.json')['profiles']:
            actions.append(('preview', 'Generate and serve a labeled draft preview'))
        if report['accepted']:
            actions.append(('export', 'Prepare a local accepted export'))
        else:
            print('Remaining blockers:', report['counts_by_code'])
        print('Troubleshooting and explicit manifest approval: ./matrix blockers')
    else:
        print('No manifest here yet. Choose start to initialize and propose a profile.')
    if not interactive:
        ui.table(actions, ['action', 'next step'])
        return 0
    action = cmd_blockers.choose('Next action (opening this menu changes nothing)', actions)
    return dispatch(store, action, [])


def dispatch(store, command, argv):
    print('Dataset: %s' % store.root, flush=True)
    if command == 'start':
        return start(store, argv)
    if command not in ('init', 'new') and not store.exists('manifest.json'):
        raise ValueError('No dataset manifest at %s; run ./matrix start.' % store.root)
    if command == 'review' and not any(a == '--reviewer' or a.startswith('--reviewer=') for a in argv):
        return review_queue(store, argv)
    if command == 'preview':
        return preview(store, argv)
    if command in ('resume', 'research'):
        args = cli.parser().parse_args([command, *argv])
        if not confirm_research(args):
            return 0
    if command == 'export':
        argv = list(argv)
        public = '--public' in argv
        if public:
            argv.remove('--public')
        if not public and not any(a == '--out' or a.startswith('--out=') for a in argv):
            argv += ['--allow-other-out', '--out', os.path.join(publish.PREVIEW_DIR, 'matrix.accepted.json')]
        command = 'export-publication'
    return cli.main(['--data', store.root, command, *argv])


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--data')
    args, rest = parser.parse_known_args(sys.argv[1:] if argv is None else argv)
    try:
        if rest and rest[0] == 'use':
            return use(rest[1:], args.data)
        if rest in (['--help'], ['-h']):
            print('./matrix [--data PATH] [start | resume | review | preview | export [--public]]')
            print('./matrix use PATH | use --show | use --clear; all module CLI commands also remain available.')
            return 0
        store = st.Store(resolve_dataset(args.data))
        if not rest:
            print('Dataset: %s' % store.root, flush=True)
            return home(store, sys.stdin.isatty() and sys.stdout.isatty())
        if rest[0] in ('start', 'review') and not any(
                a == '--reviewer' or a.startswith('--reviewer=') for a in rest) and not sys.stdin.isatty():
            print('Dataset: %s' % store.root, flush=True)
            print('Guided setup/review needs an interactive terminal. Showing status only.')
            return home(store, False)
        return dispatch(store, rest[0], rest[1:])
    except (cmd_blockers.Quit, cmd_blockers.Back, EOFError):
        print('Stopped; no further actions taken.')
        return 0
    except KeyboardInterrupt:
        print('\nStopped; no further actions taken.')
        return 130
    except (ValueError, OSError, KeyError) as error:
        print('error: %s' % error)
        return 2
    except research.Stopped as error:
        print('Research stopped: %s; resume when ready.' % error)
        return 3
