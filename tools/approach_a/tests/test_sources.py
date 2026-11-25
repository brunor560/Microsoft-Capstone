"""Immutable evidence registration on disposable assessment fixtures."""
import copy

from tools.approach_a import research, review, sources, validate
from tools.approach_a.tests.test_validation import Base


class ImmutableEvidence(Base):
    def setUp(self):
        super().setUp()
        self.add_profile()
        self.complete_cells()
        self.url = 'https://example.invalid/docs/'
        self.quote = 'fixture'
        self.check = {'status': 'verified', 'section_path': ['Fixture'], 'surface': 'cli'}
        self.page = {'publisher': 'Fixture vendor', 'title': 'Fixture documentation',
                     'sha256': 'a' * 64, 'access_date': '2026-10-21', 'version_or_update': 'Fixture v1'}
        index = sources.SourceIndex(self.store)
        index.data['entries'] = {}
        self.original_id = self.register(index, self.page)
        index.save()
        self.review_all()

    def register(self, index, page, check=None, claim='Fixture claim'):
        return index.evidence(self.url, 'Fixture', self.quote, check or self.check, page, claim)

    def test_variant_different_snapshot_gets_new_id_and_original_review_stays_current(self):
        original_cells = copy.deepcopy(self.store.load('cells.json')['cells'])
        original_reviews = self.store.load('reviews.json')
        original_entry = copy.deepcopy(self.store.load('sources.json')['entries'][self.original_id])
        self.add_profile(pid='variant-cli')
        index = sources.SourceIndex(self.store)
        new_page = dict(self.page, sha256='b' * 64, access_date='2026-11-09', version_or_update='Fixture v2')
        new_id = self.register(index, new_page)
        index.save()
        self.assertNotEqual(new_id, self.original_id)
        data = self.store.load('cells.json')
        research.apply_brief(data['cells']['variant-cli/F01'], {
            'status': 'Built in', 'supported_scope': 'New variant finding'},
            [new_id], [], 'variant-cli', 'fixture-operator')
        self.store.save('cells.json', data)
        entries = self.store.load('sources.json')['entries']
        self.assertEqual(entries[self.original_id], original_entry)
        self.assertEqual(entries[new_id]['page_sha256'], 'b' * 64)
        self.assertEqual(data['cells']['variant-cli/F01']['evidence_refs'], [new_id])
        for cid, original in original_cells.items():
            self.assertEqual(data['cells'][cid], original)
        self.assertEqual(self.store.load('reviews.json'), original_reviews)
        current = review.current(self.store, data['cells'])
        self.assertTrue(all(not r['stale'] for r in current.values()))
        self.assertNotIn('REVIEW_STALE', validate.inspect(self.store)['counts_by_code'])
        # Existing integrity checks still catch an actual edit to reviewed evidence.
        entries[self.original_id]['quote'] = 'Changed reviewed evidence'
        changed = self.store.load('sources.json')
        changed['entries'] = entries
        self.store.save('sources.json', changed)
        self.assertTrue(review.current(self.store, data['cells'])['tool-cli/F01']['stale'])

    def test_identical_snapshot_reuses_existing_id_without_changes(self):
        before = self.store.load('sources.json')
        index = sources.SourceIndex(self.store)
        self.assertEqual(self.register(index, copy.deepcopy(self.page)), self.original_id)
        index.save()
        self.assertEqual(self.store.load('sources.json'), before)

    def test_each_recorded_provenance_difference_creates_new_immutable_entry(self):
        cases = [dict(self.page, **{key: value}) for key, value in (
            ('sha256', 'b' * 64), ('access_date', '2026-11-09'),
            ('publisher', 'Changed vendor'), ('title', 'Changed title'), ('version_or_update', 'Fixture v2'))]
        for page in cases:
            with self.subTest(page=page):
                index = sources.SourceIndex(self.store)
                before = copy.deepcopy(index.data['entries'])
                new_id = self.register(index, page)
                self.assertNotEqual(new_id, self.original_id)
                self.assertEqual({key: index.data['entries'][key] for key in before}, before)
                self.assertEqual(self.register(index, page), new_id)
        index = sources.SourceIndex(self.store)
        self.assertNotEqual(self.register(index, self.page, dict(self.check, surface='ide')), self.original_id)
        self.assertNotEqual(self.register(index, self.page, claim='Different claim summary'), self.original_id)

    def test_new_id_does_not_overwrite_an_entry_when_ids_have_gaps(self):
        index = sources.SourceIndex(self.store)
        index.data['entries']['E03'] = dict(index.data['entries'][self.original_id], id='E03', quote='Other quote')
        before = copy.deepcopy(index.data['entries'])
        new_id = self.register(index, dict(self.page, access_date='2026-11-09'))
        self.assertEqual(new_id, 'E04')
        self.assertEqual({key: index.data['entries'][key] for key in before}, before)
