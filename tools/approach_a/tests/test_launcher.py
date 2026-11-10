"""Launcher routing and local state, always using disposable fixtures."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

from tools.approach_a import launcher, review, store as st
from tools.approach_a.__main__ import parser as cli_parser
from tools.approach_a.tests.test_validation import Base


class Launcher(Base):
    def setUp(self):
        super().setUp()
        self.dir = str(Path(self.dir).resolve())
        self.store = st.Store(self.dir)
        self.checkout = Path(self.dir) / 'checkout'
        self.checkout.mkdir()
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(st, 'REPO', str(self.checkout)))
        self.stack.enter_context(patch.dict(os.environ, {}, clear=True))

    def run_launcher(self, args, answers=(), tty=True):
        output = io.StringIO()
        with patch('sys.stdin.isatty', return_value=tty), patch('sys.stdout.isatty', return_value=tty), \
                patch('builtins.input', side_effect=answers), contextlib.redirect_stdout(output):
            result = launcher.main(args)
        return result, output.getvalue()

    def snapshot(self):
        return {str(p): p.read_bytes() for p in Path(self.dir).rglob('*') if p.is_file()}

    def test_dataset_precedence_and_selection_inspect_clear(self):
        self.assertEqual(self.run_launcher(['use', self.dir])[0], 0)
        self.assertEqual(launcher.resolve_dataset(), str(Path(self.dir).resolve()))
        with patch.dict(os.environ, {'APPROACH_A_DATA': '/tmp/environment-dataset'}):
            self.assertEqual(launcher.resolve_dataset(), str(Path('/tmp/environment-dataset').resolve()))
            self.assertEqual(launcher.resolve_dataset('/tmp/explicit-dataset'), str(Path('/tmp/explicit-dataset').resolve()))
        self.assertIn(str(Path(self.dir).resolve()), self.run_launcher(['use', '--show'])[1])
        self.assertEqual(self.run_launcher(['use', '--clear'])[0], 0)
        self.assertFalse(launcher.selection_file().exists())
        self.assertEqual(launcher.resolve_dataset(), str(Path(st.DEFAULT_ROOT).resolve()))

    def test_missing_saved_dataset_is_clear_and_does_not_fall_back(self):
        launcher.selection_file().write_text(json.dumps({'path': str(self.checkout / 'missing')}))
        result, output = self.run_launcher([], tty=False)
        self.assertEqual(result, 2)
        self.assertIn('Saved dataset is missing', output)
        self.assertIn('use --clear', output)
        self.assertEqual(self.run_launcher(['--data', self.dir], tty=False)[0], 0)

    def test_noninteractive_startup_and_menu_opening_do_not_write(self):
        self.add_profile()
        self.complete_cells()
        before = self.snapshot()
        result, output = self.run_launcher(['--data', self.dir], tty=False)
        self.assertEqual(result, 0)
        self.assertIn('Dataset: ' + self.dir, output)
        self.assertIn('review', output)
        self.assertIn('preview', output)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.run_launcher(['--data', self.dir], ['q'])[0], 0)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.run_launcher(['--data', self.dir, 'start'], tty=False)[0], 0)
        self.assertEqual(before, self.snapshot())

    def test_single_profile_review_opens_packet_and_queue_directly(self):
        self.add_profile()
        self.complete_cells()
        before = self.snapshot()
        with patch.object(launcher.cmd_blockers.Walker, 'walk') as walk:
            result, output = self.run_launcher(['--data', self.dir, 'review'])
        self.assertEqual(result, 0)
        self.assertIn('# Review packet: tool-cli', output)
        self.assertIn(('tool-cli', 'REVIEW_MISSING'), [call.args for call in walk.call_args_list])
        self.assertEqual(before, self.snapshot())

    def test_multiple_profiles_show_counts_before_selecting_review_queue(self):
        self.add_profile()
        self.complete_cells()
        self.add_profile(pid='second-cli')
        self.complete_cells(pid='second-cli')
        review.record(self.store, 'second-cli/F01', 'bruno', 'agree', 'Fixture review')
        with patch.object(launcher.cmd_blockers.Walker, 'walk') as walk:
            result, output = self.run_launcher(['--data', self.dir, 'review'], ['second-cli'])
        self.assertEqual(result, 0)
        self.assertIn('18 remaining cell review(s)', output)
        self.assertIn('17 remaining cell review(s)', output)
        self.assertTrue(all(call.args[0] == 'second-cli' for call in walk.call_args_list))

    def test_preview_exports_standard_draft_before_starting_existing_server(self):
        self.add_profile()
        events = []
        def export(store, args):
            events.append(('export', store.root, args.mode, args.out))
            return 0
        def serve(store, args):
            events.append(('serve', store.root, args.port))
            return 0
        with patch.object(launcher.publish, 'run', side_effect=export), \
                patch.object(launcher.preview_server, 'run', side_effect=serve):
            result, output = self.run_launcher(['--data', self.dir, 'preview', '--port', '4188'])
        self.assertEqual(result, 0)
        self.assertEqual(events, [('export', self.dir, 'preview', None), ('serve', self.dir, 4188)])
        self.assertIn('http://127.0.0.1:4188/feature-matrix/?preview=matrix.preview.json', output)

    def test_preview_failure_does_not_start_server(self):
        self.add_profile()
        with patch.object(launcher.publish, 'run', side_effect=ValueError('Fixture path rejection')), \
                patch.object(launcher.preview_server, 'run') as serve:
            self.assertEqual(self.run_launcher(['--data', self.dir, 'preview'])[0], 2)
        serve.assert_not_called()

    def test_start_reuses_default_surface_and_offers_research_after_confirmation(self):
        seen = []
        def setup(store, args):
            seen.append((args.surface, args.research, args.yes))
            self.add_profile()
            return 0
        with patch.object(launcher.cmd_start, 'run', side_effect=setup), \
                patch.object(launcher.cmd_research, 'run', return_value=0) as research:
            result, _ = self.run_launcher(['--data', self.dir, 'start', '--no-draft'], ['y'])
        self.assertEqual(result, 0)
        self.assertEqual(seen, [(None, False, False)])
        self.assertEqual(research.call_args.kwargs['only'], ['tool-cli'])

    def test_declining_research_does_not_configure_or_call_model(self):
        def setup(store, args):
            self.add_profile()
            return 0
        with patch.object(launcher.cmd_start, 'run', side_effect=setup), \
                patch.object(launcher.azure, 'connection') as connection, \
                patch.object(launcher.cmd_research, 'run') as research:
            result, _ = self.run_launcher(['--data', self.dir, 'start'], ['n'])
        self.assertEqual(result, 0)
        connection.assert_not_called()
        research.assert_not_called()

    def test_paid_drafting_shows_model_budget_and_requires_confirmation(self):
        self.add_profile()
        conn = SimpleNamespace(deployment='fixture-model', host='example.invalid', api_version='fixture-api')
        ledger = SimpleNamespace(lim={'max_requests_per_run': 3, 'max_cost_usd_per_run': 0.25}, prior=0)
        with patch.object(launcher.azure, 'connection', return_value=conn), \
                patch.object(launcher.azure, 'Ledger', return_value=ledger), \
                patch.object(launcher.cli, 'main') as invoke:
            result, output = self.run_launcher(['--data', self.dir, 'research', '--draft', 'azure'], ['n'])
        self.assertEqual(result, 0)
        self.assertIn('fixture-model', output)
        self.assertIn('max_cost_usd_per_run', output)
        invoke.assert_not_called()

    def test_export_defaults_local_and_public_requires_explicit_flag(self):
        self.add_profile()
        with patch.object(launcher.cli, 'main', return_value=0) as invoke:
            self.run_launcher(['--data', self.dir, 'export'])
            args = invoke.call_args.args[0]
            self.assertIn('--allow-other-out', args)
            self.assertIn('matrix.accepted.json', args[-1])
            self.run_launcher(['--data', self.dir, 'export', '--public'])
            self.assertEqual(invoke.call_args.args[0], ['--data', self.dir, 'export-publication'])

    def test_root_executable_and_original_module_cli_remain_compatible(self):
        self.add_profile()
        self.complete_cells()
        repo = Path(__file__).resolve().parents[3]
        env = dict(os.environ, APPROACH_A_DATA=self.dir)
        for command in ([str(repo / 'matrix'), '--data', self.dir, 'status'],
                        [sys.executable, '-m', 'tools.approach_a', '--data', self.dir, 'status']):
            result = subprocess.run(command, cwd=repo, env=env, stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('tool-cli', result.stdout)
            self.assertIn(self.dir, result.stdout)
        self.assertEqual(cli_parser().parse_args(['review', '--reviewer', 'bruno', '--decision',
                                                  'agree', '--note', 'Fixture']).cmd, 'review')

    def test_guided_start_confirms_actual_candidate_default_in_scratch_only(self):
        candidates = {c['tool_key']: c for c in self.store.candidates()}
        candidate = candidates['antigravity']
        result, output = self.run_launcher(['--data', self.dir, 'start', '--no-draft'],
                                          ['antigravity', '', 'keep', '', 'ross', 'y', 'n'])
        self.assertEqual(result, 0)
        profile = self.store.load('manifest.json')['profiles'][0]
        self.assertEqual(profile['surface'], candidate['default_surface'])
        self.assertEqual(profile['confirmed_by'], 'ross')
        self.assertIsNone(self.store.load('manifest.json')['approval'])
        self.assertIn('Proposed profile boundary', output)
        self.assertIn('Account and tier', output)

    def test_selection_is_checkout_local_and_module_cli_ignores_it(self):
        self.run_launcher(['use', self.dir])
        other_checkout = Path(self.dir) / 'other-checkout'
        other_checkout.mkdir()
        with patch.object(st, 'REPO', str(other_checkout)):
            self.assertIsNone(launcher.saved_selection())
        from tools.approach_a import __main__ as cli
        default = other_checkout / 'default'
        default.mkdir()
        (default / 'manifest.json').write_text('{}')
        with patch.object(st, 'DEFAULT_ROOT', str(default)), \
                patch.object(cli.cmd_misc, 'status', return_value=0) as status:
            cli.main(['status'])
        self.assertEqual(status.call_args.args[0].root, str(default))

    def test_complete_manifest_exposes_only_explicit_local_export_action(self):
        self.add_profile()
        self.complete_cells()
        self.review_all()
        review.approve(self.store, 'ross')
        before = self.snapshot()
        with patch.object(launcher.publish, 'run') as export:
            result, output = self.run_launcher(['--data', self.dir], tty=False)
        self.assertEqual(result, 0)
        self.assertIn('Prepare a local accepted export', output)
        export.assert_not_called()
        self.assertEqual(before, self.snapshot())

    def test_completed_resume_validates_without_credentials_or_paid_prompt(self):
        self.add_profile()
        self.complete_cells()
        sources = self.store.load('sources.json')
        sources['entries']['E01']['version_or_update'] = 'Synthetic fixture source'
        self.store.save('sources.json', sources)
        self.review_all()
        review.approve(self.store, 'ross')
        self.store.log('research_started')
        self.store.log('validated')
        with patch.object(launcher.azure, 'connection', side_effect=AssertionError('must not load credentials')), \
                patch.object(launcher.azure, 'read_env_file', side_effect=AssertionError('must not read env file')), \
                patch.object(launcher.cmd_research, 'run') as research:
            result, output = self.run_launcher(['--data', self.dir, 'resume', '--draft', 'azure'], tty=False)
        self.assertEqual(result, 0)
        self.assertIn('Nothing automated is left to resume', output)
        self.assertNotIn('Paid drafting:', output)
        self.assertTrue(self.store.load('validation_report.json')['accepted'])
        research.assert_not_called()

    def test_resumed_paid_research_requires_confirmation_before_running(self):
        self.add_profile()
        conn = SimpleNamespace(deployment='fixture-resume-model', host='example.invalid', api_version='fixture-api')
        ledger = SimpleNamespace(lim={'max_requests_per_run': 3, 'max_cost_usd_per_run': 0.25}, prior=0)
        for decision in ('n', 'y'):
            with self.subTest(decision=decision):
                events = []
                def confirm(*args, **kwargs):
                    events.append('confirmation')
                    self.assertIn('fixture-resume-model', sys.stdout.getvalue())
                    self.assertIn('max_cost_usd_per_run', sys.stdout.getvalue())
                    return decision
                def research(store, args):
                    self.assertEqual(events, ['confirmation'])
                    events.append('research')
                    return 0
                before = self.snapshot()
                with patch.object(launcher.azure, 'connection', return_value=conn), \
                        patch.object(launcher.azure, 'Ledger', return_value=ledger), \
                        patch.object(launcher.cmd_blockers, 'ask', side_effect=confirm), \
                        patch.object(launcher.cmd_research, 'run', side_effect=research):
                    result, _ = self.run_launcher(['--data', self.dir, 'resume', '--draft', 'azure'])
                self.assertEqual(result, 0)
                self.assertEqual(events, ['confirmation', 'research'] if decision == 'y' else ['confirmation'])
                self.assertEqual(before, self.snapshot())

    def test_resume_no_draft_keeps_offline_path_without_credentials_or_prompt(self):
        self.add_profile()
        with patch.object(launcher.azure, 'connection', side_effect=AssertionError('no credentials needed')), \
                patch.object(launcher.cmd_research, 'run', return_value=0) as research:
            result, _ = self.run_launcher(['--data', self.dir, 'resume', '--no-draft', '--offline'])
        self.assertEqual(result, 0)
        self.assertEqual(research.call_args.args[1].draft, 'off')
        self.assertTrue(research.call_args.args[1].offline)

    def test_start_and_review_help_with_redirected_stdin_need_no_dataset(self):
        repo = Path(__file__).resolve().parents[3]
        missing = Path(self.dir) / 'missing-dataset'
        before = self.snapshot()
        for command, option in (('start', '--surface'), ('review', '--profile')):
            for flag in ('--help', '-h'):
                with self.subTest(command=command, flag=flag):
                    result = subprocess.run([str(repo / 'matrix'), '--data', str(missing), command, flag],
                                            cwd=repo, env=dict(os.environ), stdin=subprocess.DEVNULL,
                                            capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('usage:', result.stdout)
                    self.assertIn(option, result.stdout)
                    self.assertNotIn('Showing status only', result.stdout)
                    self.assertNotIn('No dataset', result.stdout)
        self.assertFalse(missing.exists())
        self.assertEqual(before, self.snapshot())

    def test_help_bypasses_missing_saved_selection_and_noninteractive_review_stays_read_only(self):
        launcher.selection_file().write_text(json.dumps({'path': str(self.checkout / 'missing')}))
        for command in ('start', 'review'):
            for flag in ('--help', '-h'):
                with patch('sys.stdin.isatty', return_value=False), contextlib.redirect_stdout(io.StringIO()), \
                        self.assertRaises(SystemExit) as exit:
                    launcher.main([command, flag])
                self.assertEqual(exit.exception.code, 0)
        self.add_profile()
        self.complete_cells()
        before = self.snapshot()
        result, output = self.run_launcher(['--data', self.dir, 'review'], tty=False)
        self.assertEqual(result, 0)
        self.assertIn('Showing status only', output)
        self.assertEqual(before, self.snapshot())
