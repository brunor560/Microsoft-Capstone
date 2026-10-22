"""Model-assisted drafting with a fake Azure endpoint (no network, no real key)."""
import io
import json
import os
import urllib.error
from unittest import mock

from tools.approach_a import azure, cmd_research, drafting, fetch, model, pages, sources, validate
from tools.approach_a.__main__ import parser
from tools.approach_a.tests.test_validation import Base

KEY = 'sk-fake-0123456789abcdef'
PAGE = ('<html><head><title>Permissions - Fixture CLI | Docs</title></head><body><main>'
        '<h1>Fixture CLI</h1><h2>Permissions</h2>'
        '<p>Deny rules block the action immediately and cannot be overridden by the agent.</p>'
        '<h2>Project instructions</h2><p>Project instruction files are loaded at session start for every task.</p>'
        '</main></body></html>')
URL = 'https://docs.example.invalid/permissions/'


def reply(content, finish='stop', usage=(900, 200)):
    body = {'id': 'chatcmpl-1', 'model': 'gpt-4.1-mini-2025-04-14',
            'choices': [{'message': {'content': json.dumps(content) if isinstance(content, dict) else content},
                         'finish_reason': finish}],
            'usage': {'prompt_tokens': usage[0], 'completion_tokens': usage[1]}}
    return 200, {'apim-request-id': 'req-123'}, json.dumps(body)


def brief(fid, quote='Deny rules block the action immediately', section='Permissions'):
    return {'feature_id': fid, 'status': 'Built in', 'evidence_basis': 'documented_support', 'gap_reason': None,
            'supported_scope': 'Deny rules', 'unsupported_scope': [], 'unestablished_scope': [],
            'required_setup': 'None', 'activation_state': 'default', 'control_mechanism': 'enforced',
            'constraints': [], 'evidence': [{'page': 'permissions', 'section': section, 'quote': quote,
                                             'claim': 'deny rules'}]}


def http_error(code, headers=None):
    return urllib.error.HTTPError(URL, code, 'err', headers or {}, io.BytesIO(b'{"error":"' + KEY.encode() + b'"}'))


class Drafting(Base):
    def setUp(self):
        super().setUp()
        cand_dir = self.store.path('candidates', 'fixture')
        os.makedirs(cand_dir)
        cand = {'tool_key': 'fixture', 'tool': 'Fixture Tool', 'default_surface': 'cli',
                'docs': {'base_url': 'https://docs.example.invalid/', 'publisher': 'Fixture',
                         'allowed_prefixes': ['https://docs.example.invalid/'], 'surface_labels': {'Fixture CLI': 'cli'}},
                'surfaces': {'cli': {'seed_pages': ['permissions', 'permissions']}}}
        with open(os.path.join(cand_dir, 'candidate.json'), 'w') as fh:
            json.dump(cand, fh)
        fetch.PageCache(self.store).put(sources.page_key(URL), pages.to_text(PAGE), PAGE)
        self.add_profile()
        m = self.store.load('manifest.json')
        m['profiles'][0]['tool_key'] = 'fixture'
        self.store.save('manifest.json', m)
        self.env = os.path.join(self.dir, 'test.env')
        with open(self.env, 'w') as f:
            f.write('# fixture\nAZURE_DEV_ENDPOINT=https://fixture.openai.azure.com/\n'
                    'AZURE_DEV_DEPLOYMENT=gpt-4.1-mini\nAZURE_DEV_API_VERSION="2024-10-21"\n'
                    'export AZURE_DEV_API_KEY=%s\n' % KEY)
        self.ledger_path = os.path.join(self.dir, 'spend.jsonl')
        p = mock.patch.dict(os.environ, {'APPROACH_A_SPEND_LEDGER': self.ledger_path})
        p.start()
        self.addCleanup(p.stop)
        s = mock.patch.object(azure, '_sleep', lambda *_: None)
        s.start()
        self.addCleanup(s.stop)

    def config(self, **limits):
        c = azure.load_config()
        c['limits'] = dict(c['limits'], **limits)
        return c

    def client(self, post, **limits):
        # Pacing is tested on its own with a fake clock; here it must never wait.
        limits.setdefault('requests_per_minute', 10 ** 6)
        limits.setdefault('tokens_per_minute', 10 ** 9)
        c = self.config(**limits)
        conn = azure.connection(c, env_file=self.env)
        return azure.Client(conn, c, azure.Ledger(c, self.ledger_path), post=post)

    def index(self):
        idx = sources.SourceIndex(self.store, offline=True)
        cand = next(c for c in self.store.candidates() if c['tool_key'] == 'fixture')
        idx.page(URL, cand['docs'])
        return idx, cand

    def draft(self, post, **limits):
        idx, cand = self.index()
        profile = self.store.load('manifest.json')['profiles'][0]
        cl = self.client(post, **limits)
        return drafting.draft_profile(self.store, idx, cand, profile, [URL], cl, lambda *a: None, 'ross'), cl

    def all_text(self):
        out = []
        for root, _, files in os.walk(self.dir):
            for f in files:
                if not f.endswith('.env'):
                    with open(os.path.join(root, f), encoding='utf-8', errors='replace') as fh:
                        out.append(fh.read())
        return '\n'.join(out)


