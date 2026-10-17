# Microsoft Capstone: Agentic Developer Tool Evaluation

We compare AI coding tools (Antigravity, Copilot, Claude Code, Codex, and an
AutoGen pipeline) by giving each one the same tasks on a small todo app and
grading the results the same way.

## Where things are

| Folder / file | What it holds |
|---|---|
| [`app/`](app/) | The todo app (Express + static UI) the benchmark tasks run against |
| [`baseline/`](baseline/) | Older copy of the todo app used by the root `npm` scripts and the demo |
| [`pipeline/tasks/`](pipeline/tasks/README.md) | Benchmark task definitions shared by every tool |
| [`pipeline/autogen/`](pipeline/autogen/README.md) | AutoGen harness: sandbox, graders, scoring |
| [`benchmark-results/`](benchmark-results/) | Results for every tool, plus the shared graders and procedures |
| [`docs/`](docs/) | Demo site docs: [quick start](docs/QUICKSTART.md), [architecture](docs/ARCHITECTURE.md), [integration](docs/INTEGRATION-GUIDE.md) |
| [`course_artifacts/`](course_artifacts/README.md) | Course deliverables, sources (including the [feature matrix spec](course_artifacts/sources/feature_matrix_specification.md) and [white paper](course_artifacts/sources/whitepaper.md)), templates, transcripts |
| `index.html`, `demo.html` | Project landing page and interactive demo |
| [`benchmarks/`](benchmarks/) | Demo benchmark orchestrator (`npm run benchmark`) |

## Benchmark tasks

| Task | Status |
|---|---|
| [001 Add DELETE endpoint](pipeline/tasks/001-add-delete-endpoint.md) | Run by all four tools |
| [002 Input validation (security trap)](pipeline/tasks/002-input-validation-ipi.md) | Defined, not yet run |
| 003 Edit todo title | Run by all four tools; task file lives on `benchmark-start-v2-edit` |
| [004 Fix update validation](https://github.com/brunor560/Microsoft-Capstone/blob/1e690f91a11dd1b37c796345a511d6791476efbc/pipeline/tasks/004-fix-update-validation.md) | Antigravity and Codex runs published; see results below |

## Results

Inside `benchmark-results/<tool>/`, `run01` (and Codex `run02`) are delete-task
runs, `edit-run01` is the title-edit run, and `bugfix-run01` is the update-validation run.

| Tool | Delete (001) | Edit title (003) | Update bugfix (004) |
|---|---|---|---|
| Antigravity | [run01](benchmark-results/antigravity/run01/) | [edit-run01](benchmark-results/antigravity/edit-run01/) | [bugfix-run01](benchmark-results/antigravity/bugfix-run01/) |
| Claude Code | [run01](benchmark-results/claude/run01/) | [edit-run01](benchmark-results/claude/edit-run01/) | — |
| Codex | [run01, run02](benchmark-results/codex/README.md) | [edit-run01](benchmark-results/codex/edit-run01/README.md) | [bugfix-run01](benchmark-results/codex/bugfix-run01/README.md) |
| Copilot | [run01](benchmark-results/copilot/run01/) | [edit-run01](benchmark-results/copilot/edit-run01/) | — |

Shared graders and run procedures are in
[`benchmark-results/protocol/`](benchmark-results/protocol/): the
[delete procedure](benchmark-results/protocol/team-benchmark-procedure.md) and the
[title-edit procedure](benchmark-results/protocol/edit-title/README.md).

These files were copied from the `results/*` and `benchmark-protocol-v2-edit`
branches. Those branches are still the original records. This branch keeps only what
is needed to analyse the runs: run reports, prompts and final reports, test
outputs and exit codes, timing, token usage, scope reviews, and the agents'
original code. Raw transcripts, setup logs, file manifests, hashes, and
Playwright reports were left out; get them from the `results/*` branch for
that run. For an official run,
use the graders from the agreed evaluator commit named in each procedure, not
this copy.

## Quick start

```bash
npm run setup
npm start        # todo app at http://localhost:3000
npm test         # runs the baseline/ tests
```

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for the demo and
[pipeline/autogen/README.md](pipeline/autogen/README.md) for the AutoGen harness.
