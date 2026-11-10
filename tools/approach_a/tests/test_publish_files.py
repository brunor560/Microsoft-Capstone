"""Preview, output-path and committed-data-file tests for the publication export (no network)."""
import json
import os
import unittest

from tools.approach_a import publish, pubcheck, review
from tools.approach_a import store as st
from tools.approach_a.tests.test_publish import Fixture

DATA_FILE = os.path.join(publish.OUT_DIR, 'matrix.json')


class Args:
    def __init__(self, mode='accepted', out=None, allow_other_out=True):
        self.mode, self.out, self.allow_other_out, self.source_commit = mode, out, allow_other_out, 'a' * 40


class PreviewAndOutput(Fixture):
    def test_preview_keeps_draft_cells_with_labels(self):
        self.add_profile()
        p = self.export('preview')
        self.assertEqual(p['release']['publication_mode'], 'preview')
        self.assertFalse(p['release']['accepted'])
        c = self.cell(p)
        self.assertEqual(c['assessment_state'], 'pending')
        self.assertIn('CELL_PENDING', c['blocking_codes'])
        self.assertEqual(pubcheck.check_payload(p), [])

    def test_preview_is_never_publishable(self):
        self.add_profile()
        self.assertTrue(pubcheck.check_public_file(self.export('preview')))

    def test_preview_output_inside_dashboard_is_refused(self):
        with self.assertRaises(publish.PublishError):
            publish.resolve_out('preview', os.path.join(publish.DASHBOARD, 'feature-matrix', 'x.json'))
        self.assertFalse(publish.DEFAULT_OUT['preview'].startswith(publish.DASHBOARD + os.sep))

    def test_accepted_output_must_be_under_data_dir_unless_overridden(self):
        with self.assertRaises(publish.PublishError):
            publish.resolve_out('accepted', '/tmp/elsewhere/matrix.json')
        self.assertEqual(publish.resolve_out('accepted'), DATA_FILE)
        self.assertTrue(publish.resolve_out('accepted', '/tmp/e/m.json', allow_other_out=True))

    def test_cli_refuses_unaccepted_dataset_then_writes_accepted(self):
        out = os.path.join(self.dir, 'out', 'matrix.json')
        self.add_profile()
        with self.assertRaises(publish.PublishError):
            publish.run(self.store, Args('accepted', out))
        self.assertFalse(os.path.exists(out))
        review.approve(self.store, 'ross')
        self.complete_cells()
        self.review_all()
        self.assertEqual(publish.run(self.store, Args('accepted', out)), 0)
        with open(out, encoding='utf-8') as f:
            self.assertEqual(pubcheck.check_payload(json.load(f)), [])
        self.assertEqual([n for n in os.listdir(os.path.dirname(out)) if n.endswith('.tmp')], [])


class CommittedDataFile(unittest.TestCase):
    """dashboard/feature-matrix/data/matrix.json is required for a data release.

    It is either the deliberate empty marker or an accepted payload. A missing
    file fails here, so it cannot be mistaken for the deliberate empty state.
    """

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(DATA_FILE),
                        'missing %s (commit an accepted export or the empty marker)' % DATA_FILE)

    def test_file_is_empty_marker_or_clean_accepted_payload(self):
        with open(DATA_FILE, encoding='utf-8') as f:
            obj = json.load(f)
        self.assertEqual(pubcheck.check_public_file(obj, st.Store().people()), [])

    def test_empty_marker_must_be_exact(self):
        self.assertEqual(pubcheck.check_public_file(pubcheck.empty_marker()), [])
        self.assertTrue(pubcheck.check_public_file(dict(pubcheck.empty_marker(), message='Looks fine')))
        self.assertTrue(pubcheck.check_public_file({'schema': 'something-else'}))

    def test_no_preview_files_under_dashboard(self):
        found = []
        for root, _, files in os.walk(publish.DASHBOARD):
            if 'node_modules' not in root:
                found += [f for f in files if 'preview' in f.lower() and f.endswith('.json')]
        self.assertEqual(found, [])


class PreviewRoutes(unittest.TestCase):
    def test_preview_routes_stay_outside_pages_upload(self):
        from tools.approach_a import preview_server
        handler = object.__new__(preview_server.Handler)
        for url, expected in [(preview_server.PREVIEW_URL, preview_server.PREVIEW_FILE),
                              (preview_server.DEMO_URL, preview_server.DEMO_FILE)]:
            self.assertEqual(handler.translate_path(url + '?cache=1'), expected)
            self.assertFalse(os.path.realpath(expected).startswith(os.path.realpath(publish.DASHBOARD) + os.sep))

    def test_no_fictional_demo_assets_under_pages_upload(self):
        found = []
        for root, _, files in os.walk(os.path.join(publish.DASHBOARD, 'feature-matrix')):
            found.extend(os.path.join(root, name) for name in files
                         if name in ('demo-data.mjs', 'matrix.demo.json', 'shortlist-fixture.mjs'))
        self.assertEqual(found, [])


if __name__ == '__main__':
    unittest.main()
