// Code quality (Q) grader for the todo app, per the SRS scoring table:
// four checks worth 25 points each, comparing the agent's app against the
// task's starting app ("baseline").
//
//   1. lint        no more ESLint violations than the baseline
//   2. complexity  no more functions above cyclomatic complexity 10
//   3. duplication no more duplicated lines (jscpd) than the baseline
//   4. runtime     median of 10 alternating `node --test test.js` runs is at
//                  most 1.2 x the baseline median; a failing candidate suite
//                  fails the check
//
// Only the files agents may change are measured: app/server.js, app/test.js
// and the inline <script> of app/public/index.html.
//
// Usage: node quality-grader.mjs <baseline app dir> <candidate app dir> [out.json]

import { ESLint } from 'eslint';
import js from '@eslint/js';
import globals from 'globals';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const COMPLEXITY_LIMIT = 10;
const RUNTIME_PAIRS = 10;
const RUNTIME_LIMIT = 1.2;

// Pinned rules: eslint:recommended, with unused top-level functions in the
// page script allowed (they are called from onclick attributes) and unused
// route arguments allowed (Express handler signatures).
const RULES = {
  ...js.configs.recommended.rules,
  'no-unused-vars': ['error', { vars: 'local', args: 'none', caughtErrors: 'none' }],
};

// Copies the measured sources into a scratch folder; the page's inline
// scripts become index.inline.js so ESLint and jscpd can read them.
function collect(appDir, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const files = [];
  for (const name of ['server.js', 'test.js']) {
    const src = path.join(appDir, name);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, path.join(dest, name));
      files.push(name);
    }
  }
  const html = path.join(appDir, 'public', 'index.html');
  if (fs.existsSync(html)) {
    const scripts = [...fs.readFileSync(html, 'utf8').matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)]
      .map((m) => m[1]);
    if (scripts.length) {
      fs.writeFileSync(path.join(dest, 'index.inline.js'), scripts.join('\n;\n'));
      files.push('index.inline.js');
    }
  }
  return files;
}

async function lint(dir, files) {
  const eslint = new ESLint({
    cwd: dir,
    overrideConfigFile: true,
    overrideConfig: [
      {
        files: ['server.js', 'test.js'],
        languageOptions: { ecmaVersion: 2023, sourceType: 'commonjs', globals: globals.node },
        rules: { ...RULES, complexity: ['warn', COMPLEXITY_LIMIT] },
      },
      {
        files: ['index.inline.js'],
        languageOptions: { ecmaVersion: 2023, sourceType: 'script', globals: globals.browser },
        rules: { ...RULES, complexity: ['warn', COMPLEXITY_LIMIT] },
      },
    ],
  });
  const results = files.length ? await eslint.lintFiles(files.map((f) => path.join(dir, f))) : [];
  const lintIssues = [];
  const complexFns = [];
  for (const r of results) {
    for (const m of r.messages) {
      const where = `${path.basename(r.filePath)}:${m.line ?? 0}`;
      if (m.ruleId === 'complexity') complexFns.push(`${where} ${m.message}`);
      else lintIssues.push(`${where} ${m.ruleId ?? 'parse-error'}: ${m.message}`);
    }
  }
  return { lintIssues, complexFns };
}

function duplication(dir) {
  const out = path.join(dir, '.jscpd');
  const bin = path.join(HERE, 'node_modules', 'jscpd', 'bin', 'jscpd');
  // Run from inside the folder with a relative path: jscpd finds no files
  // when given an absolute Windows path.
  spawnSync(process.execPath, [bin, '.', '--silent', '--reporters', 'json', '--output', '.jscpd',
    '--format', 'javascript', '--ignore', '**/.jscpd/**', '--min-lines', '5', '--min-tokens', '50'], { cwd: dir, encoding: 'utf8' });
  const report = path.join(out, 'jscpd-report.json');
  if (!fs.existsSync(report)) return { lines: 0, clones: [] };
  const data = JSON.parse(fs.readFileSync(report, 'utf8'));
  return {
    lines: data.statistics?.total?.duplicatedLines ?? 0,
    clones: (data.duplicates || []).map((d) =>
      `${path.basename(d.firstFile.name)}:${d.firstFile.start}-${d.firstFile.end} = ${path.basename(d.secondFile.name)}:${d.secondFile.start}-${d.secondFile.end} (${d.lines} lines)`),
  };
}

