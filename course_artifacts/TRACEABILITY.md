# Requirement, design, and test traceability

Maps each SRS specification to DDD modules and the SRS test IDs found for it. A mapping records document references only; it does not show that anything is implemented or that a test passes. Status values: Unreviewed, Reviewed (name reviewer and date in the commit), Gap. Clause-level, NFR, pattern, and interface coverage is pending (DOC-007). `MATRIX:F01–F18` rows will be added with DOC-040.

Identifiers: `SRS:Spec`, `SRS:TC`, `SRS:NFR`, `SRS:F` for the SRS; `DDD:M01–M13` and `DDD:I01–I09` for design elements; `MATRIX:F01–F18` is a separate catalog.

| SRS specification | DDD design elements | Concern | SRS test IDs found | Status |
| --- | --- | --- | --- | --- |
| SRS:Spec 1.1 | M06 | Network boundary | SRS:TC-1.1-1, SRS:TC-1.1-2, SRS:TC-1.1-3, SRS:TC-1.1-4 | Unreviewed |
| SRS:Spec 1.2 | M03, M04, M06 | Secret isolation | SRS:TC-1.2-1, SRS:TC-1.2-2, SRS:TC-1.2-3 | Unreviewed |
| SRS:Spec 1.3 | M06 | Resource limits | SRS:TC-1.3-1, SRS:TC-1.3-2, SRS:TC-1.3-3, SRS:TC-1.3-4, SRS:TC-1.3-5 | Unreviewed |
| SRS:Spec 1.4 | M03, M06 | Sandbox lifecycle | SRS:TC-1.4-1, SRS:TC-1.4-2, SRS:TC-1.4-3 | Unreviewed |
| SRS:Spec 1.5 | M08 | Fail-closed auditing | SRS:TC-1.5-1, SRS:TC-1.5-2, SRS:TC-1.5-3 | Unreviewed |
| SRS:Spec 2.1 | M02, M05 | Turn/time control | SRS:TC-2.1-1, SRS:TC-2.1-2, SRS:TC-2.1-3 | Unreviewed |
| SRS:Spec 2.2 | M05, M06 | Execution feedback | SRS:TC-2.2-1, SRS:TC-2.2-2, SRS:TC-2.2-3 | Unreviewed |
| SRS:Spec 2.3 | M01, M07 | File manifest/freeze | SRS:TC-2.3-1, SRS:TC-2.3-2 | Unreviewed |
| SRS:Spec 2.4 | M02, M05 | Human escalation | SRS:TC-2.4-1, SRS:TC-2.4-2, SRS:TC-2.4-3, SRS:TC-2.4-4 | Unreviewed |
| SRS:Spec 2.5 | M01, M02, M04 | Cost/rate/provider behavior | SRS:TC-2.5-1, SRS:TC-2.5-2, SRS:TC-2.5-3, SRS:TC-2.5-4 | Unreviewed |
| SRS:Spec 3.1 | M03, M06 | Baseline application | SRS:TC-3.1-1, SRS:TC-3.1-2, SRS:TC-3.1-3, SRS:TC-3.1-4, SRS:TC-3.1-5 | Unreviewed |
| SRS:Spec 3.2 | Testbed UI; module mapping pending | Testbed client | SRS:TC-3.2-1, SRS:TC-3.2-2 | Unreviewed |
| SRS:Spec 3.3 | M03, M08 | Baseline test execution | SRS:TC-3.3-1, SRS:TC-3.3-2, SRS:TC-3.3-3 | Unreviewed |
| SRS:Spec 4.1 | M07, M08 | Independent suites | SRS:TC-4.1-1, SRS:TC-4.1-2, SRS:TC-4.1-3 | Unreviewed |
| SRS:Spec 4.2 | M04, M10 | Telemetry | SRS:TC-4.2-1, SRS:TC-4.2-2, SRS:TC-4.2-3, SRS:TC-4.2-4, SRS:TC-4.2-5 | Unreviewed |
| SRS:Spec 4.3 | M08 | License scanning | SRS:TC-4.3-1, SRS:TC-4.3-2, SRS:TC-4.3-3 | Unreviewed |
| SRS:Spec 4.4 | M13 | Static publication | SRS:TC-4.4-1, SRS:TC-4.4-2, SRS:TC-4.4-3, SRS:TC-4.4-4 | Unreviewed |
| SRS:Spec 4.5 | M12 | Trusted-base CI | SRS:TC-4.5-1, SRS:TC-4.5-2, SRS:TC-4.5-3 | Unreviewed |
| SRS:Spec 5.1 | M11 | Track A profile definition | SRS:TC-5.1-1, SRS:TC-5.1-2 | Unreviewed |
| SRS:Spec 5.2 | M11 | Track A catalog and status labels | SRS:TC-5.2-1, SRS:TC-5.2-2, SRS:TC-5.2-3 | Unreviewed |
| SRS:Spec 5.3 | M11 | Track A evidence and cell records | SRS:TC-5.3-1, SRS:TC-5.3-2, SRS:TC-5.3-3 | Unreviewed |
| SRS:Spec 5.4 | M11 | Track A review and completion | SRS:TC-5.4-1, SRS:TC-5.4-2 | Unreviewed |
| SRS:Spec 5.5 | M11 | Track A scope boundary and presentation | SRS:TC-5.5-1, SRS:TC-5.5-2 | Unreviewed |

## Track A (feature matrix)

SRS:F6 is delivered by SRS Requirement 5 and designed as DDD:M11. Harness check SRS:H-8 covers SRS:TC-5.1-1 to SRS:TC-5.5-2 by document inspection only. The matrix specification owns the catalog and method; `sources/track_a_assessment.md` is the working record. A status of Built in, Configuration or extension required, Custom implementation required, or Unavailable is Reviewed only with an evidence entry and a second reviewer. Not established from documentation is a valid completed status.

| Matrix element | Required by | Design | Record | Status |
| --- | --- | --- | --- | --- |
| MATRIX:F01–F18, features | SRS:Spec 5.2 | M11 | Status grid in `sources/track_a_assessment.md` | Catalog pinned to spec v0.2; cells not assessed |
| MATRIX:C01–C03, profiles (placeholders) | SRS:Spec 5.1 | M11 | Profile table in `sources/track_a_assessment.md` | Not defined; profile set undecided (see TODO.md) |
| MATRIX:E01…, evidence index | SRS:Spec 5.3 | M11 | Evidence index in `sources/track_a_assessment.md` | Empty |
| Reviewer record | SRS:Spec 5.4 | M11 | Review table in `sources/track_a_assessment.md` | Empty |
| Documentation-only and no-score rules | SRS:Specs 5.2, 5.5 | M11, ADR-13 | Matrix spec; SRS Requirement 5 | Stated in text only |
| Publication of Track A | None | M13 (I08) not extended | None | Explicit gap: not required unless the team decides |

MATRIX feature IDs (F01–F18) are not the SRS feature IDs (F1–F6). MATRIX:T1–T7 (tool categories) are not the SRS test-plan tasks T1–T8. MATRIX:C01… (profiles) are not DDD constraints C-1 to C-9. MATRIX:E01… (evidence) are not DDD evidence references such as E15.
