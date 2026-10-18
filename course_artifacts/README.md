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
| SRS | [sources/srs.md](sources/srs.md) | `SRS_Doc_Group#3.docx`, revision 1.1 | Phone/email contact fields omitted in the import |
| DDD | [sources/ddd.md](sources/ddd.md) | DDD version 1.5 (October 16, 2026), built from the version 1.4 PDF supplied October 15, 2026 plus additions from the version 1.0 import (see Merge notes in the file) | Version 1.4 is the baseline for text and figures; proposals and reported status kept as written; the DDD, matrix specification, whitepaper, README and AGENTS say Approach A; the SRS, `TRACEABILITY.md` and the assessment record file name still say Track A until the SRS change is made (DOC-048) |
| MATRIX | [sources/feature_matrix_specification.md](sources/feature_matrix_specification.md) | Feature matrix specification v0.2 | Documentation-only assessment method; incorporated as SRS Requirement 5 and DDD M11 |
| APPROACH A | [sources/track_a_assessment.md](sources/track_a_assessment.md) | Created from the matrix specification (not an import) | Stub: profiles undefined, no cell assessed |
| PROCEDURE | [sources/benchmark_procedure.md](sources/benchmark_procedure.md) | `team-benchmark-procedure(1).md` | Operational benchmark procedure |
| PAPER | [sources/whitepaper.md](sources/whitepaper.md) | `white_paper_draft.md` | Outline with placeholders |

The imports are not approved content until DOC-001 is done. Figures are in `sources/assets/`. The DDD diagrams (nine, from the v1.4 PDF) are images only (DOC-003); the v1.0 images are in `sources/assets/ddd-v1.0/`.

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
- Current work: team review of the feature matrix incorporated into the SRS and DDD (DOC-040), and the Approach A profile decision (DOC-041).
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
