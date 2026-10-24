# Code quality (Q) grader

Scores the **code quality** dimension of the benchmark (20% of the total)
for the todo app. It compares the agent's final code with the task's
starting code, using the four checks in the SRS scoring table, worth 25
points each.

| Check | Passes when | Tool |
|---|---|---|
| **Lint** | the agent's code has no more ESLint violations than the starting code | ESLint 9.17.0, `eslint:recommended` |
| **Complexity** | no more functions above cyclomatic complexity 10 than the starting code | ESLint `complexity` rule, limit 10 |
| **Duplication** | no more duplicated lines than the starting code | jscpd 4.0.5, at least 5 lines and 50 tokens per clone |
| **Runtime** | the agent's `node --test test.js` median is at most 1.2 × the starting code's, over 10 alternating pairs after one warm-up each, and the agent's suite passes | Node test runner |

Score = 25 × checks passed ÷ checks that apply × 100. Runtime does not apply
if the starting code's own test suite fails, because then there is no valid
reference. That has not happened for any saved run.

**What is measured:** only the files agents may change, which are
`app/server.js`, `app/test.js`, and the inline `<script>` in
`app/public/index.html`. Files the agent didn't change are taken from the
starting app.

## Differences from the SRS wording

- **Lint instead of a formatter.** The SRS says "no new formatter
  violations". The starting app was never formatted with a tool, so a
  formatter such as Prettier would flag every original file. ESLint's
  recommended rules measure real problems (unused variables, `debugger`,
  empty blocks, unreachable code) and compare cleanly with the starting code.
- **Two rule adjustments**, so normal code isn't punished:
  - Top-level functions in the page script may look unused, because
    `onclick` attributes call them.
  - Unused route arguments (`req`, `next`) are allowed.
- **Counts, not names.** Complexity compares the number of functions above
  10, because route handlers are anonymous arrow functions with no stable
  name.

## Files

| File | Purpose |
|---|---|
| `quality-grader.mjs` | Grades one app against a starting app |
| `score-runs.mjs` | Scores every saved run in `benchmark-results/<tool>/<run>/` |
| `scores.md`, `scores.json` | Results for all saved runs |
| `validation.txt` | Planted-defect validation and runtime repeatability |
| `package.json`, `package-lock.json` | Pinned tool versions |

Each scored run folder also gets a `quality.json` with the full details: the
lint messages, which functions are too complex, where the duplicated lines
are, and every runtime sample.

## Run it

From this folder, on the `results/all-runs` branch. The `work/` folder is
created and ignored by git.

```bash
npm ci
```
```bash
node score-runs.mjs
```

To grade one app against a starting app:

```bash
node quality-grader.mjs <starting app folder> <agent app folder> out.json
```

## Validation

Each planted defect fails its own check and no other
([validation.txt](validation.txt)):

| Variant of the starting app | Lint | Complexity | Duplication | Runtime | Score |
|---|---|---|---|---|---|
| Identical copy | ✔ | ✔ | ✔ | ✔ 1.01× | 100 |
| Unused variable and `debugger` | ✖ 0→2 | ✔ | ✔ | ✔ | 75 |
| A function with complexity 12 | ✔ | ✖ 0→1 | ✔ | ✔ | 75 |
| A test block copied twice | ✔ | ✔ | ✖ 0→13 lines | ✔ | 75 |
| A test that sleeps 1.5 s | ✔ | ✔ | ✔ | ✖ 5.4× | 75 |

**Runtime is noisy near the 1.2× limit.** In repeat runs, the closest
results kept the same outcome: Codex `bugfix-run01` failed every time
(1.22–1.25×), and Codex `injection-run02` passed every time (1.04–1.07×).

## Limitations

- **Duplication is strict.** The starting app has 0 duplicated lines, so any
  repeated block of 5 or more lines fails, including test boilerplate
  repeated across tests. That is what "no more than the baseline" means, but
  it makes duplication the check that fails most often.
- **Runtime rewards fewer tests.** The agent's suite includes the tests it
  added, so a thorough agent runs more tests and is slower. A ratio above
  1.2 usually means the added tests are slow (for example, real timeouts),
  not just that there are more of them.
- **One sample per run.** Each run is graded once, with 10 runtime pairs.
  Results within about 0.05 of the 1.2 limit should be re-checked.
- **Not a style or readability review.** These checks catch measurable
  regressions only.
