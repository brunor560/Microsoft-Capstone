"""Approach A assessment workbench (documentation-only feature matrix).

Usage: python3 -m tools.approach_a [--data DIR] <command> [options]
Run from the repository root. Standard library only.
"""
import argparse
import sys

from . import cmd_misc
from . import cmd_new
from . import cmd_people
from . import cmd_research
from . import cmd_start
from . import research
from . import store as st


def parser():
    ap = argparse.ArgumentParser(prog='python3 -m tools.approach_a', description=__doc__.split('\n')[0])
    ap.add_argument('--data', help='dataset directory (default: assessment/ or $APPROACH_A_DATA)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('start', help='select a tool, propose and confirm its profile boundary')
    s.add_argument('--tool', help='candidate key (default: antigravity)')
    s.add_argument('--surface', help='product surface (default: the candidate default)')
    s.add_argument('--operator', help='your roster id (required with --yes)')
    s.add_argument('--yes', action='store_true', help='accept proposals without prompting (scripted runs)')
    s.add_argument('--research', action='store_true', help='continue straight into research after confirming')
    s.add_argument('--offline', action='store_true', help='use cached pages only')
    s.add_argument('--refresh', action='store_true', help='re-fetch pages even if cached')
    s.add_argument('--crawl-limit', type=int, default=40)
    s.add_argument('--profile', action='append')
    s.add_argument('--rehearsal', action='store_true',
                   help='add the proposal as an UNCONFIRMED boundary for a labeled practice run')

    r = sub.add_parser('research', help='discover sources, run research agents and the challenge pass')
    for a in (r,):
        a.add_argument('--profile', action='append', help='limit to a profile id (repeatable)')
        a.add_argument('--operator', help='roster id recorded in the work log')
        a.add_argument('--offline', action='store_true', help='use cached pages only')
        a.add_argument('--refresh', action='store_true', help='re-fetch pages even if cached')
        a.add_argument('--crawl-limit', type=int, default=40)
        a.add_argument('--rehearsal', action='store_true', help='allow research on a proposed boundary')

    sub.add_parser('status', help='progress by profile and the last validation result')
    sh = sub.add_parser('show', help="inspect one feature's finding, scope, sources and review state")
    sh.add_argument('feature', help='F01-F18')
    sh.add_argument('--profile', action='append')

    v = sub.add_parser('validate', help='check coverage, fields, evidence, approval and review')
    v.add_argument('--brief', action='store_true')
    sub.add_parser('render', help='regenerate Markdown outputs from the JSON dataset')

    ap_ = sub.add_parser('approve', help='record manifest approval (approver role only)')
    ap_.add_argument('--approver', required=True)
    au = sub.add_parser('author', help='record the team member responsible for drafted cells')
    au.add_argument('--author', required=True)
    rv = sub.add_parser('review', help='record an independent team-member review')
    rv.add_argument('--reviewer', required=True)
    rv.add_argument('--decision', required=True, choices=['agree', 'disagree'])
    rv.add_argument('--note', required=True)
    rv.add_argument('--disposition', choices=['author_revised', 'reviewer_withdrew', 'escalated'])
    for a in (au, rv):
        a.add_argument('--feature', action='append', help='F01-F18 (repeatable; default all)')
        a.add_argument('--profile', action='append')

    rs = sub.add_parser('resume', help='continue an interrupted or partial assessment')
    rs.add_argument('--profile', action='append')
    rs.add_argument('--operator')
    rs.add_argument('--offline', action='store_true')
    rs.add_argument('--refresh', action='store_true')
    rs.add_argument('--crawl-limit', type=int, default=40)
    rs.add_argument('--brief', action='store_true')
    rs.add_argument('--rehearsal', action='store_true')
    i = sub.add_parser('init', help='create an empty dataset (catalog, roster and candidates only)')
    i.add_argument('--force', action='store_true')
    n = sub.add_parser('new', help='add a candidate for a tool with no prepared research')
    n.add_argument('--tool-name')
    n.add_argument('--docs-url', help='official documentation base URL (https, ending in /)')
    n.add_argument('--surface')
    n.add_argument('--category', help='MATRIX category tag, for example T2')
    n.add_argument('--operator')
    n.add_argument('--yes', action='store_true')
    return ap


def main(argv=None):
    args = parser().parse_args(argv)
    store = st.Store(args.data)
    if args.cmd not in ('start', 'init', 'new') and not store.exists('manifest.json'):
        print('No dataset at %s. Run `start` (or `init`) first.' % store.root)
        return 2
    handlers = {'start': cmd_start.run, 'research': cmd_research.run, 'status': cmd_misc.status,
                'show': cmd_misc.show, 'validate': cmd_people.do_validate, 'render': cmd_people.do_render,
                'approve': cmd_people.approve, 'author': cmd_people.author, 'review': cmd_people.do_review,
                'resume': cmd_people.resume, 'init': cmd_people.init, 'new': cmd_new.run}
    try:
        return handlers[args.cmd](store, args)
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        print('error: %s' % e)
        return 2
    except research.Stopped as e:
        print('\nStopped: %s. Completed cells were saved; continue with `resume`.' % e)
        return 3
    except KeyboardInterrupt:
        store.log('interrupted', command=args.cmd)
        print('\nInterrupted. Progress is saved after each step; continue with `resume`.')
        return 130


if __name__ == '__main__':
    sys.exit(main())
