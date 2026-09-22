# AutoGen Pipeline — Agentic IDE Evaluation Suite

Implementation of the architecture in [`projectbrief.md`](./projectbrief.md).

> **Scope.** All work is confined to `pipeline/autogen/`, `pipeline/tasks/`, and
> (from Phase 6) `.github/workflows/`. The repository-root `app/` directory is a
> shared baseline testbed owned by another team member and is **strictly
> read-only** — it is copied into an ephemeral scratch dir, never mutated.

## Run a benchmark

```bash
cd pipeline/autogen
./.venv/bin/python run_benchmark.py --task 001-add-delete-endpoint
```

Useful flags: `--model-profile`, `--repo`, `--interactive` (real
human-in-the-loop prompts), `--network` (allow `npm`/`pip install`),
`--export-pr` (dry run unless `--push` is also given).

## Setup

```bash
cd pipeline/autogen
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env     # then fill in
```

`.env` and `.venv/` are gitignored. The host is the only place real
credentials exist; they are never passed into the sandbox container.

## Verification gates

Each phase has an executable gate. A phase is not "done" because files exist.

```bash
# Phase 0 — dependency stack + AutoGen v0.4 API surface
./.venv/bin/python -m harness.verify_env

# Phase 0 — offline unit tests (no LLM, no Docker, no network)
./.venv/bin/python -m pytest

# Phase 0.5 — model connectivity + token capture (~14 tokens, fractions of a cent)
./.venv/bin/python -m harness.smoke_test --model-profile azure-dev

# Phase 1 — build the sandbox, then verify toolchain + credential air-gap
docker build -t agentic-eval-sandbox:latest .devcontainer
./.venv/bin/python -m harness.verify_sandbox

# Phase 2 — task matrix, ephemeral staging, and app/ integrity
./.venv/bin/python -m harness.verify_staging

# Phase 3 — live agent loop, ceilings, HITL, network isolation (~cents)
./.venv/bin/python -m harness.verify_orchestration --model-profile azure-dev

# Phase 4 — live telemetry capture + JSON artifact (~cents)
./.venv/bin/python -m harness.verify_telemetry --model-profile azure-dev

# Phase 5 — graders + weighted scoring (offline, free)
./.venv/bin/python -m harness.verify_scoring
```

Live tests can be skipped to avoid API spend:

```bash
SKIP_LIVE_TESTS=1 ./.venv/bin/python -m pytest
```

Docker-dependent tests skip automatically if the image is absent, so the
offline suite still runs on a machine without Docker.

## Model profiles

Backends are swappable via `config/models.yaml`; see §4b of the brief.

| Profile | Backend | Benchmark-valid | Purpose |
|---|---|---|---|
| `local-dev` | Ollama / `qwen3:8b` | ❌ No | Plumbing validation, zero token cost |
| `azure-dev` | Azure / `gpt-4.1-mini` | ❌ No | Plumbing validation, ~$0.01/run |
| `azure-prod` | Azure OpenAI | ✅ Yes | Real scored runs |

`azure-dev` uses the **same `azure-openai` builder** as `azure-prod`, so
exercising it also exercises the production code path — unlike `local-dev`,
which goes through the OpenAI-compatible client.

### Azure region constraint (USF tenant)

A tenant policy restricts deployment to `mexicocentral`, `westus`,
`canadacentral`, `denmarkeast`, `belgiumcentral`. Of those, **only `westus`
and `canadacentral` support Azure OpenAI** — `eastus2`, the default in most
tutorials, is blocked by policy and will fail deployment.

The `azure-dev` resource is provisioned in `westus` with `gpt-4.1-mini`
(GlobalStandard, capacity 10 ≈ 10K TPM). At a 15k-token ceiling a single run
may span 1–2 minutes of rate-limited throughput.

To point at the Ollama machine, set its LAN address in `.env`:

```
OLLAMA_BASE_URL=http://<lan-ip>:11434/v1
```

Then on the serving machine: `ollama pull qwen3:8b`.

## Status

| Phase | Deliverable | State |
|---|---|---|
| 0 | Scaffolding, deps, profile layer | ✅ Gate passed |
| 0.5 | Model connectivity smoke test | ✅ Gate passed (live `azure-dev`) |
| 1 | Air-gapped Docker sandbox | ✅ Gate passed |
| 2 | Ephemeral staging + task ingestion | ✅ Gate passed |
| 3 | Agent orchestration | ✅ Gate passed (live) |
| 4 | Telemetry | ✅ Gate passed (live) |
| 5 | Scoring harness | ✅ Gate passed |
| 6 | CI/CD bridge (microsite deferred) | ✅ Gate passed |

## Version consistency across the team

