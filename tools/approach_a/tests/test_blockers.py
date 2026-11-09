"""Interactive blocker decisions on disposable fixtures; never use real human records."""
import contextlib
import io
from pathlib import Path
from unittest.mock import patch

from tools.approach_a import cmd_blockers, review
from tools.approach_a import store as st
from tools.approach_a.__main__ import main, parser
from tools.approach_a.tests.test_validation import Base


class BlockerWalkthrough(Base):
    def prepared(self, author=None, confirmed=True):
        p = self.add_profile(who='ross' if confirmed else None)
        self.complete_cells(author=author)
        sources = self.store.load('sources.json')
        sources['entries']['E01']['version_or_update'] = 'Synthetic fixture source'
        self.store.save('sources.json', sources)
        return p

    def snapshot(self):
        return {str(p.relative_to(self.dir)): p.read_bytes() for p in Path(self.dir).rglob('*') if p.is_file()}

    def walk(self, responses, *options):
        output = io.StringIO()
        args = parser().parse_args(['blockers', *options])
        with patch('builtins.input', side_effect=responses), contextlib.redirect_stdout(output):
            result = cmd_blockers.run(self.store, args)
        self.assertEqual(result, 0)
        return output.getvalue()

    def test_list_uses_live_data_and_does_not_write(self):
        self.prepared()
        self.store.save('validation_report.json', {'accepted': True, 'issues': []})
        before = self.snapshot()
        output = self.walk([], '--list')
        self.assertIn('AUTHOR_MISSING', output)
        self.assertIn('REVIEW_MISSING', output)
        self.assertEqual(before, self.snapshot())

    def test_menu_profile_and_type_selection_then_skip_is_read_only(self):
        self.prepared()
        before = self.snapshot()
        output = self.walk(['tool-cli', 'AUTHOR_MISSING', *(['s'] * 18), 'q'])
        self.assertIn('F01', output)
        self.assertIn('F18', output)
        self.assertIn('https://example.invalid/docs/', output)
        self.assertEqual(before, self.snapshot())

    def test_eof_and_enter_at_menu_exit_without_writes(self):
        self.prepared()
        before = self.snapshot()
        self.walk([EOFError()])
        self.walk([''])
        self.assertEqual(before, self.snapshot())

    def test_author_saves_one_cell_and_refreshes_the_report(self):
        self.prepared()
        self.walk(['a', *(['s'] * 17), 'q'], '--profile', 'tool-cli', '--code', 'AUTHOR_MISSING', '--operator', 'ross')
        cells = self.store.load('cells.json')['cells']
        self.assertEqual(cells['tool-cli/F01']['author'], 'ross')
        self.assertEqual(sum(c.get('author') is not None for c in cells.values()), 1)
        self.assertEqual(self.store.load('validation_report.json')['counts_by_code']['AUTHOR_MISSING'], 17)
        self.assertTrue(self.store.exists('out/matrix.md'))

    def test_self_review_cannot_create_a_review(self):
        self.prepared(author='ross')
        output = self.walk(['a', *(['s'] * 18), 'q'], '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'ross')
        self.assertIn('Self-review', output)
        self.assertEqual(self.store.load('reviews.json')['reviews'], [])

    def test_review_requires_note_and_records_current_hash(self):
        self.prepared(author='ross')
        self.walk(['a', '', 'a', 'Checked source, platform and gap explanation', *(['s'] * 17), 'q'],
                  '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'bruno')
        records = self.store.load('reviews.json')['reviews']
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['reviewer'], 'bruno')
        self.assertEqual(records[0]['cell_sha256'], st.cell_hash(self.store.load('cells.json')['cells']['tool-cli/F01']))
        self.assertEqual(self.store.load('validation_report.json')['counts_by_code']['REVIEW_MISSING'], 17)
        data = self.store.load('cells.json'); data['cells']['tool-cli/F01']['supported_scope'] = 'Changed after review'
        self.store.save('cells.json', data)
        self.assertIn('REVIEW_STALE', self.walk([], '--list'))

    def test_disagreement_stays_open_and_is_not_counted_as_acceptance(self):
        self.prepared(author='ross')
        self.walk(['d', 'The cited passage does not cover this platform', 'unresolved', *(['s'] * 17), 'q'],
                  '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'bruno')
        record = self.store.load('reviews.json')['reviews'][0]
        self.assertEqual(record['decision'], 'disagree')
        self.assertIsNone(record['disposition'])
        self.assertIn('DISAGREEMENT_OPEN', self.store.load('validation_report.json')['counts_by_code'])

    def test_boundary_confirmation_uses_current_profile_not_old_candidate(self):
        self.prepared(author='ross', confirmed=False)
        m = self.store.load('manifest.json');m['profiles'][0]['exclusions'].append('User-added exclusion')
        self.store.save('manifest.json', m)
        self.walk(['c', 'Agreed fixture tier', '', '', 'y', 'q'], '--profile', 'tool-cli',
                  '--code', 'BOUNDARY_UNCONFIRMED', '--operator', 'ross')
        p = self.store.load('manifest.json')['profiles'][0]
        self.assertIn('User-added exclusion', p['exclusions'])
        self.assertEqual(p['account_and_tier'], 'Agreed fixture tier')
        self.assertEqual(p['source_access_date'], '2026-10-21')
        self.assertEqual(p['confirmed_by'], 'ross')
        self.assertTrue(all(c['author'] is None for c in self.store.load('cells.json')['cells'].values()))
        self.assertNotIn('BOUNDARY_UNCONFIRMED', self.store.load('validation_report.json')['counts_by_code'])

    def test_manifest_approval_still_enforces_role_and_confirmed_boundaries(self):
        self.prepared(confirmed=False)
        before = self.snapshot()
        output = self.walk([':manifest', 'APPROVAL_MISSING', 'a', 's', 'q'], '--operator', 'ross')
        self.assertIn('no confirmed boundary', output)
        self.assertIsNone(self.store.load('manifest.json')['approval'])
        self.assertEqual(before, self.snapshot())
        self.walk([':manifest', 'APPROVAL_MISSING', 'a', 's', 'q'], '--operator', 'bruno')
        self.assertIsNone(self.store.load('manifest.json')['approval'])

    def test_approval_is_explicit_and_does_not_accept_incomplete_cells(self):
        self.prepared()
        self.walk([':manifest', 'APPROVAL_MISSING', 'a', 'q'], '--operator', 'ross')
        self.assertEqual(self.store.load('manifest.json')['approval']['approver'], 'ross')
        self.assertFalse(self.store.load('validation_report.json')['accepted'])

    def test_generic_data_blocker_is_not_silently_fixed(self):
        self.add_profile()
        before = self.snapshot()
        output = self.walk([*(['s'] * 18), 'q'], '--profile', 'tool-cli', '--code', 'CELL_PENDING')
        self.assertIn('does not invent research', output)
        self.assertEqual(before, self.snapshot())

    def test_changed_cell_cannot_receive_an_unseen_review(self):
        self.prepared(author='ross')
        walker = cmd_blockers.Walker(self.store, 'bruno')
        before = walker.fingerprint('tool-cli/F01')
        data = self.store.load('cells.json');data['cells']['tool-cli/F01']['supported_scope'] = 'Concurrent edit'
        self.store.save('cells.json', data)
        with patch('builtins.input', return_value='Verified before the concurrent change'):
            with self.assertRaisesRegex(ValueError, 'changed while it was displayed'):
                walker.decide('REVIEW_MISSING', 'tool-cli/F01', 'a', before)
        self.assertFalse(self.store.load('reviews.json')['reviews'])

    def test_entrypoint_honors_selected_dataset(self):
        self.prepared()
        before = self.snapshot()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--data', self.dir, 'blockers', '--list']), 0)
        self.assertEqual(before, self.snapshot())

    def test_profile_filter_never_authors_other_profiles(self):
        self.prepared()
        self.add_profile(pid='other-cli')
        self.complete_cells(pid='other-cli', author=None)
        sources = self.store.load('sources.json');sources['entries']['E01']['version_or_update'] = 'Fixture'
        self.store.save('sources.json', sources)
        self.walk(['a', *(['s'] * 17), 'q'], '--profile', 'tool-cli', '--code', 'AUTHOR_MISSING', '--operator', 'ross')
        other = [c for c in self.store.load('cells.json')['cells'].values() if c['profile_id'] == 'other-cli']
        self.assertEqual(len(other), 18)
        self.assertTrue(all(c['author'] is None for c in other))

    def test_changed_source_cannot_receive_an_unseen_review(self):
        self.prepared(author='ross')
        walker = cmd_blockers.Walker(self.store, 'bruno')
        before = walker.fingerprint('tool-cli/F01')
        sources = self.store.load('sources.json');sources['entries']['E01']['quote'] = 'Concurrent source correction'
        self.store.save('sources.json', sources)
        with patch('builtins.input', return_value='Checked the previously displayed quote'):
            with self.assertRaisesRegex(ValueError, 'changed while it was displayed'):
                walker.decide('REVIEW_MISSING', 'tool-cli/F01', 'a', before)
        self.assertFalse(self.store.load('reviews.json')['reviews'])

    def test_ctrl_c_while_browsing_does_not_write(self):
        self.prepared()
        before = self.snapshot()
        args = parser().parse_args(['blockers'])
        with patch('builtins.input', side_effect=KeyboardInterrupt()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cmd_blockers.run(self.store, args), 130)
        self.assertEqual(before, self.snapshot())

    def test_accepted_dataset_needs_no_prompts(self):
        self.prepared(author='ross')
        self.review_all()
        review.approve(self.store, 'ross')
        before = self.snapshot()
        output = self.walk([])
        self.assertIn('No blocking findings remain', output)
        self.assertEqual(before, self.snapshot())

    def test_profile_wide_author_preserves_existing_author_and_other_profile(self):
        self.prepared()
        data = self.store.load('cells.json'); data['cells']['tool-cli/F01']['author'] = 'bruno'
        self.store.save('cells.json', data)
        self.add_profile(pid='other-cli')
        self.complete_cells(pid='other-cli', author=None)
        sources = self.store.load('sources.json'); sources['entries']['E01']['version_or_update'] = 'Fixture'
        self.store.save('sources.json', sources)
        output = self.walk(['p', 'y', 'q'], '--profile', 'tool-cli', '--code', 'AUTHOR_MISSING', '--operator', 'ross')
        cells = self.store.load('cells.json')['cells']
        self.assertEqual(cells['tool-cli/F01']['author'], 'bruno')
        self.assertEqual(sum(c['author'] == 'ross' for c in cells.values()), 17)
        self.assertTrue(all(c['author'] is None for c in cells.values() if c['profile_id'] == 'other-cli'))
        self.assertIn('Author already recorded', output)

    def test_declining_profile_wide_author_changes_nothing(self):
        self.prepared()
        before = self.snapshot()
        self.walk(['p', 'n', 'q'], '--profile', 'tool-cli', '--code', 'AUTHOR_MISSING', '--operator', 'ross')
        self.assertEqual(before, self.snapshot())

    def test_profile_wide_review_records_each_cell_hash_and_shared_note(self):
        self.prepared(author='ross')
        self.walk(['p', 'agree', 'Verified every listed cell against its sources', 'y', 'q'],
                  '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'bruno')
        records = self.store.load('reviews.json')['reviews']
        self.assertEqual(len(records), 18)
        cells = self.store.load('cells.json')['cells']
        for record in records:
            self.assertEqual(record['reviewer'], 'bruno')
            self.assertEqual(record['decision'], 'agree')
            self.assertEqual(record['cell_sha256'], st.cell_hash(cells[record['cell_id']]))
        self.assertNotIn('REVIEW_MISSING', self.store.load('validation_report.json')['counts_by_code'])

    def test_profile_wide_review_skips_self_missing_author_and_current_review(self):
        self.prepared(author='ross')
        data = self.store.load('cells.json')
        data['cells']['tool-cli/F01']['author'] = 'bruno'
        data['cells']['tool-cli/F02']['author'] = None
        self.store.save('cells.json', data)
        review.record(self.store, 'tool-cli/F03', 'kapil', 'agree', 'Already checked')
        original = self.store.load('reviews.json')['reviews'][0]
        output = self.walk(['p', 'agree', 'Checked all eligible listed cells', 'y', 'q'],
                          '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'bruno')
        records = self.store.load('reviews.json')['reviews']
        self.assertEqual(len(records), 16)
        self.assertEqual(records[0], original)
        self.assertTrue(all(r['cell_id'] not in ['tool-cli/F01', 'tool-cli/F02'] for r in records))
        self.assertIn('Self-review is not independent', output)
        self.assertIn('Needs an author first', output)
        self.assertIn('Current review already recorded', output)

    def test_profile_wide_disagreement_leaves_every_cell_blocked(self):
        self.prepared(author='ross')
        self.walk(['p', 'disagree', 'All listed findings need scope corrections', 'unresolved', 'y', 'q'],
                  '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'bruno')
        self.assertEqual(self.store.load('validation_report.json')['counts_by_code']['DISAGREEMENT_OPEN'], 18)
        self.assertTrue(all(r['decision'] == 'disagree' for r in self.store.load('reviews.json')['reviews']))

    def test_profile_wide_review_requires_note(self):
        self.prepared(author='ross')
        before = self.snapshot()
        self.walk(['p', 'agree', '', 'q'], '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'bruno')
        self.assertEqual(before, self.snapshot())

    def test_profile_wide_review_all_self_authored_changes_nothing(self):
        self.prepared(author='ross')
        before = self.snapshot()
        output = self.walk(['p', 'q'], '--profile', 'tool-cli', '--code', 'REVIEW_MISSING', '--operator', 'ross')
        self.assertIn('No eligible cells', output)
        self.assertEqual(before, self.snapshot())

    def test_profile_wide_confirmation_rechecks_every_cell_before_any_write(self):
        self.prepared(author='ross')
        walker = cmd_blockers.Walker(self.store, 'bruno')
        answers = iter(['agree', 'Checked all displayed cells'])
        def answer(prompt):
            if prompt.startswith('Record '):
                data = self.store.load('cells.json')
                data['cells']['tool-cli/F18']['supported_scope'] = 'Changed during batch confirmation'
                self.store.save('cells.json', data)
                return 'y'
            return next(answers)
        with patch('builtins.input', side_effect=answer), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'changed while it was displayed'):
                walker.apply_profile('tool-cli', 'REVIEW_MISSING')
        self.assertFalse(self.store.load('reviews.json')['reviews'])
