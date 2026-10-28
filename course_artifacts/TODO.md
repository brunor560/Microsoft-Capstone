# Documentation tasks

Short index for the `course_artifacts/` workflow. Status: Open, In progress, Ready for review, Closed. An agent may set Ready for review; a teammate closes. Owners are assigned by the team. DOC IDs are for these lists and commit messages only; do not cite them inside the SRS, DDD, or other sources. **Restarted on Oct. 21, 2026** after the SRS 2.0 and DDD (Oct. 18 submission) became the baseline. New tasks start at DOC-060; the earlier lists are archived in [todo/archive/2026-10-21_pre-v2/](todo/archive/2026-10-21_pre-v2/) and every earlier ID is accounted for in [todo/carry-over.md](todo/carry-over.md). The dated record of earlier tasks stays in [todo/history.md](todo/history.md) and is append-only.

## Where tasks live

| File | Contents |
| --- | --- |
| This file | Tasks that touch more than one source (below) |
| [todo/ddd.md](todo/ddd.md) | DDD tasks |
| [todo/srs.md](todo/srs.md) | SRS tasks |
| [todo/parked.md](todo/parked.md) | Parked code and validation work, and the benchmark decisions DOC-020 and DOC-031 (unchanged by the restart) |
| [todo/carry-over.md](todo/carry-over.md) | Where each pre-restart task went: re-listed, superseded, parked or merged |
| [todo/history.md](todo/history.md) | Full dated text of every task; new dated entries are appended |

Each tracker row holds the open ask only. Put dated updates and decisions in `todo/history.md` under the task, and keep the open ask current. File a new task in the file for the source it changes; if it changes more than one source, list it here.

## Cross-document tasks

| ID | Open ask | Owner | Status | History |
| --- | --- | --- | --- | --- |
| DOC-060 | Check the Markdown conversions of SRS 2.0 and the Oct. 18 DDD against the Word files in `references/baselines/` (tables, short cells, IDs, formulas, figures, the JSON schema blocks). The conversion was scripted; the Word table headers merged across columns, the DDD version-history table has shifted cells, and nothing was compared clause by clause. Replaces DOC-001. | Unassigned | Open | [DOC-060](todo/history.md#doc-060) |
| DOC-061 | Review the Approach A reconciliation (branch `feature-matrix-revisions`): matrix specification v0.3, the pointer-only `sources/approach_a_assessment.md`, the whitepaper Approach A text, the Approach A rows of `TRACEABILITY.md`, and the `assessment/` dataset with the `tools/approach_a/` workbench. Still open: the team's profile set and account tier for the approved manifest, and the whitepaper's weighted table (see its 3.3 open item). Replaces DOC-040 and DOC-041. | Unassigned | Ready for review | [DOC-061](todo/history.md#doc-061) |
| DOC-070 | Antigravity CLI profile for the sponsor demo: a team member confirms the boundary and tier, Ross approves the manifest, a named author takes responsibility for each agent-drafted cell, and a different member reviews every cell against its source (SRS Spec 5.3). Research F03 (requirements traceability), which is still pending. Settle the F18 timeout-default conflict between the headless page and the CLI changelog. Oct. 22: briefs can now be drafted with Azure OpenAI (amended Spec 5.4.2); settle DDD ADR-14 ("no model calls in A") and tune the demo limits in `tools/approach_a/drafting.json`. | Unassigned | Open | [DOC-070](todo/history.md#doc-070) |
| DOC-062 | Check SRS 2.0 against the Oct. 18 DDD after import: Specs 6.1, 6.2 and 6.4 name M01/M03, M05/M06 and M07/M10 as replaced modules but the DDD lists none; interface links (I01 to I12) were not compared; the DDD's `V02` reference and the "version 1.4" label (same number as the Oct. 15 PDF) need a decision. The DDD is authoritative for module and interface links. | Unassigned | Open | [DOC-062](todo/history.md#doc-062) |
| DOC-063 | Settle the items both documents mark as open or proposed that need a team decision: spend cap (SRS Spec 2.5, DDD C-3), SRS OI-1 (task manifest start commit and passing preflight) and OI-2 (cohort timing contract), the schema 3 file `benchmark_run.schema.json` (SRS says committed; reported absent), the cohort "out of 90" rule, and raw-log retention. Replaces DOC-010, DOC-012, DOC-013 and DOC-059. | Unassigned | Open | [DOC-063](todo/history.md#doc-063) |
