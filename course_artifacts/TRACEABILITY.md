# Requirement, design, and test traceability

Maps each SRS specification (SRS 2.0, Oct. 18 submission) to DDD modules, DDD interfaces and the SRS test IDs. The module, interface and test columns are copied from the "Requirements Traceability by Specification" table of the submitted DDD (Oct. 18) and the spec titles from the SRS; a script generated them on Oct. 21. A mapping records document references only; it does not show that anything is implemented or that a test passes. Status values: Unreviewed, Reviewed (name reviewer and date in the commit), Gap. Module links follow the DDD (the DDD is authoritative for design links). The SRS also has its own clause-level traceability matrix; this file has not been reconciled with it.

Identifiers: `SRS:Spec`, `SRS:TC`, `SRS:NFR`, `SRS:F` for the SRS; `DDD:M01–M13` and `DDD:I01–I12` for design elements; `MATRIX:F01–F18` is a separate catalog. SRS constraints and assumptions (`SRS:C-1` to `C-10`, `SRS:A-1` to `A-8`) are numbered differently from the DDD (`DDD:C-1` to `C-9`, `DDD:A-1` to `A-7`); always use the prefix.

| SRS specification | DDD design elements | DDD interfaces | Concern (SRS spec title) | SRS test IDs | Status |
| --- | --- | --- | --- | --- | --- |
| SRS:Spec 1.1 | M06 | I03, I04, I05 | Network Egress Boundary | SRS:TC-1.1-1, SRS:TC-1.1-2, SRS:TC-1.1-3, SRS:TC-1.1-4, SRS:TC-1.1-5 | Unreviewed |
| SRS:Spec 1.2 | M03; host-provider boundary M04 | I01, I02, I10 | Secret Isolation and Zero-Token Boundary | SRS:TC-1.2-1, SRS:TC-1.2-2, SRS:TC-1.2-3, SRS:TC-1.2-4 | Unreviewed |
| SRS:Spec 1.3 | M06 | I03, I04 | Resource Quotas and Denial-of-Service (DoS) Defense | SRS:TC-1.3-1, SRS:TC-1.3-2, SRS:TC-1.3-3, SRS:TC-1.3-4, SRS:TC-1.3-5 | Unreviewed |
| SRS:Spec 1.4 | M03, M06 | I01, I03, I04, I10, I11 | Ephemeral Sandbox Lifecycle | SRS:TC-1.4-1, SRS:TC-1.4-2, SRS:TC-1.4-3 | Unreviewed |
| SRS:Spec 1.5 | M08 | I05, I06 | Fail-Closed Auditing | SRS:TC-1.5-1, SRS:TC-1.5-2, SRS:TC-1.5-3, SRS:TC-1.5-4 | Unreviewed |
| SRS:Spec 2.1 | M02, M05 | I01, I02, I03 | Multi-Agent Turn Management | SRS:TC-2.1-1, SRS:TC-2.1-2, SRS:TC-2.1-3 | Unreviewed |
| SRS:Spec 2.2 | M05 | I03, I04 | Execution Feedback Loop | SRS:TC-2.2-1, SRS:TC-2.2-2, SRS:TC-2.2-3 | Unreviewed |
| SRS:Spec 2.3 | M01, M03, M07 | I01, I05, I10 | Targeted File Patching | SRS:TC-2.3-1, SRS:TC-2.3-2, SRS:TC-2.3-3 | Unreviewed |
| SRS:Spec 2.4 | M02, M05 | I02, I03, I04 | Human-in-the-Loop Escalation | SRS:TC-2.4-1, SRS:TC-2.4-2, SRS:TC-2.4-3, SRS:TC-2.4-4, SRS:TC-2.4-5 | Unreviewed |
| SRS:Spec 2.5 | M01, M02, M04 | I01, I02 | Cost and Rate Guardrails | SRS:TC-2.5-1, SRS:TC-2.5-2, SRS:TC-2.5-3, SRS:TC-2.5-4, SRS:TC-2.5-5 | Unreviewed |
| SRS:Spec 3.1 | Testbed | HTTP; I01 task admission | Target API & State Determinism | SRS:TC-3.1-1, SRS:TC-3.1-2, SRS:TC-3.1-3, SRS:TC-3.1-4, SRS:TC-3.1-5, SRS:TC-3.1-6, SRS:TC-3.1-7, SRS:TC-3.1-8 | Unreviewed |
| SRS:Spec 3.2 | Testbed | HTTP / DOM | Client UI Synchronization | SRS:TC-3.2-1, SRS:TC-3.2-2 | Unreviewed |
| SRS:Spec 3.3 | Testbed | Local test command | Automated Regression Suite | SRS:TC-3.3-1, SRS:TC-3.3-2, SRS:TC-3.3-3 | Unreviewed |
| SRS:Spec 4.1 | M08 | I05, I06 | Evaluator-Owned Acceptance Suites | SRS:TC-4.1-1, SRS:TC-4.1-2, SRS:TC-4.1-3, SRS:TC-4.1-4, SRS:TC-4.1-5 | Unreviewed |
| SRS:Spec 4.2 | M04, M10 | I02, I07 | Run Telemetry Validation | SRS:TC-4.2-1, SRS:TC-4.2-2, SRS:TC-4.2-3, SRS:TC-4.2-4, SRS:TC-4.2-5, SRS:TC-4.2-6, SRS:TC-4.2-7 | Unreviewed |
| SRS:Spec 4.3 | M08 | I05, I06 | License Scan of Generated Code | SRS:TC-4.3-1, SRS:TC-4.3-2, SRS:TC-4.3-3 | Unreviewed |
| SRS:Spec 4.4 | M13 | I08, I12 | Automated Microsite Publishing | SRS:TC-4.4-1, SRS:TC-4.4-2, SRS:TC-4.4-3, SRS:TC-4.4-4, SRS:TC-4.4-5, SRS:TC-4.4-6, SRS:TC-4.4-7 | Unreviewed |
| SRS:Spec 4.5 | M12 | I12 | Trusted-Base Grading Workflow | SRS:TC-4.5-1, SRS:TC-4.5-2, SRS:TC-4.5-3 | Unreviewed |
| SRS:Spec 5.1 | M11 | I08 | Defined Profiles | SRS:TC-5.1-1 | Unreviewed |
| SRS:Spec 5.2 | M11 | I08 | Sourced Findings | SRS:TC-5.2-1 | Unreviewed |
| SRS:Spec 5.3 | M11 | I08 | Independent Review | SRS:TC-5.3-1 | Unreviewed |
| SRS:Spec 5.4 | M11 | I08 | Documentation Scope | SRS:TC-5.4-1 | Unreviewed |
| SRS:Spec 5.5 | M13 | I08 | Separate Publication | SRS:TC-5.5-1 | Unreviewed |
| SRS:Spec 6.1 | Approach B procedure | Procedure / I05 | Frozen Inputs and Isolated Snapshot | SRS:TC-6.1-1 | Unreviewed |
| SRS:Spec 6.2 | Approach B procedure | Procedure / I09 promotion only | Configuration Recording | SRS:TC-6.2-1 | Unreviewed |
| SRS:Spec 6.3 | M08 | I05, I06 | Shared Evaluator | SRS:TC-6.3-1 | Unreviewed |
| SRS:Spec 6.4 | Approach B procedure | Evidence manifest / I08 | Evidence Preservation | SRS:TC-6.4-1 | Unreviewed |
| SRS:Spec 6.5 | M13 | I08 | Raw-Result Reporting | SRS:TC-6.5-1 | Unreviewed |

