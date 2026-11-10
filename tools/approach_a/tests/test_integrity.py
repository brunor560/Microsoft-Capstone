"""Review/provenance regressions: synthetic data and isolated local Git only."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from tools.approach_a import publish, pubcheck, review, store as st, validate
from tools.approach_a.tests.test_publish import Fixture


class ReviewBinding(Fixture):
    def current(self):
        return review.current(self.store, self.store.load('cells.json')['cells'])

    def test_quote_edit_under_same_id_stales_review_and_blocks_export(self):
        self.accepted()
        src = self.store.load('sources.json')
        src['entries']['E01']['quote'] = 'Different quotation, same ID'
        self.store.save('sources.json', src)
        self.assertTrue(self.current()['tool-cli/F07']['stale'])
        self.assertEqual(validate.inspect(self.store)['counts_by_code']['REVIEW_STALE'], 18)
        with self.assertRaisesRegex(publish.PublishError, 'REVIEW_STALE'):
            self.export()

    def test_profile_scope_edit_stales_only_that_profile(self):
        self.accepted()
        self.add_profile(pid='second-cli')
        self.complete_cells(pid='second-cli')
        self.review_all(pid='second-cli')
        m = self.store.load('manifest.json')
        m['profiles'][0]['platforms'] = ['Windows']
        self.store.save('manifest.json', m)
        current = self.current()
        self.assertTrue(current['tool-cli/F07']['stale'])
        self.assertFalse(current['second-cli/F07']['stale'])
        review.approve(self.store, 'ross')
        with self.assertRaisesRegex(publish.PublishError, 'REVIEW_STALE'):
            self.export()

    def test_unrelated_evidence_profile_and_manifest_version_do_not_stale_review(self):
        self.accepted()
        self.add_profile(pid='second-cli')
        src = self.store.load('sources.json')
        src['entries']['E99'] = dict(src['entries']['E01'], id='E99', quote='Unrelated')
        self.store.save('sources.json', src)
        m = self.store.load('manifest.json')
        m['profiles'][1]['platforms'] = ['Different platform']
        m['manifest_version'] += 1
        self.store.save('manifest.json', m)
        self.assertTrue(all(not r['stale'] for r in self.current().values()))
        self.assertIn('APPROVAL_MISSING', validate.inspect(self.store)['counts_by_code'])

    def test_legacy_records_are_preserved_and_require_explicit_rereview(self):
        self.accepted()
        data = self.store.load('reviews.json')
        legacy = data['reviews'][0]
        for key in ('binding_version', 'evidence_sha256', 'profile_sha256'):
            legacy.pop(key)
        self.store.save('reviews.json', data)
        original = Path(self.store.path('reviews.json')).read_bytes()
        rv = self.current()[legacy['cell_id']]
        self.assertTrue(rv['stale'])
        self.assertIn('Legacy', rv['stale_reason'])
        self.assertIn('REVIEW_STALE', validate.inspect(self.store)['counts_by_code'])
        with self.assertRaisesRegex(publish.PublishError, 'REVIEW_STALE'):
            self.export()
        self.assertEqual(original, Path(self.store.path('reviews.json')).read_bytes())
        review.record(self.store, legacy['cell_id'], 'bruno', 'agree', 'Explicit fixture re-review')
        self.assertFalse(self.current()[legacy['cell_id']]['stale'])
        self.assertEqual(self.store.load('reviews.json')['reviews'][0], legacy)


class GitProvenance(Fixture):
    def setUp(self):
        super().setUp()
        self.accepted()
        self.repo = Path(self.dir) / 'repo'
        self.repo.mkdir()
        self.dataset = self.repo / 'assessment' / 'reviewed'
        self.dataset.mkdir(parents=True)
        for name in publish.SNAPSHOT_FILES:
            shutil.copyfile(self.store.path(name), self.dataset / name)
        self.git('init', '-q')
        self.git('add', 'assessment')
        self.commit()
        self.head = self.git('rev-parse', 'HEAD').strip()
        self.public = self.repo / 'dashboard' / 'feature-matrix' / 'data' / 'matrix.json'
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(st, 'REPO', str(self.repo)))
        self.stack.enter_context(patch.object(publish, 'DASHBOARD', str(self.repo / 'dashboard')))
        self.stack.enter_context(patch.object(publish, 'OUT_DIR', str(self.public.parent)))

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.repo, check=True,
                              capture_output=True, text=True).stdout

    def commit(self):
        self.git('-c', 'user.name=Fixture Operator', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Synthetic reviewed snapshot')

    def run_export(self, dataset=None, out=None, commit=None):
        args = SimpleNamespace(mode='accepted', out=str(out or self.public),
                               allow_other_out=True, source_commit=commit)
        with contextlib.redirect_stdout(io.StringIO()):
            return publish.run(st.Store(str(dataset or self.dataset)), args)

    def test_matching_committed_snapshot_can_write_public_projection(self):
        for commit in (None, self.head):
            self.assertEqual(self.run_export(commit=commit), 0)
            payload = json.loads(self.public.read_text())
            rel = payload['release']
            self.assertEqual(rel['source_commit'], self.head)
            self.assertEqual(rel['source_dataset_path'], 'assessment/reviewed')
            self.assertTrue(rel['source_verified'])
            self.assertFalse(rel['source_dirty'])
            self.assertEqual(set(rel['source_file_sha256']), set(publish.SNAPSHOT_FILES))
            self.assertEqual(pubcheck.check_public_file(payload), [])

    def test_scratch_copy_cannot_write_public_even_with_explicit_commit(self):
        # The original fixture store is outside the repo; HEAD contains equal
        # bytes at a different path, which is not provenance for this dataset.
        for commit in (None, self.head):
            with self.assertRaisesRegex(publish.PublishError, 'committed'):
                self.run_export(dataset=self.dir, commit=commit)
            self.assertFalse(self.public.exists())
        local = Path(self.dir) / 'local.json'
        self.assertEqual(self.run_export(dataset=self.dir, out=local, commit=self.head), 0)
        rel = json.loads(local.read_text())['release']
        self.assertIsNone(rel['source_commit'])
        self.assertEqual(rel['requested_source_commit'], self.head)
        self.assertFalse(rel['source_verified'])
        self.assertTrue(rel['source_dirty'])
        self.assertTrue(pubcheck.check_public_file(json.loads(local.read_text())))

    def test_every_bound_input_rejects_uncommitted_bytes_including_roster(self):
        for name in publish.BOUND_FILES:
            with self.subTest(name=name):
                path = self.dataset / name
                original = path.read_bytes()
                path.write_bytes(original + b'\n')  # Semantically identical JSON.
                with self.assertRaisesRegex(publish.PublishError, 'committed'):
                    self.run_export(commit=self.head)
                self.assertFalse(self.public.exists())
                path.write_bytes(original)

    def test_staged_changes_and_old_explicit_commit_cannot_claim_clean_inputs(self):
        path = self.dataset / 'people.json'
        original = path.read_bytes()
        path.write_bytes(original + b'\n')
        self.git('add', 'assessment/reviewed/people.json')
        path.write_bytes(original)  # Worktree matches HEAD, index does not.
        with self.assertRaisesRegex(publish.PublishError, 'committed'):
            self.run_export(commit=self.head)
        path.write_bytes(original + b'\n')
        self.commit()
        with self.assertRaisesRegex(publish.PublishError, 'committed'):
            self.run_export(commit=self.head)
        self.assertEqual(self.run_export(), 0)

    def test_untracked_copy_inside_repo_is_not_a_committed_dataset_path(self):
        other = self.repo / 'assessment' / 'untracked'
        shutil.copytree(self.dataset, other)
        with self.assertRaisesRegex(publish.PublishError, 'committed'):
            self.run_export(dataset=other, commit=self.head)
        self.assertFalse(self.public.exists())

    def test_nonexistent_commit_cannot_be_used_for_public_output(self):
        with self.assertRaisesRegex(publish.PublishError, 'committed'):
            self.run_export(commit='f' * 40)
        self.assertFalse(self.public.exists())

    def test_final_write_rechecks_provenance_and_preserves_existing_public_file(self):
        raw = publish.snapshot(st.Store(str(self.dataset)))
        payload = publish.build(raw, source_commit=self.head, dataset_root=str(self.dataset))
        self.public.parent.mkdir(parents=True)
        self.public.write_text('Existing projection')
        path = self.dataset / 'catalog.json'
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(publish.PublishError, 'provenance'):
            publish.write(payload, str(self.public))
        self.assertEqual(self.public.read_text(), 'Existing projection')
        local = publish.build(raw, source_commit=self.head, source_dirty=False)
        self.assertFalse(local['release']['source_verified'])
        self.assertIsNone(local['release']['source_commit'])
        with self.assertRaisesRegex(publish.PublishError, 'committed'):
            publish.write(local, str(self.public))
        self.assertEqual(self.public.read_text(), 'Existing projection')

    def test_local_mismatched_dataset_reports_actual_verification_state(self):
        path = self.dataset / 'catalog.json'
        path.write_bytes(path.read_bytes() + b'\n')
        out = Path(self.dir) / 'local-mismatch.json'
        self.run_export(out=out, commit=self.head)
        rel = json.loads(out.read_text())['release']
        self.assertFalse(rel['source_verified'])
        self.assertTrue(rel['source_dirty'])
        self.assertEqual(rel['source_commit'], self.head)
        self.assertEqual(rel['source_dataset_path'], 'assessment/reviewed')
