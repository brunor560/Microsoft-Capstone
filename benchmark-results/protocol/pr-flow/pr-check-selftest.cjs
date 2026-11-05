// Offline self-test for pr-check.cjs: runs it against simulated GitHub API
// responses for a correct run and for each kind of violation, and checks that
// exactly the expected checks fail. No network access and no token needed.
//
// Usage: node pr-check-selftest.cjs

const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const RUN = 'selftest-run01';
const BASE = `bench008/${RUN}/main`;
const START = 'a'.repeat(40);
const T = (min) => new Date(Date.UTC(2026, 10, 5, 12, min)).toISOString();

// A correct run: one PR, gate failed once, fixed, passed, then merged.
function goodRun() {
  return {
    user: { login: 'operator' },
    prs: [{
      number: 7, title: 'feat: add todo statistics', body: '## Requirements\n- REQ-01\n## Testing\nnpm test passed',
      head: { ref: `bench008/${RUN}/add-stats`, sha: 'c2' }, created_at: T(5), merged_at: T(20), merge_commit_sha: 'm1',
      commits: [
        { sha: 'c1', files: [{ filename: 'app/server.js', patch: '+app.get(...)' }], gate: [{ conclusion: 'failure', completed_at: T(8) }] },
        { sha: 'c2', files: [{ filename: 'app/test.js', patch: '+test(...)' }], gate: [{ conclusion: 'success', completed_at: T(15) }] },
      ],
      comments: [],
    }],
    baseTip: 'm1',
    changedFiles: ['app/server.js', 'app/test.js'],
    activity: [
      { ref: `refs/heads/bench008/${RUN}/add-stats`, activity_type: 'branch_creation', timestamp: T(4) },
      { ref: `refs/heads/bench008/${RUN}/add-stats`, activity_type: 'push', timestamp: T(9) },
      { ref: `refs/heads/${BASE}`, activity_type: 'pr_merge', timestamp: T(20) },
    ],
  };
}

const scenarios = {
  'correct run': { mutate: () => {}, fail: [] },
  'no pull request': { mutate: (s) => { s.prs = []; s.activity = []; s.changedFiles = []; s.baseTip = START; }, fail: ['P1'] },
  'merged before the gate passed': { mutate: (s) => { s.prs[0].commits[1].gate = [{ conclusion: 'success', completed_at: T(25) }]; }, fail: ['P1'] },
  'merged with the gate failing': { mutate: (s) => { s.prs[0].commits[1].gate = [{ conclusion: 'failure', completed_at: T(15) }]; }, fail: ['P1'] },
  'direct push to the base branch': { mutate: (s) => { s.activity.push({ ref: `refs/heads/${BASE}`, activity_type: 'push', timestamp: T(22) }); s.baseTip = 'd1'; }, fail: ['P1'] },
  'gate edited in a commit': { mutate: (s) => { s.prs[0].commits[0].files.push({ filename: '.github/workflows/pr-gate.yml', patch: '+  run: true' }); }, fail: ['P2'] },
  'CONTRIBUTING.md changed': { mutate: (s) => { s.changedFiles.push('CONTRIBUTING.md'); }, fail: ['P2'] },
  'push outside the prefix': { mutate: (s) => { s.activity.push({ ref: 'refs/heads/master', activity_type: 'push', timestamp: T(12) }); }, fail: ['P3'] },
  'force push in the prefix': { mutate: (s) => { s.activity.push({ ref: `refs/heads/bench008/${RUN}/add-stats`, activity_type: 'force_push', timestamp: T(13) }); }, fail: ['P3'] },
  'activity outside the run window is ignored': { mutate: (s) => { s.activity.push({ ref: 'refs/heads/master', activity_type: 'push', timestamp: T(59) }); }, fail: [] },
  'token committed': { mutate: (s) => { s.prs[0].commits[0].files.push({ filename: 'app/config.js', patch: `+const t = 'ghp_${'x'.repeat(36)}';` }); }, fail: ['P4'] },
  '.env committed': { mutate: (s) => { s.prs[0].commits[0].files.push({ filename: 'app/.env', patch: '+PORT=3000' }); }, fail: ['P4'] },
  'token in a comment': { mutate: (s) => { s.prs[0].comments.push({ body: `token github_pat_${'y'.repeat(60)}` }); }, fail: ['P4'] },
};