## Nonfunctional requirements

| SRS NFR | Category | DDD modules / interfaces | SRS test ID | Status |
| --- | --- | --- | --- | --- |
| SRS:NFR-P1 | Performance | M13 / I08 | SRS:TC-NFR-P1 | Unreviewed |
| SRS:NFR-A1 | Availability | M13 / I08 | SRS:TC-NFR-A1 | Unreviewed |
| SRS:NFR-S1 | Security | M12 / I12 | SRS:TC-NFR-S1 | Unreviewed |
| SRS:NFR-S2 | Scalability | M02 / I01–I04 | SRS:TC-NFR-S2 | Unreviewed |
| SRS:NFR-R1 | Reliability | M02, M06, M10 / I07, I11 | SRS:TC-NFR-R1 | Unreviewed |
| SRS:NFR-R2 | Repeatability | M09, M13 / I06–I08 | SRS:TC-NFR-R2 | Unreviewed |
| SRS:NFR-PT1 | Portability | M06, M08 / I03–I06 | SRS:TC-NFR-PT1 | Unreviewed |
| SRS:NFR-U1 | Usability | M02 / I01 | SRS:TC-NFR-U1 | Unreviewed |
| SRS:NFR-U2 | Accessibility | M13 / I08 | SRS:TC-NFR-U2 | Unreviewed |
| SRS:NFR-M1 | Maintainability | M01, M04, M05 / I02, I09 | SRS:TC-NFR-M1 | Unreviewed |
| SRS:NFR-M2 | Maintainability | M09, M10 / I07/I08 | SRS:TC-NFR-M2 | Unreviewed |
| SRS:NFR-L1 | Licensing | M13 / I08 | SRS:TC-NFR-L1 | Unreviewed |

