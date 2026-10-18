# Requirement, design, and test traceability

Maps each SRS specification (revision 1.2) to DDD modules and the SRS test IDs found for it. A mapping records document references only; it does not show that anything is implemented or that a test passes. Status values: Unreviewed, Reviewed (name reviewer and date in the commit), Gap. Module links follow the DDD (the DDD is authoritative for design links). Clause-level, pattern, and interface coverage is pending (DOC-007).

Identifiers: `SRS:Spec`, `SRS:TC`, `SRS:NFR`, `SRS:F` for the SRS; `DDD:M01–M13` and `DDD:I01–I09` for design elements; `MATRIX:F01–F18` is a separate catalog. SRS constraints and assumptions (`SRS:C-1` to `C-10`, `SRS:A-1` to `A-8`) are numbered differently from the DDD (`DDD:C-1` to `C-9`, `DDD:A-1` to `A-7`); always use the prefix.

| SRS specification | DDD design elements | Concern | SRS test IDs | Status |
| --- | --- | --- | --- | --- |
| SRS:Spec 1.1 | M06 | Network boundary | SRS:TC-1.1-1, SRS:TC-1.1-2, SRS:TC-1.1-3, SRS:TC-1.1-4, SRS:TC-1.1-5 | Unreviewed |
| SRS:Spec 1.2 | M03 | Secret isolation | SRS:TC-1.2-1, SRS:TC-1.2-2, SRS:TC-1.2-3, SRS:TC-1.2-4 | Unreviewed |
| SRS:Spec 1.3 | M06 | Resource limits | SRS:TC-1.3-1, SRS:TC-1.3-2, SRS:TC-1.3-3, SRS:TC-1.3-4, SRS:TC-1.3-5 | Unreviewed |
| SRS:Spec 1.4 | M03, M06 | Sandbox lifecycle | SRS:TC-1.4-1, SRS:TC-1.4-2, SRS:TC-1.4-3 | Unreviewed |
| SRS:Spec 1.5 | M08 | Fail-closed auditing | SRS:TC-1.5-1, SRS:TC-1.5-2, SRS:TC-1.5-3 | Unreviewed |
| SRS:Spec 2.1 | M02, M05 | Turn/time control | SRS:TC-2.1-1, SRS:TC-2.1-2, SRS:TC-2.1-3 | Unreviewed |
| SRS:Spec 2.2 | M05 | Execution feedback | SRS:TC-2.2-1, SRS:TC-2.2-2, SRS:TC-2.2-3 | Unreviewed |
| SRS:Spec 2.3 | M01, M07 | File manifest/freeze | SRS:TC-2.3-1, SRS:TC-2.3-2, SRS:TC-2.3-3 | Unreviewed |
| SRS:Spec 2.4 | M02, M05 | Human escalation | SRS:TC-2.4-1, SRS:TC-2.4-2, SRS:TC-2.4-3, SRS:TC-2.4-4, SRS:TC-2.4-5 | Unreviewed |
| SRS:Spec 2.5 | M01, M02, M04 | Cost/rate/provider behavior | SRS:TC-2.5-1, SRS:TC-2.5-2, SRS:TC-2.5-3, SRS:TC-2.5-4, SRS:TC-2.5-5 | Unreviewed |
| SRS:Spec 3.1 | None numbered (testbed) | Baseline application | SRS:TC-3.1-1, SRS:TC-3.1-2, SRS:TC-3.1-3, SRS:TC-3.1-4, SRS:TC-3.1-5, SRS:TC-3.1-6 | Unreviewed |
| SRS:Spec 3.2 | None numbered (testbed) | Testbed client | SRS:TC-3.2-1, SRS:TC-3.2-2 | Unreviewed |
| SRS:Spec 3.3 | None numbered (testbed) | Baseline test execution | SRS:TC-3.3-1, SRS:TC-3.3-2, SRS:TC-3.3-3 | Unreviewed |
| SRS:Spec 4.1 | M08 | Independent suites | SRS:TC-4.1-1, SRS:TC-4.1-2, SRS:TC-4.1-3, SRS:TC-4.1-4 | Unreviewed |
| SRS:Spec 4.2 | M04, M10 | Telemetry | SRS:TC-4.2-1, SRS:TC-4.2-2, SRS:TC-4.2-3, SRS:TC-4.2-4, SRS:TC-4.2-5, SRS:TC-4.2-6 | Unreviewed |
| SRS:Spec 4.3 | M08 | License scanning | SRS:TC-4.3-1, SRS:TC-4.3-2, SRS:TC-4.3-3 | Unreviewed |
| SRS:Spec 4.4 | M13 | Static publication | SRS:TC-4.4-1, SRS:TC-4.4-2, SRS:TC-4.4-3, SRS:TC-4.4-4, SRS:TC-4.4-5, SRS:TC-4.4-6 | Unreviewed |
| SRS:Spec 4.5 | M12 | Trusted-base CI | SRS:TC-4.5-1, SRS:TC-4.5-2, SRS:TC-4.5-3 | Unreviewed |
| SRS:Spec 5.1 | M11 | Approach A profiles | SRS:TC-5.1-1 | Unreviewed |
| SRS:Spec 5.2 | M11 | Approach A sourced findings | SRS:TC-5.2-1 | Unreviewed |
| SRS:Spec 5.3 | M11 | Approach A independent review | SRS:TC-5.3-1 | Unreviewed |
| SRS:Spec 5.4 | M11 | Approach A documentation scope | SRS:TC-5.4-1 | Unreviewed |
| SRS:Spec 5.5 | M13 | Approach A separate publication | SRS:TC-5.5-1 | Unreviewed; not in the DDD specification table |
| SRS:Spec 6.1 | Approach B procedure | Pilot frozen inputs and snapshot | SRS:TC-6.1-1 | Unreviewed; not in the DDD |
| SRS:Spec 6.2 | Approach B procedure | Pilot configuration recording | SRS:TC-6.2-1 | Unreviewed; not in the DDD |
| SRS:Spec 6.3 | M08 | Pilot shared evaluator | SRS:TC-6.3-1 | Unreviewed; not in the DDD specification table |
| SRS:Spec 6.4 | Approach B procedure | Pilot evidence preservation | SRS:TC-6.4-1 | Unreviewed; not in the DDD |
| SRS:Spec 6.5 | M13 | Pilot raw-result reporting | SRS:TC-6.5-1 | Unreviewed; not in the DDD specification table |