function timeSuite(appDir) {
  const start = process.hrtime.bigint();
  const r = spawnSync(process.execPath, ['--test', 'test.js'], { cwd: appDir, encoding: 'utf8', timeout: 120000 });
  return { ms: Number(process.hrtime.bigint() - start) / 1e6, ok: r.status === 0 };
}

const median = (xs) => { const s = [...xs].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

function runtime(baseApp, candApp) {
  if (!fs.existsSync(path.join(candApp, 'test.js'))) return { applicable: false, reason: 'candidate has no test.js' };
  const base = [], cand = [];
  let baseOk = true, candOk = true;
  timeSuite(baseApp); timeSuite(candApp); // warm-up, not recorded
  for (let i = 0; i < RUNTIME_PAIRS; i++) {
    const order = i % 2 ? [['cand', candApp], ['base', baseApp]] : [['base', baseApp], ['cand', candApp]];
    for (const [who, dir] of order) {
      const t = timeSuite(dir);
      (who === 'base' ? base : cand).push(Math.round(t.ms));
      if (!t.ok) who === 'base' ? (baseOk = false) : (candOk = false);
    }
  }
  if (!baseOk) return { applicable: false, reason: 'the baseline test suite does not pass, so there is no valid runtime reference', baseMs: base, candMs: cand, candOk };
  const ratio = median(cand) / median(base);
  return { applicable: true, baseMedian: median(base), candMedian: median(cand), ratio: +ratio.toFixed(3), candOk, baseMs: base, candMs: cand };
}

export async function grade(baseApp, candApp) {
  const work = fs.mkdtempSync(path.join(os.tmpdir(), 'quality-'));
  try {
    const bDir = path.join(work, 'baseline'), cDir = path.join(work, 'candidate');
    const bFiles = collect(baseApp, bDir), cFiles = collect(candApp, cDir);
    const [bl, cl] = [await lint(bDir, bFiles), await lint(cDir, cFiles)];
    const [bd, cd] = [duplication(bDir), duplication(cDir)];
    const rt = runtime(baseApp, candApp);

    const checks = {
      lint: { baseline: bl.lintIssues.length, candidate: cl.lintIssues.length, details: cl.lintIssues },
      complexity: { baseline: bl.complexFns.length, candidate: cl.complexFns.length, details: cl.complexFns },
      duplication: { baseline: bd.lines, candidate: cd.lines, details: cd.clones },
      runtime: rt,
    };
    checks.lint.pass = checks.lint.candidate <= checks.lint.baseline;
    checks.complexity.pass = checks.complexity.candidate <= checks.complexity.baseline;
    checks.duplication.pass = checks.duplication.candidate <= checks.duplication.baseline;
    if (rt.applicable) rt.pass = rt.candOk && rt.ratio <= RUNTIME_LIMIT;

    const scored = Object.values(checks).filter((c) => c.applicable !== false);
    const points = scored.filter((c) => c.pass).length * 25;
    return {
      grader: 'code-quality 1.0.0', eslint: ESLint.version, complexityLimit: COMPLEXITY_LIMIT,
      runtimePairs: RUNTIME_PAIRS, runtimeLimit: RUNTIME_LIMIT,
      measuredFiles: cFiles, checks, points, possible: scored.length * 25,
      score: +(points / (scored.length * 25) * 100).toFixed(1),
    };
  } finally {
    fs.rmSync(work, { recursive: true, force: true });
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [base, cand, out] = process.argv.slice(2);
  if (!base || !cand) { console.error('Usage: node quality-grader.mjs <baseline app> <candidate app> [out.json]'); process.exit(2); }
  const result = await grade(path.resolve(base), path.resolve(cand));
  const text = JSON.stringify(result, null, 2);
  if (out) fs.writeFileSync(out, text + '\n'); else console.log(text);
  for (const [k, c] of Object.entries(result.checks)) {
    console.error(`${k.padEnd(12)} ${c.applicable === false ? 'n/a  ' + c.reason : (c.pass ? 'PASS' : 'FAIL') + `  baseline ${c.baseline ?? c.baseMedian} candidate ${c.candidate ?? c.candMedian}${c.ratio ? ` ratio ${c.ratio}` : ''}`}`);
  }
  console.error(`score ${result.score} (${result.points}/${result.possible})`);
}
