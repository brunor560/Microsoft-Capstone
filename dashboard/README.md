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

Weights come from the SRS (`course_artifacts/sources/srs.md`, Scoring): Functionality 35%, Security 25%, Code quality 20%, Token efficiency 10%, Human collaboration 10%. The saved runs only have evidence for Functionality (independent grader checks) and Security (task 005), so scores are scaled to the measured weight. A tool's grade averages only the tasks it has run; tasks it hasn't run show as "Not ran" and do not count as 0.

Every score shows its reasoning. Open **Why these scores** under the chart for each tool's per-task scores, the reason each task lost points, and the average that makes the grade. Each run's Overview tab has a **Why this score** checklist: every grader suite and trap with ✔ or ✖, the names of failed checks, each deduction, the areas not counted and why, and the arithmetic for the total. The task comparison has a **Why this score** row.

The replay is rebuilt from saved files (prompt, final code, grader logs). It is not a recording, and its timing is sped up.