## NFR mapping (SRS revision 1.2)

SRS revision 1.2 adds a Non-Functional Requirements section. The Design column below is the SRS's own; the DDD does not yet map these NFRs to modules.

| SRS NFR | Category | SRS test ID | Design per SRS | Status |
| --- | --- | --- | --- | --- |
| SRS:NFR-P1 | Performance | SRS:TC-NFR-P1 | M13 | Unreviewed; not mapped in the DDD |
| SRS:NFR-A1 | Availability | SRS:TC-NFR-A1 | GitHub Pages | Unreviewed; not mapped in the DDD |
| SRS:NFR-S1 | Security | SRS:TC-NFR-S1 | M12, ADR-11 | Unreviewed; not mapped in the DDD |
| SRS:NFR-S2 | Scalability | SRS:TC-NFR-S2 | M02 | Unreviewed; DDD System Size and Performance retains the six-hour target including grading and reruns; campaign timing not measured |
| SRS:NFR-R1 | Reliability | SRS:TC-NFR-R1 | M02, M10 | Unreviewed; not mapped in the DDD |
| SRS:NFR-R2 | Repeatability | SRS:TC-NFR-R2 | M09, M13 | Unreviewed; not mapped in the DDD |
| SRS:NFR-PT1 | Portability | SRS:TC-NFR-PT1 | M06, M08 | Unreviewed; not mapped in the DDD |
| SRS:NFR-U1 | Usability | SRS:TC-NFR-U1 | M02 | Unreviewed; not mapped in the DDD |
| SRS:NFR-U2 | Accessibility | SRS:TC-NFR-U2 | M13 | Unreviewed; not mapped in the DDD |
| SRS:NFR-M1 | Maintainability | SRS:TC-NFR-M1 | M04, M05 | Unreviewed; not mapped in the DDD |
| SRS:NFR-M2 | Maintainability | SRS:TC-NFR-M2 | M09, M10 | Unreviewed; not mapped in the DDD |
| SRS:NFR-L1 | Licensing | SRS:TC-NFR-L1 | Repository | Unreviewed; not mapped in the DDD |

