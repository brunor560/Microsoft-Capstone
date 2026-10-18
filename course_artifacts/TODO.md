# Documentation tasks

Short index for the `course_artifacts/` workflow. Status: Open, In progress, Ready for review, Closed. An agent may set Ready for review; a teammate closes. Owners are assigned by the team. IDs keep their original DOC numbers, so gaps in numbering are intentional (merged tasks are noted, and code work is parked in `todo/parked.md`). DOC IDs are for these lists and commit messages only; do not cite them inside the SRS, DDD, or other sources.

## Where tasks live

| File | Contents |
| --- | --- |
| This file | Tasks that touch more than one source (below) |
| [todo/ddd.md](todo/ddd.md) | DDD tasks: DOC-003, 004, 008, 015, 043-047, 049-052 |
| [todo/srs.md](todo/srs.md) | SRS tasks: DOC-042 |
| [todo/parked.md](todo/parked.md) | Parked code and validation work, and the benchmark decisions DOC-020 and DOC-031 |
| [todo/history.md](todo/history.md) | Full dated text of every task, moved verbatim from the earlier single file |

Each tracker row holds the open ask only. Put new dated updates and decisions in `todo/history.md` under the task, and keep the open ask current. File a new task in the file for the source it changes; if it changes more than one source, list it here.

## Cross-document tasks

| ID | Open ask | Owner | Status | History |
| --- | --- | --- | --- | --- |
| DOC-001 | Check the SRS and DDD Markdown conversions against the originals (SRS tables, short cells, figures and schema; the whole DDD against `references/baselines/ddd_2026-10-15_v1.4.pdf`). Blocks most other tasks. | Unassigned | In progress | [DOC-001](todo/history.md#doc-001) |
| DOC-007 | Clause-level SRS to module to pattern to test mapping, patterns, NFRs, and a review of every row in the DDD requirements table and `TRACEABILITY.md`. | Unassigned | In progress | [DOC-007](todo/history.md#doc-007) |
| DOC-010 | Amend SRS Appendix A (on hold with the other SRS changes), version the run-record schema, and commit the JSON Schema file (DOC-011). | Unassigned | Open | [DOC-010](todo/history.md#doc-010) |
| DOC-012 | Update the SRS metric contract and Appendix A wording (on hold), and decide the "total out of 90" rule when a harness failure is not a tool limitation. | Unassigned | Open | [DOC-012](todo/history.md#doc-012) |
| DOC-013 | Decide raw-log retention and cleanup (formerly DOC-014). The 120-second active-time decision is recorded in the history. | Unassigned | Ready for review | [DOC-013](todo/history.md#doc-013) |
| DOC-040 | Team review of the feature matrix in the SRS and DDD. Still open: move the active HLA from the SRS to the DDD; set the SRS revision label and date for change 1.2; update the DDD figures if Approach A should appear. | Unassigned | Ready for review | [DOC-040](todo/history.md#doc-040) |
| DOC-041 | Define the Approach A profile set (MATRIX:C01-C03 are placeholders), then reconcile the matrix spec, whitepaper, DDD M11 cell count and `track_a_assessment.md`. | Unassigned | Open | [DOC-041](todo/history.md#doc-041) |
| DOC-048 | When the SRS change is made: map the SRS Track B to Approaches B and C (or C where it means the harness), rename `sources/track_a_assessment.md`, and update `TRACEABILITY.md`. The DDD, matrix specification, whitepaper, README and AGENTS already say Approach A. | Unassigned | In progress | [DOC-048](todo/history.md#doc-048) |
