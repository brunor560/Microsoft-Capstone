# Approach A assessment record

The working record for the documentation-based feature assessment (Approach A). It is defined by the [feature matrix specification](feature_matrix_specification.md) (v0.3) and required by SRS Requirement 5 (Specs 5.1 to 5.5). Design: DDD module M11.

**Where the record is.** Since October 21, 2026, the authoritative record is the structured dataset in [`assessment/`](../../assessment/) at the repository root. It is maintained with the workbench in [`tools/approach_a/`](../../tools/approach_a/README.md). This file no longer holds profiles, cells or evidence, so the record exists in one place only. The earlier stub, with placeholder profiles MATRIX:C01 to C03 that were never approved, is in git history.

| Record element (SRS) | Location | Readable view (generated) |
| --- | --- | --- |
| Approved, versioned profile manifest (Spec 5.1) | `assessment/manifest.json` | `assessment/out/manifest.md` |
| 18 × P cells with status, scope, setup and gap reasons (Spec 5.2) | `assessment/cells.json` | `assessment/out/matrix.md`, `assessment/out/cells/<profile>/<feature>.md` |
| Official-source index, MATRIX:E01 onwards (Spec 5.2) | `assessment/sources.json` | `assessment/out/sources.md` |
| Author, independent review and disagreement records (Spec 5.3) | `assessment/cells.json` (author), `assessment/reviews.json` | `assessment/out/reviews.md` |
| Assessment work log (Spec 5.4, TC-5.4-1) | `assessment/worklog.jsonl` | `assessment/out/worklog.md` |
| Validation report (structural checks for TC-5.1-1 to TC-5.4-1) | `assessment/validation_report.json` | `assessment/out/validation_report.md` |

Generated views are not published (Spec 5.5 publication is not implemented) and are not edited by hand.

## Status on October 21, 2026

Read the current state with `python3 -m tools.approach_a status` or from the validation report. Do not copy counts into this file. When this file was written:

- One Google Antigravity CLI profile had been prepared from official documentation and exercised in a labeled rehearsal. No team member had confirmed its boundary and no manifest version had been approved.
- Its cells were agent-drafted and unreviewed, and one cell was still pending research.
- Nothing in the record was an accepted finding.

The rules in AGENTS.md still apply:
- A status other than "Not established from documentation" needs an evidence entry.
- "Not established" is never a zero or a score.
- There are no weights or rankings.
- Approach B or C results are never evidence for Approach A.