## Mapping notes and gaps found

Module mappings follow the SRS column of the DDD System Decomposition table and the Requirements Traceability by Specification table in the DDD. An earlier seed also listed M04 and M06 for Spec 1.2, M06 for Spec 2.2, M03 and M06 for Spec 3.1, M03 and M08 for Spec 3.3, and M07 for Spec 4.1. They were removed because the DDD does not link them. SRS revision 1.2 listed some of the same links in its Design fields; they were changed to match the DDD on import (see Import notes in `sources/srs.md`).

Gaps closed by SRS revision 1.2: the NFR section, the traceability matrix and Appendix B now exist; TC-4.5-3 is defined (clause 4.5.3 now has a test); the Spec 2.5 limits have values. The DDD Requirements Traceability open items were updated on Oct. 18; the SRS-amendment note for schema 3 is not updated here.

Open items:

- Done in the DDD (Oct. 18): the 11 test cases that revision 1.2 adds (TC-1.1-5, TC-1.2-4, TC-2.3-3, TC-2.4-5, TC-2.5-5, TC-3.1-6, TC-4.1-4, TC-4.2-6, TC-4.4-5, TC-4.4-6 and TC-4.5-3) are listed; the removed Approach A test IDs (TC-5.1-2 to TC-5.5-2) are gone; the F3, F4 and F5 rows follow the SRS grouping; the Risks validation text says H-0 to H-9. The review of these edits is pending.
- Still open: the DDD has no feature F7 and no rows for Specs 6.1 to 6.5 (native-tool pilots), and no rows for the NFRs. The module links are pending team review.
- Testbed Specs 3.1 to 3.3 have no numbered DDD module.

## Approach A (feature matrix)

SRS:F6 is delivered by SRS Requirement 5 and designed as DDD:M11. Harness check SRS:H-9 covers SRS:TC-5.1-1 to SRS:TC-5.5-1 by document inspection only (SRS revision 1.2; earlier it was H-8 and TC-5.5-2). The matrix specification owns the catalog and method; `sources/track_a_assessment.md` is the working record. SRS revision 1.2 no longer lists the five status labels, the cell record fields or the `MATRIX:` IDs; the matrix specification and the record file still do. A status of Built in, Configuration or extension required, Custom implementation required, or Unavailable is Reviewed only with an evidence entry and a second reviewer. Not established from documentation is a valid completed status.

| Matrix element | Required by | Design | Record | Status |
| --- | --- | --- | --- | --- |
| MATRIX:F01–F18, features | SRS:Spec 5.2 | M11 | Status grid in `sources/track_a_assessment.md` | Catalog pinned to spec v0.2; cells not assessed |
| MATRIX:C01–C03, profiles (placeholders) | SRS:Spec 5.1 | M11 | Profile table in `sources/track_a_assessment.md` | Not defined; profile set undecided (see TODO.md) |
| MATRIX:E01…, evidence index | SRS:Spec 5.2 (source URL and access date per cell) | M11 | Evidence index in `sources/track_a_assessment.md` | Empty; revision 1.2 does not require an evidence index as such |
| Reviewer record | SRS:Spec 5.3 | M11 | Review table in `sources/track_a_assessment.md` | Empty |
| Documentation-only and no-score rules | SRS:Specs 5.2 (clause 5.2.2), 5.4 | M11, ADR-14 | Matrix spec; SRS Requirement 5 | Stated in text only |
| Separate publication of Approach A findings | SRS:Spec 5.5 | M13 (DDD F6 row) | None | I08 is not extended in the DDD data design; SRS revision 1.2 now requires a separate view |

MATRIX feature IDs (F01–F18) are not the SRS feature IDs (F1–F6). MATRIX:T1–T7 (tool categories) are not the SRS test-plan tasks T1–T8. MATRIX:C01… (profiles) are not DDD constraints C-1 to C-9 or SRS constraints C-1 to C-10. MATRIX:E01… (evidence) are not DDD evidence references such as E15.
