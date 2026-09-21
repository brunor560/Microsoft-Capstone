# AutoGen Pipeline — Agentic IDE Evaluation Suite

Implementation of the architecture in [`projectbrief.md`](./projectbrief.md).

> **Scope.** All work is confined to `pipeline/autogen/`, `pipeline/tasks/`, and
> (from Phase 6) `.github/workflows/`. The repository-root `app/` directory is a
> shared baseline testbed owned by another team member and is **strictly
> read-only** — it is copied into an ephemeral scratch dir, never mutated.

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

# Phase 0.5 — model connectivity + token capture (~20 tokens)
./.venv/bin/python -m harness.smoke_test --model-profile local-dev

# Phase 1 — build the sandbox, then verify toolchain + credential air-gap
docker build -t agentic-eval-sandbox:latest .devcontainer
./.venv/bin/python -m harness.verify_sandbox
```

Docker-dependent tests skip automatically if the image is absent, so the
offline suite still runs on a machine without Docker.

## Model profiles

Backends are swappable via `config/models.yaml`; see §4b of the brief.

| Profile | Backend | Benchmark-valid | Purpose |
|---|---|---|---|
| `local-dev` | Ollama / `qwen3:8b` | ❌ No | Plumbing validation, zero token cost |
| `azure-prod` | Azure OpenAI | ✅ Yes | Real scored runs |

To point at the Ollama machine, set its LAN address in `.env`:

```
OLLAMA_BASE_URL=http://<lan-ip>:11434/v1
```

Then on the serving machine: `ollama pull qwen3:8b`.

## Status

| Phase | Deliverable | State |
|---|---|---|
| 0 | Scaffolding, deps, profile layer | ✅ Gate passed |
| 0.5 | Model connectivity smoke test | ⏳ Built; awaiting Ollama LAN address |
| 1 | Air-gapped Docker sandbox | ✅ Gate passed (16 tests) |
| 2 | Ephemeral staging + task ingestion | ⬜ Not started |
| 3 | Agent orchestration | ⬜ Not started |
| 4 | Telemetry | ⬜ Not started |
| 5 | Scoring harness | ⬜ Not started |
| 6 | CI/CD bridge (microsite deferred) | ⬜ Not started |

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

### Validated environment

Python 3.14.4 · AutoGen 0.7.5 · LiteLLM 1.102.0 · Docker 29.8.0 (linux/aarch64)

Python 3.14 was a known risk (possible missing C-extension wheels). It
installed clean — no fallback to 3.12 needed.
