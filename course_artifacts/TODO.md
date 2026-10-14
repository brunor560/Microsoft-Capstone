# Documentation tasks

Short list to start the `course_artifacts/` workflow. Status: Open, In progress, Ready for review, Closed. An agent may set Ready for review; a teammate closes. Owners are assigned by the team. IDs keep their original DOC numbers, so gaps in numbering are intentional (merged tasks are noted, and code work is parked below). DOC IDs are for this list and commit messages only; do not cite them inside the SRS, DDD, or other sources.

## Documentation and decision tasks

| ID | Task | Owner | Status |
| --- | --- | --- | --- |
| DOC-001 | Review the Markdown conversions of the SRS and DDD against the originals (text, tables, IDs, formulas, figures); fix defects. Blocks most other tasks. Partly done (Oct. 14): SRS sentences over 40 characters were compared with the original Word file; 369 of 372 match, and the other 3 differ only by a table-of-contents line and two sentences edited for Track A. Still to check: SRS tables, short cells, figures and the schema; the whole DDD against its PDF. The original also has 15 reviewer comments that were not imported. | Unassigned | In progress |
| DOC-040 | **Feature matrix in the SRS and DDD** (MATRIX:F01–F18, documentation-only). Drafted: SRS F6, Requirement 5 (Specs 5.1–5.5, Must), TC-5.x, H-8, scope, glossary and reference [13]; DDD scope, goal 7, M11 rows, Track A data and ADR-13; `sources/track_a_assessment.md` stub; traceability rows. Team review needed. Still open: move the active HLA from the SRS to the DDD (formerly DOC-009; the SRS template marks the HLA "remove after week 5"); set the SRS revision label and date for change 1.2; update the DDD figures if Track A should appear. | Unassigned | Ready for review |
| DOC-041 | **Decide the Track A profile set.** The matrix spec v0.2 defines two Copilot profiles (36 cells); the whitepaper names Copilot in VS Code, Claude Code CLI and Google Anti-Gravity. The record holds three placeholder profiles (MATRIX:C01–C03) and the SRS and DDD avoid fixing a count. The team defines each profile; nothing is filled in yet. Then reconcile the matrix spec, whitepaper, DDD M11 cell count and `track_a_assessment.md`. | Unassigned | Open |
| DOC-042 | SRS defect, not an import defect: the original Word file has the same gaps as `sources/srs.md`. It cites NFR-L1, NFR-R1, NFR-R2 and TC-NFR-* tests (Test Plan H-5 to H-7) but has no NFR section; names a traceability matrix but has none; refers to an Appendix B that does not exist; lists TC-4.5-3 in H-4 although Spec 4.5 defines only TC-4.5-1 and TC-4.5-2; and leaves the Spec 2.5 limits as placeholders ([token limit], [USD amount], [rate]). Needs a team decision: write the missing NFR section, traceability matrix and Appendix B, or remove the references. | Unassigned | Open |
| DOC-003 | Recover or recreate editable diagram sources (Mermaid); identify all figures and fix the Figure 4 reference in System Coupling. Rubric: views must not contradict each other or the text; the DDD already says its logical view differs from the SRS view, so reconcile or explain it. Team decision (Oct. 14): diagrams and figures come last. | Unassigned | Open |
| DOC-004 | Define the D05/D06/D09, V02–V05 and E15 references used in the DDD but never defined. | Unassigned | Open |
| DOC-007 | Review `TRACEABILITY.md` for real: clause-level SRS to module to pattern to test, plus NFRs. Replace wildcard test references (formerly DOC-030). Rubric: the DDD itself needs a requirement-to-design table (SRS requirement to module, interface and test), so `TRACEABILITY.md` alone is not enough; keep task IDs out of that table. Done so far: a Requirements Traceability table in the DDD (exact test IDs; wildcard references in the module table replaced) and the module column of `TRACEABILITY.md` aligned with it. Still open: clause-level mapping, patterns, NFRs, and review of every row. | Unassigned | In progress |
| DOC-008 | Check the DDD against Week 6 requirements: build-versus-buy, pattern rationale, quality attributes. Fill empty appendices A–C and the glossary (formerly DOC-005); confirm version and submission metadata (formerly DOC-006). Also check against the grading rubric in `references/architecture_document_agentic_review_rubric.md` (see DOC-043 to DOC-046 for its specific gaps). Done so far: DDD Appendices A to C filled from the DDD's own terms and references. Still open: build-versus-buy analysis, pattern rationale, quality-attribute coverage, version and submission metadata. | Unassigned | In progress |
| DOC-010 | Decide and version the proposed run-record schema (v3); the DDD calls it an SRS amendment. | Unassigned | Open |
| DOC-012 | Decide metric formulas for missing usage data and aggregation (token dimension when counts are unavailable). | Unassigned | Open |
| DOC-013 | Decide whether the 120-second active-time target stands, given a reported pilot of about 6.5 minutes. Also decide raw-log retention and cleanup (formerly DOC-014). | Unassigned | Open |
| DOC-015 | Record dispositions and rationale for the proposed ADRs and link them to requirements (formerly DOC-032). Rubric: also analyze the trade-offs behind the key decisions (for example performance versus scalability); the ADR table lists alternatives but no analysis. | Unassigned | Open |
| DOC-043 | Add a behavioral/process view to the DDD: sequence or activity diagrams for the main run workflow (Plan, Execute, Grade, Score, Publish). Decide whether to add a development/scenarios view. The rubric requires a behavioral view; none exists yet. Deferred by team decision (Oct. 14): diagrams and figures come last. | Unassigned | Open |
| DOC-044 | Expand interface contracts I01–I09: protocol, data format and error handling for each, not just a one-line contract. Review the System Inputs/Outputs sections at the same time. | Unassigned | Open |
| DOC-045 | Add DDD sections for cross-cutting concerns (observability, fault tolerance, configuration management) and operational numbers (load, capacity, latency budgets, scaling), plus a risks, assumptions and mitigations section with a validation approach. Targets already marked unmeasured stay unmeasured. Drafted: DDD Cross-Cutting Concerns (with Capacity and scaling) and Risks, Assumptions and Mitigations, built only from existing DDD content. No numbers were invented, and there is still no latency budget beyond the existing targets table. Team review needed. | Unassigned | Ready for review |
| DOC-046 | Compliance items: state how the DDD follows ISO/IEC/IEEE 42010 and the 4+1 views (both appear only in the reference list); mark AI-assisted sections, diagrams and decisions individually, not one generic note; confirm the timesheets match the work done. No timesheet template has been supplied (see `templates/README.md`). | Unassigned | Open |
| DOC-020 | Select the canonical baseline and task seed (`app/` fails, `baseline/` passes, Task 001 already contains the requested endpoint). | Unassigned | Open |
| DOC-031 | Clarify the benchmark-valid input example (`azure-prod` versus `azure-dev`). | Unassigned | Open |

DOC-043 to DOC-046 come from the grading rubric ([references](references/architecture_document_agentic_review_rubric.md)) compared with the DDD text. They are a quick read, not a scored review.

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
