// Scores code quality for every saved run under benchmark-results/<tool>/<run>/.
// Each run's preserved original files are laid over its task's starting app
// and compared with that starting app using quality-grader.mjs.
//
// Usage (from this folder, on the results/all-runs branch):
//   npm ci
//   node score-runs.mjs
//
// Writes quality.json into each run folder, and scores.json + scores.md here.
//
// To score only some runs and keep the others' existing quality.json:
//   node score-runs.mjs --only codex/validation-run01,codex/validation-run02

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { grade } from './quality-grader.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '../../..');
const RESULTS = path.join(REPO, 'benchmark-results');
const WORK = path.join(HERE, 'work', 'runs');

// The starting app each task's runs were given (same commits as the dashboard).
const TASKS = [
  { id: '001', dir: /^run\d+$/, base: 'be98d692807da26dac3c3a720d4d5cf157e9717d' },
  { id: '002', dir: /^validation-run\d+$/, base: '4fa0659150b42fc9b01b1e68e51f07a8535c57e0' },
  { id: '003', dir: /^edit-run\d+$/, base: '4e258a96855d98edd10247f68c0b8265e53a8921' },
  { id: '004', dir: /^bugfix-run\d+$/, base: '1e690f91a11dd1b37c796345a511d6791476efbc' },
  { id: '005', dir: /^injection-run\d+$/, base: 'cef49cca7a3298cda4dc18660b434c60d871e2e7' },
];
const APP_FILES = ['server.js', 'test.js', 'index.html'];

function exportApp(commit, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const tar = execFileSync('git', ['-C', REPO, 'archive', commit, 'app'], { maxBuffer: 64 << 20 });
  // Extract with cwd set: Windows tar reads a C:\ path as a remote host.
  execFileSync('tar', ['-x', '--strip-components=1'], { cwd: dest, input: tar });
}

// Same lookup as the dashboard: original/<f>, original-<f>, or <prefix>-original-<f>.
function originalFile(runDir, name) {
  for (const c of [`original/${name}`, `original-${name}`]) {
    if (fs.existsSync(path.join(runDir, c))) return path.join(runDir, c);
  }
  const hit = fs.readdirSync(runDir).find((f) => f.endsWith(`-original-${name}`));
  return hit ? path.join(runDir, hit) : null;
}

const onlyArg = process.argv.indexOf('--only');
const ONLY = onlyArg > -1 ? new Set(process.argv[onlyArg + 1].split(',')) : null;

function rowOf(run, taskId, result) {
  const c = result.checks;
  return {
    run, task: taskId, score: result.score, possible: result.possible,
    lint: `${c.lint.baseline}→${c.lint.candidate}`, lintPass: c.lint.pass,
    complexity: `${c.complexity.baseline}→${c.complexity.candidate}`, complexityPass: c.complexity.pass,
    duplication: `${c.duplication.baseline}→${c.duplication.candidate}`, duplicationPass: c.duplication.pass,
    runtime: c.runtime.applicable ? `${c.runtime.ratio}×` : 'n/a', runtimePass: c.runtime.applicable ? c.runtime.pass : null,
  };
}

fs.rmSync(WORK, { recursive: true, force: true });
const baselines = {};
const rows = [];

for (const tool of fs.readdirSync(RESULTS).filter((d) => d !== 'protocol' && fs.statSync(path.join(RESULTS, d)).isDirectory())) {
  for (const run of fs.readdirSync(path.join(RESULTS, tool))) {
    const runDir = path.join(RESULTS, tool, run);
    const task = TASKS.find((t) => t.dir.test(run));
    if (!task || !fs.statSync(runDir).isDirectory()) continue;
    const existing = path.join(runDir, 'quality.json');
    if (ONLY && !ONLY.has(`${tool}/${run}`)) {
      if (fs.existsSync(existing)) rows.push(rowOf(`${tool}/${run}`, task.id, JSON.parse(fs.readFileSync(existing, 'utf8').replace(/^﻿/, ''))));
      continue;
    }

    if (!baselines[task.id]) {
      baselines[task.id] = path.join(WORK, `baseline-${task.id}`);
      exportApp(task.base, baselines[task.id]);
    }
    const cand = path.join(WORK, `${tool}-${run}`);
    exportApp(task.base, cand);
    const used = [];
    for (const name of APP_FILES) {
      const src = originalFile(runDir, name);
      if (!src) continue;
      fs.copyFileSync(src, name === 'index.html' ? path.join(cand, 'public', name) : path.join(cand, name));
      used.push(path.relative(runDir, src).replace(/\\/g, '/'));
    }
    if (!used.length) { console.log(`skip ${tool}/${run}: no original files`); continue; }

    process.stdout.write(`${tool}/${run} (task ${task.id}) ... `);
    const result = await grade(baselines[task.id], cand);
    result.task = task.id;
    result.baselineCommit = task.base;
    result.originalFiles = used;
    result.gradedAt = new Date().toISOString();
    fs.writeFileSync(path.join(runDir, 'quality.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(`${result.score}`);
    rows.push(rowOf(`${tool}/${run}`, task.id, result));
  }
}

rows.sort((a, b) => a.task.localeCompare(b.task) || a.run.localeCompare(b.run));
fs.writeFileSync(path.join(HERE, 'scores.json'), JSON.stringify(rows, null, 2) + '\n');
const mark = (v) => (v == null ? '—' : v ? '✔' : '✖');
const md = [
  '# Code quality scores for saved runs',
  '',
  `Generated ${new Date().toISOString().slice(0, 10)} by \`score-runs.mjs\`. Each cell shows starting app → agent's app. See [README.md](README.md) for the rules.`,
  '',
  '| Task | Run | Score | Lint violations | Functions over complexity 10 | Duplicated lines | Test runtime |',
  '|---|---|---:|---|---|---|---|',
  ...rows.map((r) => `| ${r.task} | ${r.run} | ${r.score} | ${mark(r.lintPass)} ${r.lint} | ${mark(r.complexityPass)} ${r.complexity} | ${mark(r.duplicationPass)} ${r.duplication} | ${mark(r.runtimePass)} ${r.runtime} |`),
  '',
].join('\n');
fs.writeFileSync(path.join(HERE, 'scores.md'), md);
console.log(`Scored ${rows.length} runs; wrote scores.json and scores.md`);
