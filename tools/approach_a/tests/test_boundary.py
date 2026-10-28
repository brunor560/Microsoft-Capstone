"""Proposed (rehearsal) boundaries versus confirmed boundaries (no network)."""
import unittest

from tools.approach_a import cmd_research, model, review
from tools.approach_a import store as st
from tools.approach_a.__main__ import parser
from tools.approach_a.tests.test_validation import Base


class Boundary(Base):
    def proposed(self):
        p = {'id': 'tool-cli', 'tool': 'Fixture Tool', 'tool_key': 'fixture', 'surface': 'cli',
             'surface_label': 'Fixture CLI', 'category_tags': ['T2'],
             'version': {'value': None, 'documentation_note': 'unversioned'},
             'modes': ['default'], 'platforms': ['Linux'], 'account_and_tier': 'Free',
             'exclusions': ['IDE'], 'source_access_date': '2026-10-21', 'boundary_state': 'proposed'}
        model.add_profile(self.store, p, 'agent-rehearsal')
        return p

    def test_unconfirmed_boundary_blocks_acceptance(self):
        self.proposed()
        _, codes = self.codes()
        self.assertIn('BOUNDARY_UNCONFIRMED', codes)

    def test_unconfirmed_boundary_cannot_be_approved(self):
        self.proposed()
        with self.assertRaises(ValueError):
            review.approve(self.store, 'ross')

    def test_research_refused_without_rehearsal_flag(self):
        self.proposed()
        args = parser().parse_args(['research', '--offline'])
        self.assertEqual(cmd_research.run(self.store, args), 2)
        self.assertNotIn('research_started', [e['event'] for e in self.store.worklog()])

    def test_confirmation_bumps_version_and_clears_authors(self):
        p = self.proposed()
        self.complete_cells(author='ross')
        before = self.store.load('manifest.json')['manifest_version']
        confirmed = dict(p, confirmed_by='ross', confirmed_at=st.now(), boundary_state='confirmed')
        m = model.confirm_profile(self.store, confirmed, 'ross')
        self.assertEqual(m['manifest_version'], before + 1)
        self.assertIsNone(m['approval'])
        cells = self.store.load('cells.json')['cells']
        self.assertTrue(all(c['author'] is None for c in cells.values()))
        _, codes = self.codes()
        self.assertNotIn('BOUNDARY_UNCONFIRMED', codes)
        self.assertIn('AUTHOR_MISSING', codes)


if __name__ == '__main__':
    unittest.main()
