// Builds dashboard/data.js from the results/all-runs branch.
// Usage: node dashboard/build-data.mjs [branch]   (default origin/results/all-runs)
import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const BRANCH = process.argv[2] || 'origin/results/all-runs';
const ROOT = 'benchmark-results';
const git = (...a) => execFileSync('git', a, { encoding: 'utf8', maxBuffer: 64 << 20, stdio: ['ignore', 'pipe', 'ignore'] });
// Some Windows logs were captured through a CP437 console; undo the common mojibake
const MOJIBAKE = [['Γ£ö', '✔'], ['Γ£û', '✖'], ['Γä╣', 'ℹ'], ['ΓÇö', '—'], ['ΓÇÖ', '’'], ['ΓåÆ', '→'], ['Γû╢', '▶'], ['Γ£ô', '✓'], ['Γ£ÿ', '✘'], ['ΓÇ║', '›']];
const fix = (t) => MOJIBAKE.reduce((s, [a, b]) => s.split(a).join(b), t.replace(/^﻿/, ''));
const decode = (buf) => (buf[0] === 0xff && buf[1] === 0xfe ? buf.toString('utf16le') : buf.toString('utf8'));
const show = (ref, p) => {
  if (!p) return null;
  try {
    const buf = execFileSync('git', ['show', `${ref}:${p}`], { maxBuffer: 64 << 20, stdio: ['ignore', 'pipe', 'ignore'] });
    return fix(decode(buf)).replace(/\x1b\[[0-9;]*m/g, '');
  } catch { return null; }
};
const ls = (ref, p) => { try { return git('ls-tree', '-r', '--name-only', ref, p).split('\n').filter(Boolean); } catch { return []; } };

const TASKS = [
  { id: '001', name: 'Add DELETE endpoint', short: 'Delete', dir: /^run\d+$/, base: 'be98d692807da26dac3c3a720d4d5cf157e9717d', taskFile: 'pipeline/tasks/001-add-delete-endpoint.md', tokenLimit: 300000 },
  { id: '003', name: 'Edit todo title', short: 'Edit title', dir: /^edit-run\d+$/, base: '4e258a96855d98edd10247f68c0b8265e53a8921', taskFile: 'pipeline/tasks/003-edit-todo-title.md', tokenLimit: 500000 },
  { id: '004', name: 'Fix update validation', short: 'Update bugfix', dir: /^bugfix-run\d+$/, base: '1e690f91a11dd1b37c796345a511d6791476efbc', taskFile: 'pipeline/tasks/004-fix-update-validation.md', tokenLimit: 400000 },
  { id: '005', name: 'Todo priority (prompt-injection traps)', short: 'Injection', dir: /^injection-run\d+$/, base: 'cef49cca7a3298cda4dc18660b434c60d871e2e7', taskFile: 'pipeline/tasks/005-todo-priority.md', tokenLimit: 400000 },
];
const TOOLS = [
  { id: 'antigravity', name: 'Antigravity' },
  { id: 'antigravity-cli', name: 'Antigravity CLI' },
  { id: 'claude', name: 'Claude Code' },
  { id: 'codex', name: 'Codex' },
  { id: 'copilot', name: 'Copilot' },
];
const APP_FILES = ['app/server.js', 'app/test.js', 'app/public/index.html'];

function kv(text) {
  const o = {};
  for (const line of (text || '').split(/\r?\n/)) {
    for (const m of line.matchAll(/([A-Za-z_]+)=(\S+)/g)) o[m[1]] = m[2];
  }
  return o;
}

function counts(log) {
  if (!log) return {};
  let m;
  const r = {};
  if ((m = log.match(/ℹ pass (\d+)/))) r.pass = +m[1];
  if ((m = log.match(/ℹ fail (\d+)/))) r.fail = +m[1];
  if (r.pass == null && (m = log.match(/^# pass (\d+)/m))) r.pass = +m[1];
  if (r.fail == null && (m = log.match(/^# fail (\d+)/m))) r.fail = +m[1];
  if (r.pass == null && (m = log.match(/(\d+) passed/))) r.pass = +m[1];
  if (r.fail == null && (m = log.match(/(\d+) failed/))) r.fail = +m[1];
  if (r.pass == null && /\bPASS\b/.test(log) && !/\bFAIL\b/.test(log)) r.verdict = 'PASS';
  if (r.pass != null && r.fail == null) r.fail = 0;
  return r;
}

// Individual test lines for the replay
function testLines(log) {
  if (!log) return [];
  const out = [];
  for (const raw of log.split(/\r?\n/)) {
    const l = raw.replace(/\s+\([\d.]+m?s\)\s*$/, '');
    let m;
    if ((m = l.match(/^(\s*)[✔]\s+(.*)$/))) out.push({ ok: true, depth: m[1].length, name: m[2] });
    else if ((m = l.match(/^(\s*)[✖✗]\s+(.*)$/))) out.push({ ok: false, depth: m[1].length, name: m[2] });
    else if ((m = l.match(/^\s*([✓✘])\s+\d+\s+.*? › (.*)$/))) out.push({ ok: m[1] === '✓', depth: 0, name: m[2] });
    else if ((m = l.match(/^\s*ok \d+ (?:.*? › |- )(.*)$/))) out.push({ ok: true, depth: 0, name: m[1] });
    else if ((m = l.match(/^\s*not ok \d+ (?:.*? › |- )(.*)$/))) out.push({ ok: false, depth: 0, name: m[1] });
    else if ((m = l.match(/^\s*(PASS|FAIL|REVIEW|NOTE)[: ]\s*(.+)$/))) out.push({ ok: m[1] !== 'FAIL', depth: 0, name: `${m[1]} ${m[2]}` });
  }
  return out;
}

const SUITE_NAMES = {
  local: 'Agent\'s own tests', api: 'Independent API tests', browser: 'Independent browser tests',
  acceptance: 'Acceptance tests', supplemental: 'Supplemental tests',
  security_runtime: 'Runtime security tests', security_scan: 'Static security scan',
};
const SUITE_FILES = {
  local: ['original-local-tests.txt', 'verification-local-tests.txt', 'verification-*/original-local-tests.txt'],
  api: ['original-api-tests.txt'],
  browser: ['original-browser-tests.txt'],
  acceptance: ['original-acceptance.txt', 'verification-acceptance.txt', 'verification-*/original-acceptance.txt'],
  supplemental: ['original-supplemental.txt', 'verification-supplemental.txt', 'verification-*/original-supplemental.txt'],
  security_runtime: ['original-security-runtime.txt'],
  security_scan: ['original-security-scan.txt'],
};
// A run regraded after an evaluator fix keeps its original logs as evidence and adds
// regrade-fixed-grader-<suite>.txt plus regrade-fixed-grader-exits.txt. The regrade is the
// result to report, so it takes precedence for the suites it covers.
const REGRADE_FILES = {
  api: 'regrade-fixed-grader-api-tests.txt',
  browser: 'regrade-fixed-grader-browser-tests.txt',
  security_runtime: 'regrade-fixed-grader-security-runtime.txt',
  security_scan: 'regrade-fixed-grader-security-scan.txt',
};

function findFile(files, dir, pattern) {
  const re = new RegExp('^' + pattern.replace(/[.]/g, '\\.').replace('*', '[^/]+') + '$');
  return files.find((f) => re.test(f.slice(dir.length + 1)));
}

function originalFor(files, dir, appPath) {
  const base = path.basename(appPath);
  const cands = [
    `original/${base}`, `original-${base}`,
  ];
  for (const c of cands) if (files.includes(`${dir}/${c}`)) return `${dir}/${c}`;
  return files.find((f) => f.startsWith(dir + '/') && f.endsWith(`-original-${base}`)) || null;
}

function mdSection(md, heading) {
  if (!md) return null;
  const re = new RegExp(`^#+\\s*${heading}[^\\n]*\\n([\\s\\S]*?)(?=^#+\\s|$(?![\\s\\S]))`, 'mi');
  const m = md.match(re);
  return m ? m[1].trim() : null;
}

function codeBlock(md) {
  const m = md && md.match(/```[a-z]*\n([\s\S]*?)```/);
  return m ? m[1].trim() : null;
}

function traps(md) {
  if (!md) return [];
  const m = md.match(/\|\s*Trap\s*\|[^\n]*\n\|[-| ]+\|\n((?:\|[^\n]*\n?)+)/i);
  if (!m) return [];
  return m[1].trim().split('\n').map((row) => {
    const c = row.split('|').slice(1, -1).map((s) => s.trim());
    return { trap: c[0], result: c[1], disclosure: c[2] };
  });
}

function tokens(json) {
  if (!json) return null;
  let t;
  try { t = JSON.parse(json); } catch { return null; }
  const u = t.recorded_usage || t.usage || t;
  const input = u.input_tokens_field_sum ?? u.input_tokens;
  const cached = u.cache_read_tokens_field_sum ?? u.cached_input_tokens ?? u.cache_read_input_tokens;
  const output = u.output_tokens_field_sum ?? u.output_tokens;
  const cacheCreate = u.cache_creation_input_tokens || 0;
  // Claude reports uncached input separately from cache reads/creations (cache_read_input_tokens),
  // so those are added. OpenAI/Codex cached_input_tokens is already part of input_tokens, so it is not.
  // (Antigravity's *_field_sum counts are left as input + output, as before: its cache accounting is unverified.)
  const separateCache = u.cache_read_input_tokens != null;
  const reconstructed = /reconstructed/i.test(t.measurement_type || '') || u.input_tokens_field_sum != null;
  const accountingUnverified = reconstructed || /not independently verified|unverified/i.test(t.cache_accounting || '');
  const inputPlusOutput = t.input_plus_output_tokens ?? ((input || 0) + (output || 0));
  const scoringProvisional = accountingUnverified && t.scoring_policy === 'cache_reads_separate_provisional';
  const assumedTotal = inputPlusOutput + (cached || 0) + (u.cache_creation_tokens_field_sum || 0);
  const total = scoringProvisional ? assumedTotal : accountingUnverified ? null : u.total_tokens ?? ((input || 0) + (separateCache ? (cached || 0) + cacheCreate : 0) + (output || 0));
  return { input, cached, output, total, inputPlusOutput, reconstructed, accountingUnverified, scoringProvisional, measurementType: t.measurement_type || null, cacheAccounting: t.cache_accounting || null, cost: t.total_cost_usd ?? null, model: t.model || null, turns: t.num_turns ?? null };
}

// Model and reasoning effort, from whichever run record names them
const MODEL_PATTERNS = [
  /^model=(.+)$/m,
  /^model_requested=(.+)$/m,
  /^displayed_model=(.+)$/m,
  /^Model:\s*([^;\n]+)/m,
  /Observed coding model:\s*`([^`]+)`/,
  /resolved to ([^|\n]+?)\s*\|/,
  /\|\s*Model[^|]*\|\s*`([^`]+)`/,
  /\|\s*Model[^|]*\|\s*([^|(`\n]+?)\s*(?:\(`|\/|\|)/,
  /used its default,?:? `([^`]+)`/,
  /ran [^(\n]+\(`([^`]+)`\)/,
  /^-?\s*(?:Displayed )?[Mm]odel:\s*([^,\n]+)/m,
];
const PRETTY = { 'gpt-6.1-sol': 'GPT-6.1 Sol', 'gpt-6-luna': 'GPT-6 Luna', 'claude-sonnet-5-5': 'Claude Sonnet 5.5' };
function modelInfo(dir) {
  const srcs = ['session-configuration.txt', 'run-configuration.txt', 'run-configuration.md', 'setup.txt', 'README.md'].map((f) => show(BRANCH, `${dir}/${f}`)).filter(Boolean);
  let model = null;
  for (const src of srcs) {
    for (const re of MODEL_PATTERNS) {
      const m = src.match(re);
      if (m && !/unknown|auto$/i.test(m[1].trim())) { model = m[1].trim().replace(/\s+$/, ''); break; }
    }
    if (model) break;
  }
  if (model) model = PRETTY[model] || model;
  const all = srcs.join('\n');
  const e = all.match(/reasoning[^\n]{0,20}?\b(low|medium|high|xhigh)\b/i) || all.match(/\b(low|medium|high)\b[^\n]{0,12}reasoning/i) || all.match(/Reasoning effort:\s*(\w+)/i) || all.match(/\((Thinking)\)/);
  return { model, effort: e ? e[1].toLowerCase() : null };
}

// Code quality from benchmark-results/protocol/code-quality (quality.json in the run folder).
// Human-collaboration and operator records (RUN-RECORD.md sections 4 and 4a).
function jsonFile(dir, name) {
  const text = show(BRANCH, `${dir}/${name}`);
  if (!text) return null;
  try { return JSON.parse(text); } catch { return { invalid: true }; }
}

function quality(dir) {
  const text = show(BRANCH, `${dir}/quality.json`);
  if (!text) return null;
  let q;
  try { q = JSON.parse(text); } catch { return null; }
  const keep = (c) => c && ({ ...c, details: (c.details || []).slice(0, 20) });
  return { score: q.score, points: q.points, possible: q.possible, grader: q.grader, baselineCommit: q.baselineCommit,
    checks: { lint: keep(q.checks.lint), complexity: keep(q.checks.complexity), duplication: keep(q.checks.duplication),
      runtime: q.checks.runtime && { ...q.checks.runtime, baseMs: undefined, candMs: undefined } } };
}

// Was the agent told that code quality is graded? Task files gained a "How your work is
// graded" section on 2026-10-24. If the run recorded its snapshot commit, check that commit's
// task file; otherwise the run predates the section (every run without a recorded commit does).
const GRADING_SECTION = /^## How your work is graded/m;
function qualityNotice(files, dir, task) {
  const f = files.find((x) => /(^|\/)source-commits\.txt$/.test(x.slice(dir.length + 1)))
    || files.find((x) => x === `${dir}/setup.txt`);
  const commit = f && (show(BRANCH, f) || '').match(/^(?:baseline|snapshot|start)_commit=([0-9a-f]{7,40})/m)?.[1];
  if (!commit) return { told: false, commit: null, basis: 'no snapshot commit recorded; the run predates the grading section in task files' };
  const spec = show(commit, task.taskFile);
  if (spec == null) return { told: false, commit, basis: `task file not found at ${commit.slice(0, 7)}` };
  return GRADING_SECTION.test(spec)
    ? { told: true, commit, basis: `the task file at ${commit.slice(0, 7)} has the "How your work is graded" section` }
    : { told: false, commit, basis: `the task file at ${commit.slice(0, 7)} has no grading section` };
}

function elapsed(files, dir) {
  for (const f of ['timing.txt', 'original-timing.txt', 'conversation/timing.txt']) {
    const t = show(BRANCH, `${dir}/${f}`);
    if (!t) continue;
    const o = kv(t);
    const s = o.elapsed_seconds || o.elapsed_s;
    if (s) return { seconds: +(+s).toFixed(1), method: (t.match(/method=(.*)/) || [])[1] || null };
  }
  return null;
}

const tree = ls(BRANCH, ROOT);
const runs = [];

for (const tool of TOOLS) {
  const dirs = [...new Set(tree.filter((f) => f.startsWith(`${ROOT}/${tool.id}/`)).map((f) => f.split('/')[2]))].filter((d) => !d.includes('.'));
  for (const d of dirs) {
    const task = TASKS.find((t) => t.dir.test(d));
    if (!task) continue;
    const dir = `${ROOT}/${tool.id}/${d}`;
    const files = tree.filter((f) => f.startsWith(dir + '/'));
    const readme = show(BRANCH, `${dir}/README.md`);
    const exits = kv(show(BRANCH, `${dir}/original-test-exits.txt`)
      || show(BRANCH, files.find((f) => f.endsWith('original-test-exits.txt')) || '') || '');

    const regradeExits = kv(show(BRANCH, `${dir}/regrade-fixed-grader-exits.txt`) || '');
    const regrade = regradeExits.grader_commit
      ? { commit: regradeExits.grader_commit, date: regradeExits.graded_utc || null, original: [] } : null;

    const suite = (key, log, exit) => {
      const c = counts(log);
      const ok = exit != null ? exit === '0' : (c.fail === 0 || c.verdict === 'PASS');
      return { key, name: SUITE_NAMES[key], exit: exit ?? null, ok, ...c, tests: testLines(log), log: log ? log.slice(0, 20000) : null };
    };
    const suites = [];
    for (const [key, pats] of Object.entries(SUITE_FILES)) {
      let f = null;
      for (const p of pats) if ((f = findFile(files, dir, p))) break;
      const log = f ? show(BRANCH, f) : null;
      const exit = exits[`${key}_exit`];
      const re = regrade && REGRADE_FILES[key] && files.includes(`${dir}/${REGRADE_FILES[key]}`)
        ? show(BRANCH, `${dir}/${REGRADE_FILES[key]}`) : null;
      if (re != null) {
        const s = suite(key, re, regradeExits[`${key}_exit`]);
        suites.push({ ...s, regraded: true });
        if (log || exit != null) {
          const o = suite(key, log, exit);
          regrade.original.push({ key, name: o.name, pass: o.pass ?? null, fail: o.fail ?? null, verdict: o.verdict ?? null, exit: o.exit, ok: o.ok, changed: o.ok !== s.ok || o.pass !== s.pass });
        }
        continue;
      }
      if (!log && exit == null) continue;
      suites.push(suite(key, log, exit));
    }

    const changed = [];
    for (const app of APP_FILES) {
      const orig = originalFor(files, dir, app);
      if (!orig) continue;
      const before = show(task.base, app) ?? '';
      const after = show(BRANCH, orig) ?? '';
      if (before.replace(/\r\n/g, '\n') === after.replace(/\r\n/g, '\n')) continue;
      changed.push({ path: app, before: before.replace(/\r\n/g, '\n'), after: after.replace(/\r\n/g, '\n') });
    }

    const prompt = show(BRANCH, `${dir}/conversation/initial-prompt.txt`) || show(BRANCH, `${dir}/initial-prompt.txt`)
      || show(BRANCH, `${dir}/prompt.txt`) || codeBlock(mdSection(readme, 'Initial prompt'));
    const report = show(BRANCH, `${dir}/conversation/final-report.txt`) || show(BRANCH, `${dir}/final-report.txt`)
      || show(BRANCH, files.find((f) => f.endsWith('final-report.txt')) || '');
    const allOk = suites.length > 0 && suites.every((s) => s.ok);
    const sha = git('log', '-1', '--format=%h|%cs', BRANCH, '--', dir).trim().split('|');
    const approvalNotes = show(BRANCH, `${dir}/approval-notes.txt`);
    const approvalFields = kv(approvalNotes);

    runs.push({
      id: `${tool.id}-${d}`, tool: tool.id, task: task.id, run: d,
      status: allOk ? 'pass' : suites.length ? 'fail' : 'unknown',
      title: (readme || '').split('\n')[0].replace(/^#\s*/, ''),
      summary: (readme || '').split('\n').slice(1).find((l) => l.trim() && !l.startsWith('#') && !l.startsWith('|')) || '',
      ...modelInfo(dir), suites, timing: elapsed(files, dir), tokens: tokens(show(BRANCH, `${dir}/token-usage.json`)),
      approvalNotes, approvalCount: approvalFields.approval_count != null ? Number(approvalFields.approval_count) : null,
      correctivePromptCount: approvalFields.human_corrective_prompt_count != null ? Number(approvalFields.human_corrective_prompt_count) : null,
      changed, prompt, report, traps: traps(readme), readme, regrade, quality: quality(dir), qualityNotice: qualityNotice(files, dir, task), interventions: jsonFile(dir, 'interventions.json'), hReview: jsonFile(dir, 'h-review.json'), operator: jsonFile(dir, 'operator.json'),
      commit: sha[0], date: sha[1], path: dir,
      url: `https://github.com/brunor560/Microsoft-Capstone/tree/${BRANCH.replace(/^origin\//, '')}/${dir}`,
    });
  }
}

// The starting app's files, so the dashboard can run the before and after apps side by side.
const tasks = TASKS.map(({ dir, ...t }) => ({ ...t, spec: show(t.base, t.taskFile) || show('origin/benchmark-start-v2-edit', t.taskFile),
  app: { server: (show(t.base, 'app/server.js') || '').replace(/\r\n/g, '\n'), html: (show(t.base, 'app/public/index.html') || '').replace(/\r\n/g, '\n') } }));
const data = { generated: new Date().toISOString(), branch: BRANCH, branchCommit: git('rev-parse', '--short', BRANCH).trim(), tools: TOOLS, tasks, runs };
const out = path.join(path.dirname(fileURLToPath(import.meta.url)), 'data.js');
writeFileSync(out, `window.BENCH_DATA = ${JSON.stringify(data)};\n`);
console.log(`Wrote ${runs.length} runs to ${out}`);
for (const r of runs) console.log(`  ${r.tool.padEnd(12)} ${r.task} ${r.run.padEnd(16)} ${r.status.padEnd(5)} suites=${r.suites.map((s) => `${s.key}:${s.pass ?? s.verdict ?? '?'}/${s.fail ?? '-'}`).join(' ')} files=${r.changed.length} t=${r.timing?.seconds ?? '-'} tok=${r.tokens?.total ?? '-'}`);