The graders only ever run **inside the container**, so a teammate's local
`complexipy` is irrelevant — but that only guarantees consistency if
everyone's image was built from the current Dockerfile. A stale cached image
would grade with a different analyser and say nothing.

Three layers guard this:

1. **Pinned** in `.devcontainer/Dockerfile` (`complexipy==3.0.0`, etc.).
2. **Asserted** by `harness.verify_sandbox`, which reads the *running*
   image's versions and fails if any differ from `EXPECTED_VERSIONS`.
3. **Cross-checked** by `test_pinned_versions_match_dockerfile`, so the
   Dockerfile and the gate cannot silently disagree.

If a teammate sees `FAIL complexipy 3.1.0 != pinned 3.0.0`, rebuild:

```bash
docker build --no-cache -t agentic-eval-sandbox:latest .devcontainer
```

**Better: pull the shared image.** `publish-sandbox-image.yml` pushes a
multi-arch (`amd64` + `arm64`) build to `ghcr.io` on every change to
`.devcontainer/`, so the team can share one digest instead of each
rebuilding:

```bash
docker pull ghcr.io/brunor560/microsoft-capstone/agentic-eval-sandbox:latest
docker tag ghcr.io/brunor560/microsoft-capstone/agentic-eval-sandbox:latest \
  agentic-eval-sandbox:latest
```

That removes version drift as a class of problem; the assertions above remain
as a safety net for locally-built images.

## CI/CD notes (Phase 6)

Three workflows in `/.github/workflows/`, all **zero-cost** (no model calls):

| Workflow | Trigger | Purpose |
|---|---|---|
| `autogen-pipeline-ci.yml` | push/PR on `pipeline/**` | Offline suite + all four offline gates |
| `agent-pr-referee.yml` | PR from an `agent/*` branch | Independently re-grades the PR |
| `publish-sandbox-image.yml` | change to `.devcontainer/` | Publishes multi-arch image to `ghcr.io` |

CI runs with `SKIP_LIVE_TESTS=1`, so it never spends Azure credits. It still
builds the sandbox and runs the Docker-backed grader tests, which is where
tool-output parsing regressions actually surface.

The CI job also plants **poisoned credential canaries** in the runner
environment and asserts they are absent inside the container — so if Docker
ever began forwarding the host environment, the build fails rather than
silently reopening the exfiltration vector.

### The referee refuses rather than misleads

`harness/referee.py` re-grades PRs independently, because a self-reported
score is not evidence. Two deliberate design choices:

- **It grades F, S and Q only, renormalised over their 0.80 weight.** `T`
  and `H` are properties of the *run* (tokens spent, operator
  interventions), not of the resulting code, so CI cannot observe them.
  The verdict states this scope explicitly.
- **It refuses to grade an unsupported test framework.** Pointed at the
  Node `app/`, pytest collects zero tests and reports `F = 0` with
  `reliable: true` — indistinguishable from *"the agent's code fails every
  test"*. The referee now detects the framework and exits 1 with a reason
  instead. A genuine test failure still scores a real 0.

### PR export is dry-run by default

`export_pr(..., dry_run=True)` is the default: opening PRs mutates a shared
repository, so it must be opted into explicitly. Agent branches are
namespaced `agent/<task_id>/<run_id>`, and every commit message and PR body
states the work is machine-generated and unreviewed.

**Push happens on the host, never in the sandbox** — pushing needs a real
token, and the sandbox is blind to host credentials by design.

## Scoring notes (Phase 5)

`0.35F + 0.25S + 0.20Q + 0.10T + 0.10H`, assembled in `harness/scoring.py`.
Graders live in `graders/` behind a name registry, so adding `node --test`
or `go test` needs no change to the harness.

**"Stable" in the Q definition means "versus the Phase 2 baseline commit."**
The brief did not say what the reference point was; comparing against the
pre-agent tree makes it mean *the agent did not degrade what it was given*.
Criteria that cannot be measured (e.g. `complexipy` on a JS target) are
**excluded from the denominator** rather than awarded or deducted.

**A crashed grader is not a zero.** `Scorecard.reliable` is `False` when any
grader errored, so "the tests never ran" is distinguishable from "every test
failed". Consumers should treat an unreliable card as provisional.

**Graders never write into the directory they grade.** All artifacts
(`pytest` JSON report, `complexipy.json`, `__pycache__`, `.pytest_cache/`)
go to `/tmp` *inside* the container. `/workspace` is a bind mount of the
host, so writing there leaves files behind — which contaminated `app/`
during Phase 6 development. `tests/test_grader_cleanliness.py` pins this
with a byte-level digest of the graded tree before and after.

One subtlety worth knowing if you extend the graders: each `runner.run()`
starts a **fresh container**, so `/tmp` does not persist between calls. A
report must be written and read back in the *same* command.