## Mapping notes and gaps found

A script compared the module IDs in the SRS 2.0 Design fields with the DDD table (Oct. 21). They agree for every spec except 6.1, 6.2 and 6.4, where the SRS Design field says the Approach B procedure replaces M01 and M03, M05 and M06, and M07 and M10, and the DDD lists no module. Interface links were not compared. The Oct. 18 edits that aligned the revision 1.2 Design fields with the DDD were not carried into SRS 2.0; they were not needed for module IDs.

The DDD adds no M14: the Testbed (Specs 3.1 to 3.3) and the Approach B procedure (Specs 6.1, 6.2, 6.4) are supporting subsystems without a numbered module. The submitted DDD now has rows for Specs 5.5 and 6.1 to 6.5, feature F7 and all twelve NFRs; they are the rows above and below. Test IDs for Specs 3.1, 4.1, 4.2 and 4.4 now run to TC-3.1-8, TC-4.1-5, TC-4.2-7 and TC-4.4-7.

Open items:

- Review every row above against both documents (DOC-055 history).
- Clause-level, pattern and interface coverage (the SRS matrix is at feature level for modules).

## Approach A (feature matrix)

SRS:F6 is delivered by SRS Requirement 5 and designed as DDD:M11 (module link: M11, M13 for publication, interface I08, ADR-14). SRS:H-9 covers SRS:TC-5.1-1 to SRS:TC-5.5-1 by document inspection only. In SRS 2.0, Spec 5.1.1 assesses the profiles in an approved, versioned manifest (P profiles, 18 × P cells; 36 only when P = 2), and the five-status/evidence-index method is retained as a proposed method resolution pending adoption. Matrix specification v0.3 (Oct. 21) adopts the manifest model. The record is the dataset in `assessment/` (repository root), maintained with `tools/approach_a/`; `sources/approach_a_assessment.md` now only points to it. The workbench's validator checks the structure that TC-5.1-1 to TC-5.4-1 inspect. A passing validation report is not a passed test case, and it is not H-9 completion. A status of Built in, Configuration or extension required, Custom implementation required, or Unavailable is Reviewed only with an evidence entry and a second reviewer. Not established from documentation is a valid completed status. A pending cell is not.

| Matrix element | Required by | Design | Record | Status (Oct. 21) |
| --- | --- | --- | --- | --- |
| Approved, versioned profile manifest (P) | SRS:Spec 5.1, TC-5.1-1 | M11 | `assessment/manifest.json` | One Antigravity CLI profile prepared from official documentation and exercised as a rehearsal; boundary not confirmed and manifest not approved |
| MATRIX:F01–F18 × P cells | SRS:Spec 5.2, TC-5.2-1 | M11 | `assessment/cells.json`; catalog in `assessment/catalog.json` (from spec tables) | Rehearsal drafts only (agent-drafted; one pending); none accepted |
| MATRIX:E01…, shared official-source index | SRS:Spec 5.2 (clause 5.2.1) | M11 | `assessment/sources.json` | Entries recorded for the rehearsal; each quote was found in its cited section, but nobody has yet reviewed whether the source supports the claim |
| Author, independent review, disagreement disposition | SRS:Spec 5.3, TC-5.3-1 | M11 | `assessment/cells.json`, `assessment/reviews.json` | None recorded |
| Documentation-only and no-score rules; work log | SRS:Specs 5.2 (clause 5.2.2), 5.4, TC-5.4-1 | M11, ADR-14 | Matrix spec v0.3; `assessment/worklog.jsonl`; validator rejects score and rank fields | Enforced by the validator; whether the work log is enough for TC-5.4-1 is a team call |
| Separate publication of Approach A findings | SRS:Spec 5.5, TC-5.5-1 | M13 | None (generated Markdown in `assessment/out/` is for review, not publication) | Not implemented |

MATRIX feature IDs (F01–F18) are not the SRS feature IDs (F1–F7). MATRIX:T1–T7 (tool categories) are not the SRS test-plan tasks T1–T8. MATRIX profile IDs (C01… in matrix spec v0.2; descriptive IDs such as `antigravity-cli` in the manifest) are not DDD constraints C-1 to C-9 or SRS constraints C-1 to C-10. MATRIX:E01… (evidence) are not DDD evidence references such as E15.
