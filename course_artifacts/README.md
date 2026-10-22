# Course artifact documentation workspace

Shared workspace for Team 3's course documents. Markdown files in `sources/` are the editable sources. Word and PDF files are exports for submission only. Any teammate can use this with their own IDE and model by asking their agent to read `AGENTS.md` first.

## Workflow

1. Read [AGENTS.md](AGENTS.md), [TODO.md](TODO.md) (index; see also [todo/ddd.md](todo/ddd.md), [todo/srs.md](todo/srs.md), [todo/parked.md](todo/parked.md), [todo/history.md](todo/history.md)), and [TRACEABILITY.md](TRACEABILITY.md).
2. Make the change in the affected `sources/` files. Check the ownership table in `AGENTS.md` for dependent documents.
3. Update `TRACEABILITY.md` and the task files (`TODO.md`, `todo/`) if the change affects them.
4. Review the diff, then commit with a short note: sources touched, sources not touched and why, task IDs, AI assistance.
5. A teammate reviews and closes finished tasks.

## Sources

| ID | File | Imported from | Notes |
| --- | --- | --- | --- |
| SRS | [sources/srs.md](sources/srs.md) | Version 2.0 (October 18, 2026), the team-approved submission, from `references/baselines/srs_2026-10-18_v2.0.docx` | Replaced the revision 1.2 import on Oct. 21. Converted by script, not reviewed clause by clause; Design fields not edited; see Import notes at the end of the file |
| DDD | [sources/ddd.md](sources/ddd.md) | DDD submitted October 18, 2026 (its Document Control says version 1.4, but it is not the Oct. 15 v1.4 PDF), from `references/baselines/ddd_2026-10-18_v1.4-submitted.docx` | Team-approved. Replaced the earlier Markdown "version 1.5" merge on Oct. 21; defines M01 to M13 and I01 to I12; see Import notes at the end of the file |
| MATRIX | [sources/feature_matrix_specification.md](sources/feature_matrix_specification.md) | Feature matrix specification v0.2 | Documentation-only assessment method; incorporated as SRS Requirement 5 and DDD M11 |
| APPROACH A | [sources/approach_a_assessment.md](sources/approach_a_assessment.md) | Created from the matrix specification (not an import); renamed from `track_a_assessment.md` on Oct. 21 | Pointer only. Since matrix spec v0.3 the record is the structured dataset in `../assessment/`, maintained with `../tools/approach_a/` (see its README). No accepted finding yet (DOC-070) |
| PROCEDURE | [sources/benchmark_procedure.md](sources/benchmark_procedure.md) | `team-benchmark-procedure(1).md` | Operational benchmark procedure |
| PAPER | [sources/whitepaper.md](sources/whitepaper.md) | `white_paper_draft.md` | Outline with placeholders |

The SRS 2.0 and DDD files are the team-approved Oct. 18 submission (copies are in `submissions/` and `references/baselines/`); their Markdown conversion is not yet checked against the Word files (DOC-001). The other imports are not approved content. Figures are in `sources/assets/`. The nine DDD diagrams (`ddd-2026-10-18-*.png`) are images only (DOC-003). Images from earlier DDD imports remain in `sources/assets/` and `sources/assets/ddd-v1.0/` but are no longer referenced.

## Folder map

| Path | Purpose |
| --- | --- |
| `sources/` | Editable documents and figures |
| `todo/` | Task lists split by source (DDD, SRS, parked work) and the dated task history; see [TODO.md](TODO.md) for the index |
| `templates/` | Supplied course templates (`originals/`) and readable equivalents (`markdown/`); see [templates/README.md](templates/README.md) |
| `references/` | Supplied slide decks, the DDD and SRS grading rubrics, and the DDD baseline PDFs; see [references/README.md](references/README.md) |
| `submissions/` | Dated Word/PDF exports; see [submissions/README.md](submissions/README.md) |

## Boundaries

- Matrix assessment is documentation-only. Do not add live testing or treat availability as effectiveness.
- Current work: the SRS 2.0 and DDD (Oct. 18 submission) are the baseline. The Approach A reconciliation (DOC-061) is ready for review, and the Antigravity CLI profile needs confirmation, approval, authorship and review before the sponsor demo (DOC-070). Task lists were restarted on Oct. 21; see [TODO.md](TODO.md).
- The Approach A workbench (`../tools/approach_a/`) is the one authorized code exception to rule 8 in AGENTS.md. It reads official documentation only and never runs an assessed tool. Since Oct. 22 (amended SRS Spec 5.4.2) it can also send documentation excerpts to Azure OpenAI to draft briefs, within fixed spending limits; those drafts are not findings until a named author and an independent reviewer accept them.
- Documentation tasks do not authorize code changes, model runs, spending, deployment, or publishing.
- Behavior reported in the DDD is not verified against the repository until a commit is recorded.

## Starter prompt

```text
Read course_artifacts/AGENTS.md, README.md, TODO.md (plus the todo/ file for
the source you are changing), and TRACEABILITY.md.

Task: [describe the change]
Related task IDs: [DOC-xxx or none]
Team decisions for this task: [explicit decisions, or none]

Update the affected sources, TRACEABILITY.md, and the task files (TODO.md,
todo/). Report which
sources you changed and which you left alone and why. Check local links.
```

This workspace was prepared with AI assistance on October 14, 2026 and consolidated the same day. Team review is still required; record AI assistance in later commits as the course requires.