**Three silent-failure traps, all caught by gates rather than review:**

- `complexipy` is a **linter** — it exits 1 above its complexity threshold
  (15). An `&& cat report.json` chain therefore broke *precisely when code
  was most complex*, skipping the criterion instead of failing it, which
  would have **rewarded** deeply nested code.
- `scc` needs the path **before** its flags. `scc --format json PATH`
  returns `[]` silently, which would make duplication look unchanged
  forever.
- Graders writing into `/workspace` leave artifacts on the host. Caught
  only by `git status` — `git diff` stays clean because nothing *tracked*
  changes.

## Telemetry notes (Phase 4)

Artifacts land in `logs/<task_id>_<run_id>.json`. The schema is a **stable
contract** documented in [`docs/telemetry-schema.md`](./docs/telemetry-schema.md)
— the microsite dashboard will consume it.

**Consumers must filter on `model.benchmark_valid`.** `logs/` accumulates
cheap plumbing runs (`azure-dev`, `local-dev`) next to real benchmark runs;
charting them together would present a dev-model run as a framework
comparison.

**LiteLLM was evaluated and not adopted.** AutoGen v0.4 already exposes token
usage directly, so a LiteLLM proxy would add a network hop to re-derive
numbers already in hand. Per-call *latency*, however, genuinely is not
available from AutoGen — so `harness/instrumented_client.py` wraps the model
client and times each `create()` call. The Phase 4 gate asserts latency is
non-zero, because serializing `0.0` would be indistinguishable from a real
measurement.

## Orchestration notes (Phase 3)

**Network isolation.** `DockerCommandLineCodeExecutor` does not expose
Docker's `network_mode`, so its containers get full outbound internet by
default. `harness/executor.py` adds `IsolatedDockerCodeExecutor`, which
defaults to `network_mode="none"` — isolation is **opt-out, not opt-in**.

Trade-off: with networking off, `npm install` / `pip install` fail. Tasks
needing dependency resolution must pass `network_mode=None`.

**The TERMINATE sentinel is scoped to the coder.** A bare
`TextMentionTermination("TERMINATE")` also inspects the incoming user task,
so any task whose text contains that word — including the natural
instruction *"reply TERMINATE when done"* — ends the run before a single
model call. It is therefore AND-ed with `SourceMatchTermination(["coder"])`.
Regression-tested offline in `test_orchestrator.py`.

**Interventions vs. consultations.** `H` decrements 10 points per
*substantive* operator reply. Bare approvals (`""`, `y`, `yes`, `ok`,
`approve`, `continue`, `c`) are assent, not correction, and cost nothing —
otherwise simply running the pipeline interactively would tank the score.

## Sandbox notes

The image is pinned (`trufflehog 3.97.5`, `scc 4.1.0`, `pytest 8.3.4`,
`complexipy 3.0.0`) so grading stays reproducible, and builds natively on
`arm64` and `amd64`.

Two behaviours found in Phase 1 that Phase 5's graders must respect:

- **TruffleHog reports only *verified* secrets by default.** An unverifiable
  leaked key returns zero findings, which would silently award `S = 100` to a
  leaking agent. Graders must pass `--results=verified,unknown,unverified`.
- **`complexipy` has no `--version` flag** (exits 2 with usage); probe
  `importlib.metadata` instead.

The container currently **has outbound internet access**. No credentials exist
inside it, so there is nothing to exfiltrate, but Phase 3 should consider
`network=none` for scored runs to close the vector entirely.

## Known gaps

- **No Node grader.** `app/` is Node/Express but the sandbox is
  `python:3.11-slim`. The referee correctly *refuses* to grade it rather
  than reporting a misleading `F = 0`, so end-to-end runs against `app/`
  produce `reliable: false`. Adding a `node --test` grader means installing
  Node in the image and registering a grader in `graders/`.
- **Microsite deploy deferred** — owned by another team member. The
  contract is `docs/telemetry-schema.md`.
- **Workflows untested on GitHub.** They are valid YAML and the commands
  they run all pass locally, but no PR has triggered them yet. The
  `ghcr.io` publish may need package permissions from the repo owner
  (`brunor560`).
- **`app/test.js` line 1** is a stray Markdown fence that makes the file
  invalid JavaScript, so `npm test` fails. Left alone — `app/` is not ours;
  task 001 makes fixing it part of the benchmark.

### Validated environment

Python 3.14.4 · AutoGen 0.7.5 · LiteLLM 1.102.0 · Docker 29.8.0 (linux/aarch64)

Python 3.14 was a known risk (possible missing C-extension wheels). It
installed clean — no fallback to 3.12 needed.