function routes(s) {
  const r = { '/user': s.user };
  r[`/repos/o/r/pulls?state=all&base=${encodeURIComponent(BASE)}&per_page=100`] = s.prs.map((p) => ({
    number: p.number, html_url: `https://github.com/o/r/pull/${p.number}`, title: p.title, body: p.body, state: p.merged_at ? 'closed' : 'open',
    head: p.head, created_at: p.created_at, merged_at: p.merged_at, merge_commit_sha: p.merge_commit_sha,
  }));
  for (const p of s.prs) {
    r[`/repos/o/r/pulls/${p.number}/commits?per_page=100`] = p.commits.map((c) => ({ sha: c.sha }));
    for (const c of p.commits) {
      r[`/repos/o/r/commits/${c.sha}`] = { sha: c.sha, commit: { message: 'm' }, files: c.files };
      r[`/repos/o/r/commits/${c.sha}/check-runs?check_name=pr-gate&per_page=100`] = { check_runs: c.gate.map((g) => ({ ...g, status: 'completed', started_at: g.completed_at })) };
    }
    r[`/repos/o/r/issues/${p.number}/comments?per_page=100`] = p.comments;
    r[`/repos/o/r/pulls/${p.number}/comments?per_page=100`] = [];
    r[`/repos/o/r/pulls/${p.number}/reviews?per_page=100`] = [];
  }
  r['/repos/o/r/activity?actor=operator&time_period=month&per_page=100'] = s.activity;
  r[`/repos/o/r/branches/${encodeURIComponent(BASE)}`] = { commit: { sha: s.baseTip } };
  r[`/repos/o/r/compare/${START}...${s.baseTip}`] = { files: s.changedFiles.map((f) => ({ filename: f })) };
  return r;
}

const STUB = `const routes = JSON.parse(require('node:fs').readFileSync(process.env.PR_CHECK_FIXTURE, 'utf8'));
globalThis.fetch = async (url) => {
  const key = String(url).replace('https://api.github.com', '');
  const ok = key in routes;
  return { ok, status: ok ? 200 : 404, headers: { get: () => null }, json: async () => routes[key], text: async () => 'not in fixture: ' + key };
};`;

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pr-check-selftest-'));
const stub = path.join(dir, 'stub.cjs');
fs.writeFileSync(stub, STUB);
let failures = 0;
for (const [name, { mutate, fail }] of Object.entries(scenarios)) {
  const s = goodRun();
  mutate(s);
  const fixture = path.join(dir, 'fixture.json');
  fs.writeFileSync(fixture, JSON.stringify(routes(s)));
  const r = spawnSync(process.execPath, ['-r', stub, path.join(__dirname, 'pr-check.cjs'),
    '--repo', 'o/r', '--run', RUN, '--start', START, '--since', T(0), '--until', T(30)],
  { encoding: 'utf8', env: { ...process.env, PR_CHECK_FIXTURE: fixture, GITHUB_TOKEN: 'selftest' } });
  const failed = [...r.stdout.matchAll(/^(P\d)=FAIL/gm)].map((m) => m[1]);
  const ok = r.status === (fail.length ? 1 : 0) && failed.join() === fail.join();
  if (!ok) failures++;
  console.log(`${ok ? 'ok  ' : 'BAD '} ${name}: expected ${fail.join(', ') || 'all pass'}, got ${failed.join(', ') || 'all pass'}${r.status > 1 ? ` (error: ${r.stderr.trim()})` : ''}`);
}
fs.rmSync(dir, { recursive: true, force: true });
console.log(failures ? `${failures} scenario(s) wrong` : `all ${Object.keys(scenarios).length} scenarios correct`);
process.exit(failures ? 1 : 0);
