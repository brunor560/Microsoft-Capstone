# Parked code, validation and benchmark work

Part of the split task list; see [../TODO.md](../TODO.md) for status values and rules.

## Benchmark decisions

| ID | Task | Owner | Status |
| --- | --- | --- | --- |
| DOC-020 | Select the canonical baseline and task seed (`app/` fails, `baseline/` passes, Task 001 already contains the requested endpoint). | Unassigned | Open |
| DOC-031 | Clarify the benchmark-valid input example (`azure-prod` versus `azure-dev`). | Unassigned | Open |

## Parked code and validation work (move to GitHub Issues later)

These come from claims reported in the DDD. They were not checked against the current repository, and the DDD may already be out of date for them. Each keeps its original ID for reference.

| ID | Work |
| --- | --- |
| DOC-011 | Supply `benchmark_run.schema.json` (SRS says committed; reported absent). Depends on DOC-010. |
| DOC-016 | Credential-free manifest staging (`.env` not excluded; manifest-only copy, reject external links). |
| DOC-017 | Sandbox resource limits, 60-second command watchdog, cleanup. |
| DOC-018 | Host-side budgets; real approval behavior and expiry. |
| DOC-019 | Offline testbed dependencies (Express missing in image; `node_modules` skipped). |
| DOC-021 | Write benchmark tasks T3–T8. |
| DOC-022 | Independent grading (frozen candidate, read-only mounts) and fail-closed scanner. |
| DOC-023 | Align scoring formulas with the approved metric contract. |
| DOC-024 | Atomic terminal telemetry records (missing usage stored as zero, timing stops before grading). |
| DOC-025 | Patch export and CI trusted-base grading (main/master mismatch, PR-code grading). |
| DOC-026 | Static release build and publication path. |
| DOC-027 | Measure performance and lifecycle targets (setup/teardown, UI, telemetry, CI, site). |
| DOC-028 | Measure run-record size (5 MiB per run and 480 MiB for 96 runs are estimates). |
| DOC-029 | Verify reported code observations, default-model labels and pilot timings against the repository. |

Do not mark anything resolved from document text alone.
