# Benchmark Run Dashboard

A static page for browsing the benchmark results on the `results/all-runs` branch: scores, a tool × task matrix, run replays and code diffs.

## Run it

Needs Node 18 or newer. From the repository root:

```bash
git fetch origin
node dashboard/build-data.mjs
node dashboard/serve.mjs
```

Open http://localhost:4173. To use another port, pass it as an argument (`node dashboard/serve.mjs 8080`) or set `PORT`.

`build-data.mjs` reads the results branch straight from git and writes `dashboard/data.js`; you don't need to check the branch out. Rerun it whenever new runs are pushed. To read a different branch, pass its name: `node dashboard/build-data.mjs origin/results/codex-injection-run01`.

## Files

| File | Purpose |
|---|---|
| `index.html` | The dashboard (HTML, CSS and JavaScript in one file) |
| `build-data.mjs` | Collects runs, test logs, timing, tokens, models and code from git into `data.js` |
| `data.js` | Generated data; safe to delete and rebuild |
| `serve.mjs` | Minimal static server |

## Using it

- **Score by tool**: weighted grade per tool. Use the task chips to grade on specific tasks, and the Sort control to order by score, harness or model.
- **Filters**: tool, task, model, result and text search. They apply to everything below.
- **Results matrix**: click a cell to open a run, or a task label to compare every tool on that task.
- **Run panel**: overview, replay, code diff (against the starting code or another tool's solution), test results, prompt and final report, and the task spec.

## Scoring

Weights come from the SRS (`course_artifacts/sources/srs.md`, Scoring): Functionality 35%, Security 25%, Code quality 20%, Token efficiency 10%, Human collaboration 10%. The saved runs have evidence for Functionality (independent grader checks), Code quality (each run's `quality.json`, from `benchmark-results/protocol/code-quality` on `results/all-runs`) and Security (task 005), so scores are scaled to the measured weight. A tool's grade averages only the tasks it has run; tasks it hasn't run show as "Not ran" and do not count as 0.

Open **How code quality is scored** under the chart for a plain-language explanation of the four code-quality checks, how they are weighted, a worked example (the lowest-scoring run) and how often each check fails.

**Token efficiency** is scored against a token limit per task (001 300,000; 003 500,000; 004 400,000; 005 400,000): 100 up to half the limit, 0 at the limit. Runs whose tool doesn't report tokens get no T score. **Human collaboration** is scored from `interventions.json` once a second team member has rated it in `h-review.json` (100 − 25 per avoidable intervention). Each run's Overview also has an **Operator** box from `operator.json`: whether a person or an AI session ran the benchmark, what it knew and its setup effort. That is not part of the agent's score. See `RUN-RECORD.md` on `results/all-runs`.

Each run is labelled **told** or **not told** about code quality: told when its recorded snapshot commit's task file has the "How your work is graded" section (added 2026-10-24), not told otherwise. Runs without a recorded commit predate that section. Code quality is scored the same either way; the label shows which runs are fair to compare on quality.

Every score shows its reasoning. Open **Why these scores** under the chart for each tool's per-task scores, the reason each task lost points, and the average that makes the grade. Each run's Overview tab has a **Why this score** checklist: every grader suite and trap with ✔ or ✖, the names of failed checks, each deduction, the areas not counted and why, and the arithmetic for the total. The task comparison has a **Why this score** row.

If a run was regraded after an evaluator fix, its folder has `regrade-fixed-grader-*.txt` logs and a `regrade-fixed-grader-exits.txt` naming the grader commit. The dashboard scores those suites from the regrade, marks them "(fixed grader)", and shows the original grader's results in a **Regraded with a fixed grader** box as evidence.

The replay is rebuilt from saved files (prompt, final code, grader logs). It is not a recording, and its timing is sped up.