def fid_of(body):
    import re
    return re.search(r'Feature (F\d\d)', body['messages'][1]['content']).group(1)


class Tests(Drafting):
    def test_env_mapping_and_redaction(self):
        conn = azure.connection(self.config(), env_file=self.env)
        self.assertEqual((conn.deployment, conn.api_version, conn.host),
                         ('gpt-4.1-mini', '2024-10-21', 'fixture.openai.azure.com'))
        self.assertNotIn(KEY, repr(conn) + json.dumps(conn.describe()))
        with open(self.env, 'w') as f:
            f.write('AZURE_DEV_ENDPOINT=https://x.openai.azure.com/\n')
        with self.assertRaises(ValueError) as cm:
            azure.connection(self.config(), env_file=self.env)
        self.assertIn('AZURE_DEV_API_KEY', str(cm.exception))

    def test_drafts_verify_and_stay_unaccepted(self):
        sent = []

        def post(conn, body, timeout):
            sent.append(body)
            return reply(brief(fid_of(body)))
        r, cl = self.draft(post)
        self.assertGreater(r['drafted'], 0)
        self.assertEqual(len(sent), r['drafted'])
        self.assertTrue(all(b['max_tokens'] == cl.ledger.lim['max_output_tokens_per_request'] for b in sent))
        args = parser().parse_args(['research', '--offline', '--operator', 'ross'])
        cmd_research.run(self.store, args)
        cells = self.store.load('cells.json')['cells']
        drafted = [c for c in cells.values() if c['assessment_state'] == 'challenged']
        self.assertEqual(len(drafted), r['drafted'])
        c = drafted[0]
        self.assertEqual(c['drafted_by'], 'model:azure-openai/gpt-4.1-mini')
        self.assertEqual(c['model_provenance']['request_id'], 'req-123')
        self.assertIn('model_drafted', {f['type'] for f in c['challenge']['flags']})
        rep = validate.run(self.store)
        self.assertFalse(rep['accepted'])
        self.assertIn('AUTHOR_MISSING', {i['code'] for i in rep['issues']})
        log = self.store.worklog()
        self.assertTrue(any(e['event'] == 'model_request' and e['usage']['input_tokens'] == 900 for e in log))
        self.assertNotIn(KEY, self.all_text())

    def test_invented_quote_stays_pending(self):
        r, _ = self.draft(lambda c, b, t: reply(brief(fid_of(b), quote='Deny rules are optional suggestions only')))
        args = parser().parse_args(['research', '--offline', '--operator', 'ross'])
        cmd_research.run(self.store, args)
        cells = self.store.load('cells.json')['cells']
        self.assertEqual(model.counts(cells)['pending'], 18)
        self.assertGreater(r['drafted'], 0)

    def test_invalid_response_rejected_then_skipped(self):
        r, _ = self.draft(lambda c, b, t: reply('not json'))
        self.assertGreater(r['rejected'], 0)
        self.assertEqual(r['drafted'], 0)
        calls = []
        r2, _ = self.draft(lambda c, b, t: calls.append(1) or reply(brief(fid_of(b))))
        self.assertEqual(calls, [])
        self.assertEqual(r2['drafted'], 0)

    def test_page_outside_excerpts_dropped(self):
        b = brief('F07')
        b['evidence'][0]['page'] = 'https://evil.example/'
        out, problems = drafting.check_brief(json.dumps(b), 'F07', self.store.catalog(), [
            {'page': 'permissions', 'section': 'Permissions', 'text': ''}])
        self.assertIsNone(out)
        self.assertIn('no usable evidence', problems)

    def test_retry_on_429_then_success(self):
        seq = [http_error(429, {'retry-after': '1'})]

        def post(conn, body, timeout):
            if seq:
                raise seq.pop()
            return reply(brief(fid_of(body)))
        r, cl = self.draft(post, max_requests_per_run=2)
        self.assertEqual(r['drafted'], 1)
        self.assertEqual(cl.ledger.requests, 2)
        self.assertNotIn(KEY, self.all_text())

    def test_auth_error_raises_unavailable(self):
        calls = []

        def post(conn, body, timeout):
            calls.append(1)
            raise http_error(401)
        with self.assertRaises(azure.AuthError):
            self.draft(post)
        self.assertEqual(len(calls), 1)
        self.assertTrue(any(e['event'] == 'model_request_failed' and e.get('stops_run')
                            for e in self.store.worklog()))
        self.assertNotIn(KEY, self.all_text())

    def test_bad_request_skips_only_that_feature(self):
        calls = []

        def post(conn, body, timeout):
            calls.append(1)
            if len(calls) == 1:
                raise http_error(400)
            return reply(brief(fid_of(body)))
        r, _ = self.draft(post, max_requests_per_run=2)
        self.assertEqual((r['failed'], r['drafted']), (1, 1))

    def test_default_mode_and_opt_out(self):
        cfg = azure.load_config()
        self.assertEqual(cfg['default_draft'], 'azure')
        with mock.patch.dict(os.environ, {'APPROACH_A_DRAFT': ''}):
            self.assertEqual(azure.draft_mode(parser().parse_args(['research']), cfg), 'azure')
            self.assertEqual(azure.draft_mode(parser().parse_args(['research', '--no-draft']), cfg), 'off')
            self.assertEqual(azure.draft_mode(parser().parse_args(['resume', '--no-draft']), cfg), 'off')
        self.assertEqual(azure.draft_mode(parser().parse_args(['research']), cfg), 'off')  # tests force off
        self.assertTrue(azure.env_file_for(parser().parse_args(['research']), cfg).endswith(
            os.path.join('pipeline', 'autogen', '.env')))
        self.assertEqual(azure.env_file_for(parser().parse_args(['research', '--env-file', self.env]), cfg), self.env)

    def run_default(self, *extra):
        """research with no drafting flags and drafting on by default (as in the demo)."""
        args = parser().parse_args(['research', '--operator', 'ross'] + list(extra))
        with mock.patch.dict(os.environ, {'APPROACH_A_DRAFT': ''}):
            return cmd_research.run(self.store, args)

    def test_default_missing_env_file_stops_with_error(self):
        missing = os.path.join(self.dir, 'absent.env')
        with mock.patch.object(azure, 'env_file_for', lambda a, c: missing):
            self.assertEqual(self.run_default(), 2)
        events = [e['event'] for e in self.store.worklog()]
        self.assertIn('research_refused', events)
        self.assertNotIn('research_started', events)
        self.assertEqual(model.counts(self.store.load('cells.json')['cells'])['pending'], 18)

    def test_default_offline_stops_with_error(self):
        self.assertEqual(self.run_default('--offline'), 2)
        self.assertNotIn('research_started', [e['event'] for e in self.store.worklog()])

    def test_no_draft_opt_out_runs_without_azure(self):
        args = parser().parse_args(['research', '--offline', '--no-draft', '--operator', 'ross'])
        with mock.patch.dict(os.environ, {'APPROACH_A_DRAFT': ''}), \
                mock.patch.object(azure, '_post', side_effect=AssertionError('no request expected')):
            self.assertEqual(cmd_research.run(self.store, args), 0)

    def test_unavailable_mid_run_stops_and_keeps_drafts(self):
        calls = []

        def post(conn, body, timeout):
            calls.append(1)
            if len(calls) == 1:
                return reply(brief(fid_of(body)))
            raise urllib.error.URLError('connection refused')
        with mock.patch.object(azure, 'env_file_for', lambda a, c: self.env), \
                mock.patch.object(azure, '_post', post), \
                mock.patch.object(azure, 'Pacer', lambda *a: mock.Mock(wait=lambda *a, **k: None)), \
                mock.patch.object(fetch, 'fetch', side_effect=AssertionError('cached pages only')):
            self.assertEqual(self.run_default(), 2)
        self.assertEqual(len(drafting.load_drafts(self.store, 'tool-cli')), 1)
        events = [e['event'] for e in self.store.worklog()]
        self.assertIn('research_stopped', events)
        self.assertNotIn('challenge_pass', events)
        self.assertNotIn(KEY, self.all_text())

    def test_request_limit(self):
        calls = []
        r, cl = self.draft(lambda c, b, t: calls.append(1) or reply(brief(fid_of(b))), max_requests_per_run=1)
        self.assertEqual(len(calls), 1)
        self.assertTrue(r['stopped'].startswith('limit'))
        self.assertTrue(any(e['event'] == 'model_limit_reached' for e in self.store.worklog()))

    def test_total_spend_cap_persists(self):
        with open(self.ledger_path, 'w') as f:
            f.write(json.dumps({'cost_usd': 4.999}) + '\n')
        calls = []
        r, _ = self.draft(lambda c, b, t: calls.append(1) or reply(brief(fid_of(b))))
        self.assertEqual(calls, [])
        self.assertIn('total spending cap', r['stopped'])

    def test_pacer_waits_on_token_window(self):
        clock = [0.0]
        waits = []
        with mock.patch.object(azure, '_clock', lambda: clock[0]), \
                mock.patch.object(azure, '_sleep', lambda s: (waits.append(s), clock.__setitem__(0, clock[0] + s))):
            p = azure.Pacer(10, 10000)
            p.wait(6000)
            p.wait(6000)
        self.assertEqual(len(waits), 1)
        self.assertAlmostEqual(waits[0], 60, delta=1)
