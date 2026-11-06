"""Publication export tests on synthetic datasets (no network).

Run from the repository root:  python3 -m unittest discover -s tools/approach_a/tests -t .
Fixtures are test data, not findings.
"""
import json
import re

from tools.approach_a import publish, pubcheck, review
from tools.approach_a.tests.test_validation import Base

CID = 'tool-cli/F07'


class Fixture(Base):
    def accepted(self):
        self.add_profile()
        review.approve(self.store, 'ross')
        self.complete_cells()
        self.review_all()

    def export(self, mode='accepted'):
        return publish.build(publish.snapshot(self.store), mode, source_commit='a' * 40, source_dirty=False)

    def cell(self, payload, fid='F07', pid='tool-cli'):
        return next(c for c in payload['cells'] if c['feature_id'] == fid and c['profile_id'] == pid)

    def mutate(self, fn):
        data = self.store.load('cells.json')
        fn(data['cells'][CID])
        self.store.save('cells.json', data)


class AcceptedExport(Fixture):
    def test_valid_dataset_exports_and_passes_checks(self):
        self.accepted()
        p = self.export()
        self.assertEqual(pubcheck.check_payload(p), [])
        self.assertEqual(pubcheck.check_public_file(p, self.store.people()), [])
        self.assertEqual(len(p['cells']), 18)
        self.assertEqual(p['release']['publication_mode'], 'accepted')
        self.assertTrue(p['release']['accepted'])

    def test_no_names_or_roster_ids_in_payload(self):
        self.accepted()
        p = self.export()
        self.assertEqual(pubcheck.leaks(p, self.store.people()), [])
        text = json.dumps(p)
        for ident in ('ross', 'bruno', 'joseph', 'kapil', 'volenec', 'rocha', 'bressani', 'srikanth'):
            # whole words only: "ross" is also part of "across" in catalog text
            self.assertIsNone(re.search(r'(?<!\w)%s(?!\w)' % ident, text, re.I), ident)
        c = self.cell(p)
        self.assertEqual(c['author'], {'recorded': True})
        self.assertTrue(c['review']['independent'])
        self.assertNotIn('reviewer', c['review'])
        self.assertNotIn('approver', p['release']['approval'])

    def test_identity_in_payload_is_detected(self):
        self.accepted()
        p = self.export()
        p['cells'][0]['limitations'] = 'reviewed by Bruno'
        self.assertTrue(pubcheck.leaks(p, self.store.people()))
        p = self.export()
        p['cells'][0]['review']['reviewer'] = 'x'
        self.assertTrue(any('identity field' in b for b in pubcheck.check_payload(p)))

    def test_rejections_write_nothing(self):
        def unapprove():
            m = self.store.load('manifest.json')
            m['approval'] = None
            self.store.save('manifest.json', m)
        cases = {
            'unapproved manifest': unapprove,
            'pending cell': lambda: self.mutate(lambda c: c.update(assessment_state='pending')),
            'dangling evidence': lambda: self.mutate(lambda c: c.update(evidence_refs=['E99'])),
            'stale review': lambda: self.mutate(lambda c: c.update(required_setup='changed after review')),
            'self-review': lambda: self.mutate(lambda c: c.update(author='bruno')),
        }
        for name, change in cases.items():
            with self.subTest(name):
                self.setUp()
                self.accepted()
                change()
                with self.assertRaises(publish.PublishError):
                    self.export()

    def test_open_disagreement_is_rejected(self):
        self.accepted()
        review.record(self.store, CID, 'kapil', 'disagree', 'Quote does not support status', 'escalated')
        with self.assertRaises(publish.PublishError):
            self.export()

    def test_unverified_evidence_is_rejected(self):
        self.accepted()
        src = self.store.load('sources.json')
        src['entries']['E01']['check'] = 'not_found'
        self.store.save('sources.json', src)
        with self.assertRaises(publish.PublishError):
            self.export()

    def test_reviewed_not_established_keeps_gap_reason(self):
        self.accepted()
        c = self.cell(self.export())
        self.assertEqual(c['status'], 'Not established from documentation')
        self.assertEqual(c['evidence_basis'], 'documentation_gap')
        self.assertIn('silent', c['gap_reason'])

    def test_evidence_change_under_same_id_changes_cell_evidence_hash(self):
        self.accepted()
        before = self.cell(self.export())['evidence_sha256']
        src = self.store.load('sources.json')
        src['entries']['E01']['quote'] = 'a different quotation under the same id'
        self.store.save('sources.json', src)
        self.assertNotEqual(self.cell(self.export())['evidence_sha256'], before)

    def test_unsafe_evidence_url_is_rejected(self):
        self.accepted()
        p = self.export()
        p['evidence'][0]['url'] = 'javascript:alert(1)'
        self.assertTrue(any('unsafe' in b for b in pubcheck.check_payload(p)))

    def test_score_fields_are_rejected(self):
        self.accepted()
        p = self.export()
        p['cells'][0]['score'] = 3
        self.assertTrue(any('score' in b for b in pubcheck.check_payload(p)))

    def test_release_binds_inputs_and_is_stable(self):
        self.accepted()
        a, b = self.export(), self.export()
        self.assertEqual(a['release']['release_id'], b['release']['release_id'])
        self.assertEqual(set(a['release']['source_file_sha256']), set(publish.BOUND_FILES))
        self.assertNotIn('people.json', a['release']['source_file_sha256'])

    def test_source_dataset_is_not_modified(self):
        self.accepted()
        names = ('cells.json', 'reviews.json', 'manifest.json', 'worklog.jsonl', 'validation_report.json')

        def read():
            return {n: open(self.store.path(n), 'rb').read() if self.store.exists(n) else None for n in names}
        before = read()
        self.export()
        self.assertEqual(before, read())
