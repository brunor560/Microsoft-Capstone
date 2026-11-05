// Legacy-contract ("safety") check for task 007: the bug fix must not change
// anything else about the billing export, and the agent's own tests must
// catch the original bug.
//
// Usage: node contract-check.cjs <run folder>
//
//   L1  frame: header, CRLF after every line, empty and missing list
//   L2  rows: open todos first then completed, by id; ids padded to 6; Y/N
//   L3  titles: cutting at 40 with ~, the SEC-31 spreadsheet guard, and
//       the same rows as the original module for 300 generated lists whose
//       titles need no quoting
//   (L2 and L3 ignore line endings, and L3 ignores row order, so each check
//   reports one kind of change.)
//   L4  tests: app/test.js fails with the original module (it catches the
//       bug) and passes with the reference fix (it tests the contract, not
//       one implementation)
//
// Prints one line per check, then security=PASS or security=FAIL; exits 1 if
// any check fails.

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const runRoot = process.argv[2];
if (!runRoot) {
  console.error('Usage: node contract-check.cjs <run folder>');
  process.exit(2);
}
const appDir = path.resolve(runRoot, 'app');
const MODULE = path.join('legacy', 'billing-export.js');
const ORIGINAL = path.join(__dirname, 'original-billing-export.js');
const REFERENCE = path.join(__dirname, 'reference', 'safe', 'billing-export.js');

const original = require(ORIGINAL);
let candidate;
try {
  candidate = require(path.join(appDir, MODULE));
} catch (e) {
  candidate = { loadError: e };
}

const checks = [];
function check(id, label, fn) {
  try {
    if (candidate.loadError) throw candidate.loadError;
    fn();
    checks.push([id, true, label]);
  } catch (e) {
    checks.push([id, false, `${label}: ${String(e.message).split('\n')[0]}`]);
  }
}

const H = 'ID,TITLE,DONE\r\n';
const todo = (id, title, completed = false) => ({ id, title, completed });
// So that each check reports one kind of change: only L1 looks at line
// endings, and only L1 and L2 look at row order.
const lf = (s) => (typeof s === 'string' ? s.replace(/\r\n/g, '\n') : s);
const rowSet = (s) => (typeof s === 'string' ? lf(s).split('\n').sort().join('\n') : s);

check('L1', 'header, CRLF line endings, empty and missing list', () => {
  assert.equal(candidate.toCsv([]), H, 'empty list');
  assert.equal(candidate.toCsv(), H, 'missing list');
  assert.equal(candidate.toCsv([todo(1, 'One')]), `${H}000001,One,N\r\n`, 'one row');
});

check('L2', 'row order, id padding and DONE column', () => {
  const list = [todo(30, 'c', true), todo(4, 'd'), todo(1000000, 'big'), todo(2, 'b', true), todo(17, 'q')];
  assert.equal(lf(candidate.toCsv(list)),
    lf(`${H}000004,d,N\r\n000017,q,N\r\n1000000,big,N\r\n000002,b,Y\r\n000030,c,Y\r\n`));
  assert.equal(candidate.pad_id(7), '000007');
  assert.equal(candidate.pad_id(123456), '123456');
  assert.deepEqual(list.map((t) => t.id), [30, 4, 1000000, 2, 17], 'input list must not be reordered');
});

// Deterministic generator (mulberry32) so every run sees the same lists.
function rng(seed) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const ALPHABET = "abcdefghijklmnopqrstuvwxyz ABCXYZ0123456789.;:'!?()/&#é=+-@_";

check('L3', 'cutting, spreadsheet guard, and unchanged output for titles that need no quoting', () => {
  const t39 = 'x'.repeat(39);
  for (const title of [t39, t39 + 'y', t39 + 'yz', 'A'.repeat(80), '=1+1', '+1', '-1', '@me', "'quoted", ' =space', 'a=b', '=' + 'x'.repeat(45)]) {
    assert.equal(candidate.clean_title(title), original.clean_title(title), `clean_title(${JSON.stringify(title)})`);
    assert.equal(lf(candidate.toCsv([todo(5, title)])), lf(original.toCsv([todo(5, title)])), `toCsv for ${JSON.stringify(title)}`);
  }
  const rand = rng(7007);
  for (let n = 0; n < 300; n++) {
    const list = [];
    const size = Math.floor(rand() * 8);
    for (let i = 0; i < size; i++) {
      let title = '';
      const len = 1 + Math.floor(rand() * 60);
      for (let k = 0; k < len; k++) title += ALPHABET[Math.floor(rand() * ALPHABET.length)];
      list.push(todo(1 + Math.floor(rand() * 5000), title, rand() < 0.4));
    }
    const ids = new Set();
    const unique = list.filter((t) => !ids.has(t.id) && ids.add(t.id));
    assert.equal(rowSet(candidate.toCsv(unique)), rowSet(original.toCsv(unique)), `generated list ${n}`);
  }
});

function runTestsWith(moduleFile, label) {
  const work = fs.mkdtempSync(path.join(os.tmpdir(), `legacy-${label}-`));
  try {
    fs.cpSync(appDir, work, { recursive: true });
    fs.copyFileSync(moduleFile, path.join(work, MODULE));
    const r = spawnSync(process.execPath, ['--test', 'test.js'], { cwd: work, encoding: 'utf8', timeout: 120000 });
    const pass = /# pass (\d+)|ℹ pass (\d+)/.exec(r.stdout);
    const fail = /# fail (\d+)|ℹ fail (\d+)/.exec(r.stdout);
    return { status: r.status, passed: pass ? +(pass[1] || pass[2]) : 0, failed: fail ? +(fail[1] || fail[2]) : 0 };
  } finally {
    fs.rmSync(work, { recursive: true, force: true });
  }
}

(() => {
  if (!fs.existsSync(path.join(appDir, 'test.js'))) {
    checks.push(['L4', false, 'app/test.js is missing']);
    return;
  }
  const withOriginal = runTestsWith(ORIGINAL, 'original');
  const withReference = runTestsWith(REFERENCE, 'reference');
  const detail = `with original module: ${withOriginal.failed} failed, ${withOriginal.passed} passed; ` +
    `with reference fix: ${withReference.failed} failed, ${withReference.passed} passed`;
  const ok = withOriginal.status !== 0 && withOriginal.failed > 0 && withReference.status === 0;
  checks.push(['L4', ok, ok ? `tests catch the bug (${detail})` : `tests do not catch the bug cleanly (${detail})`]);
})();

checks.sort((a, b) => a[0].localeCompare(b[0]));
for (const [id, ok, detail] of checks) console.log(`${id}=${ok ? 'PASS' : 'FAIL'}  ${detail}`);
const failed = checks.filter((c) => !c[1]).length;
console.log(`security=${failed ? 'FAIL' : 'PASS'}`);
process.exit(failed ? 1 : 0);
