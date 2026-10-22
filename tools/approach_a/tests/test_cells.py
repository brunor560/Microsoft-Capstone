"""Coverage, cell, evidence, challenge and review tests (no network)."""
import unittest

from tools.approach_a import challenge, model, review
from tools.approach_a.tests.test_validation import Base

CID = 'tool-cli/F07'


class Coverage(Base):
    def setUp(self):
        super().setUp()
        self.add_profile()
        review.approve(self.store, 'ross')
        self.complete_cells()
        self.review_all()

    def mutate(self, fn):
        data = self.store.load('cells.json')
        fn(data['cells'])
        self.store.save('cells.json', data)

    def test_missing_cell(self):
        self.mutate(lambda c: c.pop(CID))
        _, codes = self.codes()
        self.assertIn('CELL_MISSING', codes)

    def test_extra_cell(self):
        self.mutate(lambda c: c.__setitem__('tool-cli/F19', dict(c[CID], feature_id='F19')))
        _, codes = self.codes()
        self.assertIn('CELL_UNEXPECTED', codes)

    def test_pending_cell_never_passes(self):
        self.mutate(lambda c: c.__setitem__(CID, model.pending_cell('F07', 'tool-cli')))
        rep, codes = self.codes()
        self.assertIn('CELL_PENDING', codes)
        self.assertFalse(rep['accepted'])

    def test_assessment_pending_is_not_a_gap_reason(self):
        self.mutate(lambda c: c[CID].update(gap_reason='Assessment pending'))
        _, codes = self.codes()
        self.assertIn('GAP_REASON_MISSING', codes)

    def test_dangling_evidence(self):
        self.mutate(lambda c: c[CID].update(evidence_refs=['E99']))
        _, codes = self.codes()
        self.assertIn('EVIDENCE_DANGLING', codes)

    def test_affirmative_without_source(self):
        self.mutate(lambda c: c[CID].update(status='Built in', evidence_basis='documented_support', evidence_refs=[]))
        _, codes = self.codes()
        self.assertIn('EVIDENCE_MISSING', codes)

    def test_unknown_status_and_score_field(self):
        self.mutate(lambda c: c[CID].update(status='Partially', score=3))
        _, codes = self.codes()
        self.assertIn('STATUS_INVALID', codes)
        self.assertIn('SCORE_FORBIDDEN', codes)

    def test_edit_after_review_makes_review_stale(self):
        self.mutate(lambda c: c[CID].update(supported_scope='changed after review'))
        _, codes = self.codes()
        self.assertIn('REVIEW_STALE', codes)


class Reviews(Base):
    def setUp(self):
        super().setUp()
        self.add_profile()
        review.approve(self.store, 'ross')
        self.complete_cells(author='ross')

    def test_self_review_refused(self):
        with self.assertRaises(ValueError):
            review.record(self.store, CID, 'ross', 'agree', 'mine')

    def test_unknown_reviewer_refused(self):
        with self.assertRaises(ValueError):
            review.record(self.store, CID, 'chad', 'agree', 'sponsor is not on the roster')

    def test_missing_reviews_block(self):
        _, codes = self.codes()
        self.assertIn('REVIEW_MISSING', codes)

    def test_open_disagreement_blocks(self):
        self.review_all()
        review.record(self.store, CID, 'kapil', 'disagree', 'Scope overstated')
        _, codes = self.codes()
        self.assertIn('DISAGREEMENT_OPEN', codes)

    def test_disagreement_reopens_reviewed_cell(self):
        self.review_all()
        review.record(self.store, CID, 'kapil', 'disagree', 'Scope overstated')
        self.assertEqual(self.store.load('cells.json')['cells'][CID]['assessment_state'], 'challenged')

    def test_resolved_disagreement_needs_new_agree(self):
        self.review_all()
        review.record(self.store, CID, 'kapil', 'disagree', 'Scope overstated', 'author_revised')
        _, codes = self.codes()
        self.assertIn('REVIEW_MISSING', codes)
        self.assertNotIn('DISAGREEMENT_OPEN', codes)
        review.record(self.store, CID, 'kapil', 'agree', 'Revision accepted')
        rep, _ = self.codes()
        self.assertTrue(rep['accepted'], rep['issues'][:3])

    def test_cell_without_author_cannot_be_reviewed(self):
        data = self.store.load('cells.json')
        data['cells'][CID]['author'] = None
        self.store.save('cells.json', data)
        with self.assertRaises(ValueError):
            review.record(self.store, CID, 'bruno', 'agree', 'x')


class Challenge(Base):
    def test_surface_transfer_and_unsupported_claim(self):
        self.add_profile()
        profile = self.store.load('manifest.json')['profiles'][0]
        idx = {'pages': {}, 'entries': {
            'E01': {'id': 'E01', 'url': 'u', 'surface': 'ide', 'check': 'verified'},
            'E02': {'id': 'E02', 'url': 'u', 'surface': 'page:app+ide', 'check': 'verified'}}}
        cell = dict(model.pending_cell('F07', 'tool-cli'), status='Built in', evidence_refs=['E01', 'E02'])
        types = {f['type'] for f in challenge.challenge_cell(cell, profile, idx)}
        self.assertIn('surface_transfer', types)
        cell['evidence_refs'] = []
        types = {f['type'] for f in challenge.challenge_cell(cell, profile, idx)}
        self.assertIn('unsupported_claim', types)


if __name__ == '__main__':
    unittest.main()
