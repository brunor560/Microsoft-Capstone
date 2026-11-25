"""Refresh checks and explicit application on disposable fixtures; no network/model."""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
from unittest.mock import patch

from tools.approach_a import fetch, pages, publish, refresh, review, sources, validate
from tools.approach_a.__main__ import main, parser
from tools.approach_a.tests.test_validation import Base

URL = 'https://docs.example.invalid/guide/'
QUOTE = 'Deny rules block unsafe commands.'
HTML = ('<html><head><title>Fixture docs</title></head><body><main><h1>Documentation</h1>'
        '<p>This page describes the product.</p><h2>CLI</h2><p>Documented terminal surface.</p>'
        '<h3>Permissions</h3><p>' + QUOTE + '</p><p>Available to Pro accounts on Linux only.</p>'
        '<h2>IDE</h2><p>Editor toolbar contains a blue panel.</p></main></body></html>')


class Refresh(Base):
    def setUp(self):
        super().setUp()
        self.reports = []
        self.add_profile()
        self.complete_cells()
        candidate_dir = Path(self.store.path('candidates', 'fixture'))
        candidate_dir.mkdir()
        self.docs = {'base_url': 'https://docs.example.invalid/', 'allowed_prefixes': ['https://docs.example.invalid/'],
                     'publisher': 'Fixture', 'surface_labels': {'CLI': 'cli', 'IDE': 'ide'}}
        (candidate_dir / 'candidate.json').write_text(json.dumps({'tool_key': 'fixture', 'tool': 'Fixture',
            'docs': self.docs, 'surfaces': {'cli': {'seed_pages': [URL]}}}))
        text = pages.to_text(HTML)
        self.rec = {'url': URL, 'publisher': 'Fixture', 'title': 'Fixture docs',
                    'sha256': refresh.st.sha256(text.encode()), 'access_date': '2026-11-09',
                    'version_or_update': 'Fixture snapshot', 'available_on': []}
        fetch.PageCache(self.store).put(sources.page_key(URL), text, HTML)
        index = sources.SourceIndex(self.store)
        index.data['entries'] = {}
        index.data['pages'] = {URL: self.rec}
        checked = pages.locate(text, 'CLI > Permissions', QUOTE, self.docs['surface_labels'], [])
        self.ref = index.evidence(URL, 'CLI > Permissions', QUOTE, checked, self.rec, 'Native restrictions')
        index.save()
        cells = self.store.load('cells.json')
        for cell in cells['cells'].values():
            cell.update(status='Built in', evidence_basis='documented_support', supported_scope='Native restrictions',
                        evidence_refs=[self.ref], gap_reason=None)
        self.store.save('cells.json', cells)
        self.review_all()
        review.approve(self.store, 'ross')
        self.assertTrue(validate.inspect(self.store)['accepted'])

    def tearDown(self):
        for directory in self.reports:
            shutil.rmtree(directory, ignore_errors=True)
        super().tearDown()

    def snapshot(self):
        return {str(p.relative_to(self.dir)): p.read_bytes() for p in Path(self.dir).rglob('*') if p.is_file()}

    def check(self, html=HTML, profiles=None, failure=None):
        response = (200, URL, html)
        with patch.object(refresh.fetch, 'fetch', side_effect=failure, return_value=response) as get:
            path, report = refresh.check(self.store, profiles)
        self.reports.append(path.parent)
        self.assertEqual(get.call_count, 1)  # 18 cells share one distinct URL.
        return path, report

    def test_unchanged_page_preserves_records_and_reviews_and_never_calls_model(self):
        before = self.snapshot()
        with patch('tools.approach_a.azure.Client.chat', side_effect=AssertionError('no model calls')):
            path, report = self.check()
        self.assertTrue(all(c['classification'] == refresh.UNCHANGED for c in report['cells']))
        self.assertEqual(before, self.snapshot())
        self.assertFalse(str(path).startswith(self.store.root))
        with self.assertRaisesRegex(ValueError, 'only affected'):
            refresh.apply(self.store, path, ['tool-cli/F07'])
        self.assertEqual(before, self.snapshot())

    def test_unrelated_explicit_other_surface_edit_preserves_current_review(self):
        before = self.snapshot()
        path, report = self.check(HTML.replace('blue panel', 'green panel'))
        self.assertTrue(all(c['classification'] == refresh.UNCHANGED for c in report['cells']))
        self.assertIn('verified_context', report['cells'][0]['reasons'][0])
        self.assertEqual(before, self.snapshot())
        self.assertTrue(all(not r['stale'] for r in review.current(self.store, self.store.load('cells.json')['cells']).values()))

    def test_surviving_quote_with_changed_scope_reopens_only_selected_cell_and_blocks_export(self):
        original_sources = self.store.load('sources.json')
        original_manifest = self.store.load('manifest.json')
        original_cells = self.store.load('cells.json')['cells']
        original_reviews = self.store.load('reviews.json')
        before = self.snapshot()
        path, report = self.check(HTML.replace('Pro accounts on Linux only', 'Enterprise accounts on Windows only'))
        self.assertTrue(all(c['classification'] == refresh.CHANGED for c in report['cells']))
        self.assertIn('context_changed', report['cells'][0]['reasons'][0])
        self.assertEqual(before, self.snapshot())
        result = refresh.apply(self.store, path, ['tool-cli/F07'])
        self.assertFalse(result['accepted'])
        self.assertIn('AUTHOR_MISSING', result['counts_by_code'])
        self.assertIn('CHALLENGE_MISSING', result['counts_by_code'])
        self.assertIn('REVIEW_STALE', result['counts_by_code'])
        cells = self.store.load('cells.json')['cells']
        updated = cells['tool-cli/F07']
        self.assertIsNone(updated['author'])
        self.assertEqual(updated['assessment_state'], 'drafted')
        self.assertEqual(updated['supported_scope'], original_cells['tool-cli/F07']['supported_scope'])
        self.assertNotEqual(updated['evidence_refs'], [self.ref])
        self.assertEqual(self.store.load('sources.json')['entries'][self.ref], original_sources['entries'][self.ref])
        self.assertEqual(self.store.load('reviews.json'), original_reviews)
        self.assertEqual(self.store.load('manifest.json'), original_manifest)
        self.assertEqual(Path(self.store.path('.cache', 'pages', sources.page_key(URL) + '.txt')).read_text(), pages.to_text(HTML))
        current = review.current(self.store, cells)
        self.assertTrue(current['tool-cli/F07']['stale'])
        for cid in cells:
            if cid != 'tool-cli/F07':
                self.assertEqual(cells[cid], original_cells[cid])
                self.assertFalse(current[cid]['stale'])
        with self.assertRaisesRegex(publish.PublishError, 'REVIEW_STALE'):
            publish.build(publish.snapshot(self.store))
        # A fresh snapshot is archived without overwriting the old URL cache.
        new_entry = self.store.load('sources.json')['entries'][updated['evidence_refs'][0]]
        self.assertIsNotNone(refresh.historical(self.store, new_entry))
        from tools.approach_a import packet
        self.assertIn('Windows only', packet.context(self.store, new_entry))
        self.assertNotIn('Linux only', packet.context(self.store, new_entry))

    def test_global_scope_qualifier_and_cross_surface_reference_are_not_ignored(self):
        for html in (HTML.replace('describes the product', 'describes the Enterprise-only product'),
                     HTML.replace('Editor toolbar contains a blue panel.', 'CLI now requires Enterprise.')):
            _, report = self.check(html)
            self.assertTrue(all(c['classification'] == refresh.CHANGED for c in report['cells']))

    def test_removed_passage_creates_unverified_new_evidence_and_keeps_finding(self):
        path, report = self.check(HTML.replace(QUOTE, 'That passage was removed.'))
        self.assertTrue(all(c['classification'] == refresh.CHANGED for c in report['cells']))
        self.assertIn('passage_changed', report['cells'][0]['reasons'][0])
        refresh.apply(self.store, path, ['tool-cli/F07'])
        cell = self.store.load('cells.json')['cells']['tool-cli/F07']
        self.assertEqual(cell['status'], 'Built in')
        self.assertIn('EVIDENCE_UNVERIFIED', validate.inspect(self.store)['counts_by_code'])

    def test_missing_historical_context_is_unknown_not_just_a_quote_match(self):
        cache = Path(self.store.path('.cache', 'pages'))
        shutil.rmtree(cache)
        before = self.snapshot()
        _, report = self.check(HTML.replace('blue panel', 'green panel'))
        self.assertTrue(all(c['classification'] == refresh.UNKNOWN for c in report['cells']))
        self.assertIn('historical_context', report['cells'][0]['reasons'][0])
        self.assertEqual(before, self.snapshot())

    def test_fetch_failure_and_gap_checks_remain_visible_without_rewriting_findings(self):
        before = self.snapshot()
        path, report = self.check(failure=OSError('fixture offline'))
        self.assertTrue(all(c['classification'] == refresh.UNKNOWN for c in report['cells']))
        self.assertIn('fetch_failed', report['cells'][0]['reasons'][0])
        self.assertEqual(before, self.snapshot())
        original = copy.deepcopy(self.store.load('cells.json')['cells']['tool-cli/F07'])
        refresh.apply(self.store, path, ['tool-cli/F07'])
        cell = self.store.load('cells.json')['cells']['tool-cli/F07']
        for field in ('status', 'supported_scope', 'evidence_refs', 'gap_reason'):
            self.assertEqual(cell[field], original[field])
        self.assertIn('fetch_failed', str(cell['documentation_refresh']))
        self.assertFalse(validate.inspect(self.store)['accepted'])

    def test_documentation_gap_is_reported_separately_even_with_identical_cited_page(self):
        data = self.store.load('cells.json')
        data['cells']['tool-cli/F07'].update(status='Not established from documentation',
            evidence_basis='documentation_gap', gap_reason='Broader documentation did not establish the feature')
        self.store.save('cells.json', data)
        review.record(self.store, 'tool-cli/F07', 'bruno', 'agree', 'Fixture gap review')
        before = self.snapshot()
        _, report = self.check()
        affected = next(c for c in report['cells'] if c['cell_id'] == 'tool-cli/F07')
        self.assertEqual(affected['classification'], refresh.UNKNOWN)
        self.assertIn('documentation_gap', '; '.join(affected['reasons']))
        self.assertEqual(before, self.snapshot())

    def test_edits_between_check_and_apply_reject_before_any_write(self):
        for name in ('manifest.json', 'cells.json', 'sources.json', 'reviews.json'):
            with self.subTest(name=name):
                original = Path(self.store.path(name)).read_bytes()
                path, _ = self.check(HTML.replace('Linux only', 'Windows only'))
                Path(self.store.path(name)).write_bytes(original + b'\n')
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, 'Dataset changed'):
                    refresh.apply(self.store, path, ['tool-cli/F07'])
                self.assertEqual(before, self.snapshot())
                Path(self.store.path(name)).write_bytes(original)

    def test_cli_apply_requires_selection_and_explicit_confirmation(self):
        path, _ = self.check(HTML.replace('Linux only', 'Windows only'))
        args = parser().parse_args(['refresh', '--apply', str(path)])
        before = self.snapshot()
        with patch('builtins.input', side_effect=['tool-cli/F07', 'n']), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(refresh.run(self.store, args), 0)
        self.assertEqual(before, self.snapshot())
        with patch('builtins.input', side_effect=['tool-cli/F07', 'y']), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(refresh.run(self.store, args), 0)
        self.assertIsNone(self.store.load('cells.json')['cells']['tool-cli/F07']['author'])

    def test_module_cli_check_interruption_is_read_only(self):
        before = self.snapshot()
        with patch.object(refresh.fetch, 'fetch', side_effect=KeyboardInterrupt), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--data', self.dir, 'refresh']), 130)
        self.assertEqual(before, self.snapshot())

    def test_profile_filter_and_unchanged_cells_remain_current_after_apply(self):
        self.add_profile(pid='other-cli')
        data = self.store.load('cells.json')
        for cid, cell in data['cells'].items():
            if cell['profile_id'] == 'other-cli':
                cell.update(copy.deepcopy(data['cells']['tool-cli/' + cell['feature_id']]), profile_id='other-cli')
        self.store.save('cells.json', data)
        self.review_all(pid='other-cli')
        review.approve(self.store, 'ross')
        before = copy.deepcopy(self.store.load('cells.json')['cells'])
        path, report = self.check(HTML.replace('Linux only', 'Windows only'), profiles=['tool-cli'])
        self.assertEqual(len(report['cells']), 18)
        refresh.apply(self.store, path, ['tool-cli/F07'])
        cells = self.store.load('cells.json')['cells']
        for cid in before:
            if cid != 'tool-cli/F07':
                self.assertEqual(cells[cid], before[cid])
                self.assertFalse(review.current(self.store, cells)[cid]['stale'])

    def test_reopened_cell_recovers_only_after_human_verification_and_independent_review(self):
        from tools.approach_a import challenge
        path, _ = self.check(HTML.replace('Linux only', 'Windows only'))
        refresh.apply(self.store, path, ['tool-cli/F07'])
        # Synthetic human correction and responsibility, never real assessment data.
        cells = self.store.load('cells.json')
        cells['cells']['tool-cli/F07']['supported_scope'] = 'Pro accounts on Windows only'
        self.store.save('cells.json', cells)
        challenge.run(self.store, lambda *args: None, 'fixture', only=['tool-cli'])
        self.assertFalse(validate.inspect(self.store)['accepted'])
        review.set_author(self.store, 'tool-cli/F07', 'ross')
        self.assertFalse(validate.inspect(self.store)['accepted'])
        review.record(self.store, 'tool-cli/F07', 'bruno', 'agree', 'Fixture re-review of changed scope')
        self.assertTrue(validate.inspect(self.store)['accepted'])
        self.assertTrue(publish.build(publish.snapshot(self.store))['release']['accepted'])

    def test_comparison_snapshot_edit_is_rejected_before_writing(self):
        path, report = self.check(HTML.replace('Linux only', 'Windows only'))
        artifact = path.parent / report['pages'][URL]['file']
        page = json.loads(artifact.read_text())
        page['html'] = HTML
        artifact.write_text(json.dumps(page))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'Comparison snapshot changed'):
            refresh.apply(self.store, path, ['tool-cli/F07'])
        self.assertEqual(before, self.snapshot())

    def test_shared_url_is_fetched_once_across_profiles(self):
        self.add_profile(pid='other-cli')
        data = self.store.load('cells.json')
        for cell in data['cells'].values():
            if cell['profile_id'] == 'other-cli':
                cell.update(status='Built in', evidence_basis='documented_support', evidence_refs=[self.ref])
        self.store.save('cells.json', data)
        before = self.snapshot()
        _, report = self.check()
        self.assertEqual(len(report['cells']), 36)
        self.assertEqual(before, self.snapshot())

    def test_availability_change_outside_main_text_is_not_a_hash_only_pass(self):
        badge = '<div>Available on:<div class="surface-chips-list"><span class="chip">IDE</span></div></div>'
        html = HTML.replace('<main>', badge + '<main>')
        self.assertEqual(pages.to_text(html), pages.to_text(HTML))
        _, report = self.check(html)
        self.assertTrue(all(c['classification'] == refresh.CHANGED for c in report['cells']))
        self.assertIn('availability badges changed', report['cells'][0]['reasons'][0])
