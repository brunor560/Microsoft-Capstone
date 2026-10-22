"""Validator and review-rule tests on synthetic datasets (no network).

Run from the repository root:  python3 -m unittest discover -s tools/approach_a/tests -t .
Fixtures are built in temporary directories; they are test data, not findings.
"""
import json
import os
import shutil
import tempfile
import unittest

from tools.approach_a import challenge, model, review, validate
from tools.approach_a import store as st

ROOT = os.path.join(st.REPO, 'assessment')


def quiet(*_):
    pass


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix='aa-test-')
        self.store = st.Store(self.dir)
        self.store.init_from(ROOT)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def codes(self):
        rep = validate.run(self.store)
        return rep, {i['code'] for i in rep['issues']}

    def add_profile(self, pid='tool-cli', who='ross'):
        p = {'id': pid, 'tool': 'Fixture Tool', 'tool_key': 'fixture', 'surface': 'cli',
             'surface_label': 'Fixture CLI', 'category_tags': ['T2'],
             'version': {'value': None, 'documentation_note': 'Fixture docs are unversioned'},
             'modes': ['default'], 'platforms': ['Linux'], 'account_and_tier': 'Free',
             'exclusions': ['IDE'], 'source_access_date': '2026-10-21',
             'confirmed_by': who, 'confirmed_at': st.now()}
        model.add_profile(self.store, p, who)
        return p

    def complete_cells(self, pid='tool-cli', author='ross'):
        """Fill every cell as a finished NE gap finding with a fixture source."""
        src = self.store.load('sources.json')
        src['entries']['E01'] = {'id': 'E01', 'url': 'https://example.invalid/docs/', 'section': 'Fixture',
                                 'access_date': '2026-10-21', 'check': 'verified', 'surface': 'cli',
                                 'page_title': 'Fixture', 'quote': 'fixture'}
        self.store.save('sources.json', src)
        data = self.store.load('cells.json')
        for c in data['cells'].values():
            if c['profile_id'] != pid:
                continue
            c.update({'assessment_state': 'challenged', 'evidence_basis': 'documentation_gap',
                      'gap_reason': 'Fixture pages are silent on this feature', 'evidence_refs': ['E01'],
                      'drafted_by': 'agent', 'assessment_date': '2026-10-21', 'author': author,
                      'challenge': {'flags': []}})
        self.store.save('cells.json', data)

    def review_all(self, reviewer='bruno', pid='tool-cli'):
        for f in self.store.catalog()['features']:
            review.record(self.store, model.cell_id(f['id'], pid), reviewer, 'agree', 'Checked against source')


class EmptyAndManifest(Base):
    def test_empty_manifest_does_not_pass(self):
        rep, codes = self.codes()
        self.assertFalse(rep['accepted'])
        self.assertIn('INPUT_INCOMPLETE', codes)
        self.assertEqual(rep['P'], 0)

    def test_unapproved_manifest_blocks(self):
        self.add_profile()
        self.complete_cells()
        self.review_all()
        rep, codes = self.codes()
        self.assertEqual(codes, {'APPROVAL_MISSING'})

    def test_full_valid_dataset_is_accepted(self):
        self.add_profile()
        review.approve(self.store, 'ross')
        self.complete_cells()
        self.review_all()
        rep, codes = self.codes()
        self.assertTrue(rep['accepted'], rep['issues'][:5])
        self.assertEqual(rep['expected_cells'], 18)

    def test_manifest_change_after_approval_is_stale(self):
        self.add_profile()
        review.approve(self.store, 'ross')
        m = self.store.load('manifest.json')
        m['profiles'][0]['exclusions'].append('edited after approval')
        self.store.save('manifest.json', m)
        _, codes = self.codes()
        self.assertIn('APPROVAL_STALE', codes)

    def test_non_approver_cannot_approve(self):
        self.add_profile()
        with self.assertRaises(ValueError):
            review.approve(self.store, 'bruno')
        with self.assertRaises(ValueError):
            review.approve(self.store, 'nobody')

    def test_duplicate_profile_rejected(self):
        self.add_profile()
        with self.assertRaises(ValueError):
            self.add_profile()
        m = self.store.load('manifest.json')
        m['profiles'].append(dict(m['profiles'][0]))
        self.store.save('manifest.json', m)
        _, codes = self.codes()
        self.assertIn('PROFILE_INVALID', codes)

    def test_profile_missing_fields(self):
        self.add_profile()
        m = self.store.load('manifest.json')
        m['profiles'][0]['platforms'] = []
        m['profiles'][0]['confirmed_by'] = None
        self.store.save('manifest.json', m)
        _, codes = self.codes()
        self.assertIn('PROFILE_INVALID', codes)
