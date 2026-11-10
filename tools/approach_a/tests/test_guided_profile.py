"""Single-profile setup and research routing on disposable fixtures only."""
import contextlib
import copy
import datetime
import io
import json
from pathlib import Path
from unittest.mock import patch

from tools.approach_a import cmd_research, guided_profile as guided, model, publish, review
from tools.approach_a.__main__ import parser
from tools.approach_a.tests.test_validation import Base


class FixedDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2026, 11, 9)


class GuidedProfile(Base):
    def setUp(self):
        super().setUp()
        candidate = {
            'tool_key': 'fixture', 'tool': 'Fixture Tool', 'default_surface': 'cli',
            'docs': {'base_url': 'https://docs.example.invalid/', 'publisher': 'Fixture',
                     'allowed_prefixes': ['https://docs.example.invalid/'], 'surface_labels': {'Fixture CLI': 'cli'}},
            'surfaces': {'cli': {'profile_id': 'fixture-cli', 'label': 'Fixture CLI', 'category_tags': ['T2'],
                'version': {'value': '1.0', 'documentation_note': 'Old fixture snapshot'},
                'modes': ['interactive'], 'platforms': ['Linux'], 'account_and_tier': 'Free',
                'exclusions': ['IDE'], 'included_components': ['Native CLI'],
                'interface_and_execution_location': 'Local terminal', 'instructions_and_permissions': 'Manual approval',
                'model_support': 'Vendor routing', 'seed_pages': ['entry']}}}
        directory = Path(self.store.path('candidates', 'fixture'))
        (directory / 'briefs' / 'cli').mkdir(parents=True)
        (directory / 'candidate.json').write_text(json.dumps(candidate))
        # A prepared source finding exists for the old scope. Copying setup must
        # not apply it to fresh cells, even during offline research.
        (directory / 'briefs' / 'cli' / 'F01.json').write_text(json.dumps({
            'feature_id': 'F01', 'status': 'Built in', 'supported_scope': 'Old tier finding', 'evidence': []}))
        self.candidate = next(c for c in self.store.candidates() if c['tool_key'] == 'fixture')
        original = model.profile_from_candidate(self.candidate, 'cli')
        original.update(confirmed_by='ross', confirmed_at='2026-01-01T00:00:00Z', source_access_date='2026-01-01',
                        documentation_entry_points=['https://docs.example.invalid/copied-entry'])
        model.add_profile(self.store, original, 'ross')
        self.complete_cells(pid='fixture-cli')
        sources = self.store.load('sources.json')
        sources['entries']['E01']['version_or_update'] = 'Synthetic source'
        self.store.save('sources.json', sources)
        self.review_all(pid='fixture-cli')
        review.approve(self.store, 'ross')

    def snapshot(self):
        return {str(p): p.read_bytes() for p in Path(self.dir).rglob('*') if p.is_file()}

    def run_setup(self, answers):
        output = io.StringIO()
        with patch('builtins.input', side_effect=answers), contextlib.redirect_stdout(output):
            try:
                result = guided.run(self.store, parser().parse_args(['start', '--no-draft']))
            except guided.prompts.Quit:
                result = None
        return result, output.getvalue()

    def create(self, tier='Pro', platform=None, version='2.0'):
        answers = ['copy', 'fixture-cli', tier]
        if platform:
            answers += ['platforms', platform]
        answers += ['version', version, 'source_access_date', '2026-11-09', 'confirm', 'ross', 'y']
        return self.run_setup(answers)

    def test_copy_and_edit_creates_fresh_variant_without_copying_decisions(self):
        original_manifest = self.store.load('manifest.json')
        original_cells = copy.deepcopy(self.store.load('cells.json')['cells'])
        original_sources = self.store.load('sources.json')
        original_reviews = self.store.load('reviews.json')
        pid, output = self.create(platform='Windows')
        manifest = self.store.load('manifest.json')
        variant = manifest['profiles'][-1]
        self.assertEqual(manifest['profiles'][0], original_manifest['profiles'][0])
        self.assertEqual(manifest['manifest_version'], original_manifest['manifest_version'] + 1)
        self.assertIsNone(manifest['approval'])
        self.assertNotEqual(pid, 'fixture-cli')
        self.assertEqual(variant['tool_key'], 'fixture')
        self.assertEqual(variant['surface'], 'cli')
        self.assertEqual(variant['platforms'], ['Windows'])
        self.assertEqual(variant['modes'], ['interactive'])
        self.assertEqual(variant['exclusions'], ['IDE'])
        self.assertEqual(variant['documentation_entry_points'], ['https://docs.example.invalid/copied-entry'])
        self.assertEqual(variant['version']['value'], '2.0')
        self.assertEqual(variant['source_access_date'], '2026-11-09')
        self.assertIn('INHERITED setup', output)
        self.assertIn('EDITED', output)
        cells = self.store.load('cells.json')['cells']
        for cid, cell in original_cells.items():
            self.assertEqual(cells[cid], cell)
        fresh = [c for c in cells.values() if c['profile_id'] == pid]
        self.assertEqual(len(fresh), 18)
        for cell in fresh:
            self.assertEqual(cell['assessment_state'], 'pending')
            self.assertIsNone(cell['author'])
            self.assertIsNone(cell['drafted_by'])
            self.assertEqual(cell['evidence_refs'], [])
        self.assertEqual(self.store.load('sources.json'), original_sources)
        self.assertEqual(self.store.load('reviews.json'), original_reviews)
        self.assertFalse(review.current(self.store, cells)['fixture-cli/F01']['stale'])

    def test_cancel_and_declined_confirmation_do_not_change_files(self):
        for answers in (['copy', 'fixture-cli', 'Pro', 'q'],
                        ['copy', 'fixture-cli', 'Pro', 'version', '2.0', 'source_access_date', '2026-11-09',
                         'confirm', 'ross', 'n']):
            before = self.snapshot()
            pid, _ = self.run_setup(answers)
            self.assertIsNone(pid)
            self.assertEqual(before, self.snapshot())

    def test_required_placeholders_block_confirmation_and_old_dates_are_not_inherited(self):
        before = self.snapshot()
        pid, output = self.run_setup(['copy', 'fixture-cli', 'Proposed: TBD', 'confirm', 'q'])
        self.assertIsNone(pid)
        self.assertIn('Confirmation blocked:', output)
        self.assertIn('version [NEEDS INPUT]', output)
        self.assertIn('source_access_date [NEEDS INPUT]', output)
        self.assertIn('account_and_tier [NEEDS INPUT]', output)
        self.assertEqual(before, self.snapshot())
        p = guided.proposal(self.store.load('manifest.json')['profiles'][0], self.candidate, copied=True)
        self.assertIsNone(p['source_access_date'])
        self.assertIsNone(p['version']['value'])
        self.assertEqual(p['version']['documentation_note'], '')

    def test_matching_boundary_offers_existing_profile_without_writes(self):
        before = self.snapshot()
        pid, output = self.run_setup(['copy', 'fixture-cli', 'Free', 'version', '1.0',
                                     'source_access_date', '2026-11-09', 'confirm', 'y'])
        self.assertIsNone(pid)
        self.assertIn('Existing profile fixture-cli:', output)
        self.assertIn('research pending/drafted=0', output)
        self.assertIn('remaining reviews=0', output)
        self.assertEqual(before, self.snapshot())

    def test_distinct_tier_and_platform_variants_keep_ids_review_and_export_separate(self):
        first, _ = self.create(tier='Pro', platform='Windows', version='1.0')
        second, _ = self.create(tier='Team', platform='Windows', version='1.0')
        third, _ = self.create(tier='Pro', platform='Linux', version='1.0')
        self.assertEqual(len({'fixture-cli', first, second, third}), 4)
        for pid in (first, second, third):
            sources = self.store.load('sources.json')
            self.complete_cells(pid=pid)
            self.store.save('sources.json', sources)
            self.review_all(pid=pid)
        review.approve(self.store, 'ross')
        payload = publish.build(publish.snapshot(self.store))
        self.assertEqual(len(payload['profiles']), 4)
        self.assertEqual(len(payload['cells']), 72)
        self.assertEqual({p['id'] for p in payload['profiles']}, {'fixture-cli', first, second, third})
        self.assertEqual(len(review.current(self.store, self.store.load('cells.json')['cells'])), 72)

    def test_variant_research_uses_edited_entrypoints_and_only_its_own_fresh_cells(self):
        answers = ['copy', 'fixture-cli', 'Pro', 'documentation_entry_points',
                   'https://docs.example.invalid/new-entry', 'version', '2.0',
                   'source_access_date', '2026-11-09', 'confirm', 'ross', 'y']
        pid, _ = self.run_setup(answers)
        originals = copy.deepcopy({k: c for k, c in self.store.load('cells.json')['cells'].items() if c['profile_id'] == 'fixture-cli'})
        args = parser().parse_args(['research', '--profile', pid, '--offline', '--no-draft'])
        def discover(index, docs, seeds, *unused):
            self.assertEqual(seeds, ['https://docs.example.invalid/new-entry'])
            self.assertEqual(docs['base_url'], 'https://docs.example.invalid/')
            return seeds, 0
        with patch.object(cmd_research.src, 'discover', side_effect=discover), \
                patch('tools.approach_a.research.load_briefs', side_effect=AssertionError('must not copy old briefs')), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cmd_research.run(self.store, args), 0)
        cells = self.store.load('cells.json')['cells']
        self.assertTrue(all(c['assessment_state'] == 'pending' for c in cells.values() if c['profile_id'] == pid))
        self.assertEqual({k: c for k, c in cells.items() if c['profile_id'] == 'fixture-cli'}, originals)

    def test_prepared_candidate_detects_matching_boundary_despite_new_access_date(self):
        before = self.snapshot()
        pid, output = self.run_setup(['prepared', 'fixture', '', 'Free', 'version', '1.0',
                                     'source_access_date', '2026-11-09', 'confirm', 'n'])
        self.assertIsNone(pid)
        self.assertIn('Existing profile fixture-cli', output)
        self.assertEqual(before, self.snapshot())

    def test_cancel_before_initializing_a_dataset_writes_nothing(self):
        from tools.approach_a import store as st
        target = st.Store(str(Path(self.dir) / 'not-created'))
        before = self.snapshot()
        with patch('builtins.input', side_effect=['prepared', 'antigravity', '', 'Individual', 'q']), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(guided.prompts.Quit):
            guided.run(target, parser().parse_args(['start', '--no-draft']))
        self.assertFalse(Path(target.root).exists())
        self.assertEqual(before, self.snapshot())

    def test_new_tool_path_retains_existing_command_without_creating_a_profile(self):
        before = self.snapshot()
        pid, output = self.run_setup(['new'])
        self.assertIsNone(pid)
        self.assertIn('./matrix new', output)
        self.assertEqual(before, self.snapshot())

    def test_duplicate_list_order_and_case_are_not_new_boundaries(self):
        original = self.store.load('manifest.json')['profiles'][0]
        p = copy.deepcopy(original)
        p['modes'] = ['INTERACTIVE', 'interactive']
        p['platforms'] = [' linux ']
        p['account_and_tier'] = 'FREE'
        self.assertEqual(guided.duplicate(p, [original]), original)

    def test_variant_drafting_receives_its_exact_tier_platform_and_modes(self):
        from tools.approach_a import drafting
        pid, _ = self.create(tier='Team', platform='Windows', version='1.0')
        profile = next(p for p in self.store.load('manifest.json')['profiles'] if p['id'] == pid)
        message = drafting.messages(self.store.catalog()['features'][0], profile, [
            {'page': 'https://docs.example.invalid/entry', 'section': 'CLI', 'text': 'Fixture official excerpt'}])[-1]['content']
        self.assertIn('Account/tier: Team', message)
        self.assertIn('Platforms: Windows', message)
        self.assertIn('Modes: interactive', message)
        self.assertIn('Fixture official excerpt', message)

    def test_access_date_accepts_yesterday_and_today_but_rejects_tomorrow(self):
        profile = copy.deepcopy(self.store.load('manifest.json')['profiles'][0])
        with patch.object(guided.datetime, 'date', FixedDate):
            for date in ('2026-11-08', '2026-11-09'):
                with self.subTest(date=date):
                    profile['source_access_date'] = date
                    self.assertEqual(guided.problems(profile, self.candidate), [])
            profile['source_access_date'] = '2026-11-10'
            self.assertIn('source_access_date (cannot be later than today)', guided.problems(profile, self.candidate))
            for date in ('20261109', '2026-02-30'):
                with self.subTest(date=date):
                    profile['source_access_date'] = date
                    self.assertIn('source_access_date (YYYY-MM-DD, actually reviewed)', guided.problems(profile, self.candidate))

    def test_future_date_blocks_confirmation_without_writes_until_corrected(self):
        answers = ['copy', 'fixture-cli', 'Pro', 'version', '2.0',
                   'source_access_date', '2026-11-10', 'confirm']
        before = self.snapshot()
        with patch.object(guided.datetime, 'date', FixedDate):
            pid, output = self.run_setup([*answers, 'q'])
            self.assertIsNone(pid)
            self.assertIn('source_access_date [NEEDS INPUT]', output)
            self.assertIn('Confirmation blocked: source_access_date (cannot be later than today)', output)
            self.assertEqual(before, self.snapshot())
            pid, _ = self.run_setup([*answers, 'source_access_date', '2026-11-09', 'confirm', 'ross', 'y'])
        self.assertIsNotNone(pid)
        profile = self.store.load('manifest.json')['profiles'][-1]
        self.assertEqual(profile['source_access_date'], '2026-11-09')
