# Documentation tasks

Short list to start the `course_artifacts/` workflow. Status: Open, In progress, Ready for review, Closed. An agent may set Ready for review; a teammate closes. Owners are assigned by the team. IDs keep their original DOC numbers, so gaps in numbering are intentional (merged tasks are noted, and code work is parked below). DOC IDs are for this list and commit messages only; do not cite them inside the SRS, DDD, or other sources.

## Documentation and decision tasks

| ID | Task | Owner | Status |
| --- | --- | --- | --- |
| DOC-001 | Review the Markdown conversions of the SRS and DDD against the originals (text, tables, IDs, formulas, figures); fix defects. Blocks most other tasks. | Unassigned | Open |
| DOC-040 | **Feature matrix in the SRS and DDD** (MATRIX:F01–F18, documentation-only). Drafted: SRS F6, Requirement 5 (Specs 5.1–5.5, Must), TC-5.x, H-8, scope, glossary and reference [13]; DDD scope, goal 7, M11 rows, Track A data and ADR-13; `sources/track_a_assessment.md` stub; traceability rows. Team review needed. Still open: move the active HLA from the SRS to the DDD (formerly DOC-009; the SRS template marks the HLA "remove after week 5"); set the SRS revision label and date for change 1.2; update the DDD figures if Track A should appear. | Unassigned | Ready for review |
| DOC-041 | **Decide the Track A profile set.** The matrix spec v0.2 defines two Copilot profiles (36 cells); the whitepaper names Copilot in VS Code, Claude Code CLI and Google Anti-Gravity. The record holds three placeholder profiles (MATRIX:C01–C03) and the SRS and DDD avoid fixing a count. The team defines each profile; nothing is filled in yet. Then reconcile the matrix spec, whitepaper, DDD M11 cell count and `track_a_assessment.md`. | Unassigned | Open |
| DOC-042 | SRS import gap: the SRS cites NFR-* IDs, TC-NFR-* tests and an RTM, but no NFR section or RTM table was found in `sources/srs.md`. Compare with the original Word file (part of DOC-001 if it is an import defect). | Unassigned | Open |
| DOC-003 | Recover or recreate editable diagram sources (Mermaid); identify all figures and fix the Figure 4 reference in System Coupling. | Unassigned | Open |
| DOC-004 | Define the D05/D06/D09, V02–V05 and E15 references used in the DDD but never defined. | Unassigned | Open |
| DOC-007 | Review `TRACEABILITY.md` for real: clause-level SRS to module to pattern to test, plus NFRs. Replace wildcard test references (formerly DOC-030). | Unassigned | Open |
| DOC-008 | Check the DDD against Week 6 requirements: build-versus-buy, pattern rationale, quality attributes. Fill empty appendices A–C and the glossary (formerly DOC-005); confirm version and submission metadata (formerly DOC-006). | Unassigned | Open |
| DOC-010 | Decide and version the proposed run-record schema (v3); the DDD calls it an SRS amendment. | Unassigned | Open |
| DOC-012 | Decide metric formulas for missing usage data and aggregation (token dimension when counts are unavailable). | Unassigned | Open |
| DOC-013 | Decide whether the 120-second active-time target stands, given a reported pilot of about 6.5 minutes. Also decide raw-log retention and cleanup (formerly DOC-014). | Unassigned | Open |
| DOC-015 | Record dispositions and rationale for the proposed ADRs and link them to requirements (formerly DOC-032). | Unassigned | Open |
| DOC-020 | Select the canonical baseline and task seed (`app/` fails, `baseline/` passes, Task 001 already contains the requested endpoint). | Unassigned | Open |
| DOC-031 | Clarify the benchmark-valid input example (`azure-prod` versus `azure-dev`). | Unassigned | Open |

No timesheet template has been supplied (see `templates/README.md`); add the file there if the team wants it tracked.

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
