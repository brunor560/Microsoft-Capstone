# SRS Grading Rubric and Agent Review Guide

## 1. Purpose and authority

Use this document to review the Software Requirements Specification (SRS) and related course documentation before submission. It organizes the instructor-provided rubric into numbered criteria and actionable review checks for the agentic documentation workflow.

**Sources:** Instructor rubric text and SRS scoring screenshot supplied by the team on October 17, 2026. These are the grading authority; the checks and review templates below operationalize them. The screenshot supplies a 100-point criterion and three scoring bands. It does not assign separate weights to the detailed SRS criteria or specify deduction amounts. Section order is a review sequence, not an instructor-assigned weighting or ranking.

The instructor references alignment with standards such as IEEE 830/29148. This guide does not independently establish compliance with either standard or add requirements from their full texts.

### 1.1 Official scoring regions

The screenshot labels the rubric **SRS** and shows one criterion, **Professional Standards**, worth **100 points**. The band labels and ranges below reproduce the screenshot; descriptions summarize its wording.

| Rating | Displayed point range | Numerical interpretation | Instructor description (summary) |
| --- | --- | --- | --- |
| Full Marks | 100 to >90 pts | 90 < score ≤ 100 | All documents are present and well written; rubric and templates are followed; presentation is well done; timesheet supports the level of work. |
| Average Marks | 90 to >65 pts | 65 < score ≤ 90 | All documents are present; rubric is followed and templates mostly followed; presentation is reasonable; timesheet generally supports the level of work. |
| low marks | 65 to >0 pts | 0 < score ≤ 65 | Some documents are missing; timesheet does not support the presented work and detail; project will face issues; presentation is insufficient. |

**Boundary handling:** A score of 90 falls in Average Marks; 65 falls in low marks. The displayed ranges do not explicitly place a score of 0 in a band; do not infer an additional rule.

### 1.2 Applying the scoring regions

Review the submission holistically against the scoring descriptions above and the detailed instructor criteria in Sections 2–10. Include presentation and timesheet evidence when assessing the overall Professional Standards criterion.

- Report the best-supported scoring band with evidence and outstanding gaps.
- If asked for a numerical estimate, label it as an estimate out of 100, explain its basis, and state limitations from unavailable evidence.
- Do not invent subsection weights, fixed deduction amounts, or a formula that turns checklist completion into the official score.
- If only the SRS is available, give an SRS-focused assessment and identify the missing submission, presentation, or timesheet evidence that limits an overall score.

### 1.3 Team review assumptions (added by the team; not instructor text)

The team will include the figures, the timesheet, and the presentation in the actual submission. When reviewing a Markdown or Word draft of the SRS before then:

- Treat figures, the timesheet, and the presentation as **assumed present**. Do not mark them Blocked, do not list them as gaps, and do not lower the supported band because they are absent from the draft under review.
- Still review everything that can be checked from the text: figure numbers, captions, and cross-references; whether the prose matches what each figure is described as showing; and consistency among scenarios, requirements, and acceptance criteria.
- Do not judge the content or notation of a figure that was not supplied. Record it as "assumed present, not reviewed".
- An assumption is not evidence. Do not state that the timesheet supports the work or that the presentation is well done. Phrase the band as conditional, for example "Average Marks, assuming the figures, timesheet, and presentation meet the Full Marks descriptions".
- Section 1.2's instruction to flag missing presentation or timesheet evidence does not apply to these three items. The required-document list and the AI citation format are not covered by this assumption; Section 2 still applies to them.
- If a figure, timesheet, or presentation is supplied, review it as in Sections 1.1 and 1.2.


## 2. Submission completeness, status reporting, references, and AI attribution

**Instructor criteria:** All required documents must be present and professionally written. Status reports must accurately describe specific project items. References must sufficiently support the project, and all instances of AI use must be referenced properly.

- [ ] Check the submission against the course's required-document list; report any missing or unavailable items.
- [ ] Confirm that required templates are followed and the presentation meets the quality described in the scoring bands.
- [ ] Check whether timesheets support the reported level of work and detail.
- [ ] Confirm that status reports identify concrete work, progress, and unresolved items consistently with available project evidence.
- [ ] Check that claims of completion or validation are supported; distinguish planned, implemented, and verified work.
- [ ] Confirm that references support relevant claims and are cited consistently in the text and reference list.
- [ ] Confirm that AI assistance is disclosed and attributed according to the applicable course instructions.
- [ ] Check professional tone, grammar, terminology, formatting, and consistency across submitted documents.

**Agent guidance:** The supplied text does not enumerate every required document or prescribe an AI citation format. Flag those checks as blocked when the relevant course instructions are unavailable; do not invent them.

## 3. Scope, objectives, and operating environment

**Instructor criteria:** Clearly define system scope and operating environment; align requirements with user needs or business objectives.

- [ ] Explain the system purpose, intended users, and goals.
- [ ] State scope boundaries so included and excluded behavior can be distinguished.
- [ ] Describe the operating environment and relevant external systems or dependencies.
- [ ] Identify assumptions and constraints that affect required behavior or feasibility.
- [ ] Ensure requirements support the stated scope and objectives.

**Review evidence:** Scope and environment sections, stakeholder or user needs, objectives, and links from requirements to those needs or objectives.

## 4. Functional requirements and specifications

**Instructor criteria:** Functional requirements and specifications must be rigorously structured, atomic, uniquely identifiable, unambiguous, testable, and traceable. The instructor explicitly requires requirements and specifications to be **numbered, measurable, unique, and in priority order**.

- [ ] Give each requirement and specification a unique number or identifier.
- [ ] State one independently verifiable obligation per requirement; split compound obligations when needed.
- [ ] Use clear normative language, such as “The system shall …,” to distinguish obligations from background explanation.
- [ ] Define relevant triggers, conditions, inputs, observable behavior, and expected outputs.
- [ ] Provide measurable pass/fail criteria. Behavioral requirements may use observable outcomes rather than numeric thresholds.
- [ ] Remove vague terms, ambiguous references, contradictory statements, and duplicate obligations.
- [ ] Link each requirement to a user need or business objective.
- [ ] Assign priority using a defined scheme and present requirements in priority order.

**Agent guidance:** Keep identifiers stable when reordering by priority so existing traceability links remain valid. Do not silently choose priorities on behalf of stakeholders; flag unresolved priorities for team review.

## 5. Non-functional requirements and quality attributes

**Instructor criteria:** Categorize non-functional requirements and quantify them wherever possible. Named categories are performance, scalability, security, usability, reliability, and maintainability. Examples of measures include latency thresholds, throughput targets, and mean time between failures (MTBF).

- [ ] Address each named category, or explain why a category is not applicable to the system.
- [ ] Identify quality requirements with unique IDs and defined priorities.
- [ ] Specify a numeric threshold where appropriate, or another objective acceptance criterion.
- [ ] Define relevant measurement conditions, such as workload, environment, observation period, and units.
- [ ] Ensure targets are technically feasible within the project's constraints.
- [ ] Link each quality requirement to a verification method and acceptance criteria.

**Agent guidance:** The rubric's metric examples are illustrative, not mandatory metrics for every project. Do not invent thresholds, workloads, or reliability claims to fill gaps. Record proposed values separately until the team approves them.

## 6. Use cases or user stories and system context

**Instructor criteria:** Include well-formed use cases or user stories and system context diagrams that make architectural implications evident.

- [ ] Include use cases or user stories covering the principal user goals and interactions.
- [ ] State actors, goals, relevant conditions, and expected outcomes clearly.
- [ ] Cover relevant alternative paths and exceptions.
- [ ] Connect scenarios to the requirements they motivate or validate.
- [ ] Include system context diagrams showing the system boundary, external actors or systems, and meaningful interactions.
- [ ] Keep scenario descriptions, diagrams, and requirements consistent.
- [ ] Make externally imposed boundaries and interaction constraints evident without unnecessarily prescribing internal implementation.

**Agent guidance:** A use-case format may use preconditions, main flow, alternatives, and postconditions; a user-story format may use explicit acceptance criteria. These are suggested review structures, not additional instructor-mandated templates.

## 7. Bidirectional traceability and acceptance criteria

**Instructor criteria:** Top-tier work exhibits bidirectional traceability between requirements and validation/test cases, explicit acceptance criteria, and prioritization.

- [ ] Trace requirements to their originating user needs or business objectives.
- [ ] Trace each requirement to one or more validation or test cases appropriate to its verification.
- [ ] Trace validation or test cases back to the requirements they verify.
- [ ] Define explicit expected results or acceptance criteria that permit a pass/fail decision.
- [ ] Identify requirements without verification coverage and tests without a justified requirement link.
- [ ] Check that all linked IDs exist and that links remain consistent after edits.

**Suggested traceability structure:**

| Need/objective ID | Requirement ID | Priority | Validation/test ID | Acceptance criteria | Verification status/evidence |
| --- | --- | --- | --- | --- | --- |
| `<source ID>` | `<requirement ID>` | `<defined priority>` | `<test ID>` | `<observable pass/fail condition>` | `<planned or supported result>` |

**Agent guidance:** A test specification can establish planned verification coverage before implementation. It does not establish that the requirement has passed a test. Keep planned coverage and executed results distinct.

## 8. Domain model, constraints, edge cases, and failure modes

**Instructor criteria:** Demonstrate domain modeling discipline through clear entities, constraints, and assumptions, with edge-case consideration and failure modes.

- [ ] Define key domain entities, terms, and relevant relationships consistently.
- [ ] State relevant data constraints, permitted values, and business rules.
- [ ] Make assumptions and external dependencies explicit.
- [ ] Address relevant boundary conditions, invalid inputs, unavailable dependencies, and failed operations.
- [ ] Define observable failure behavior and applicable recovery expectations.
- [ ] Include acceptance criteria and verification coverage for specified edge and failure behavior.

**Agent guidance:** Select cases relevant to the system's scope. Do not add features or internal mechanisms merely to make the document appear more comprehensive.

## 9. Clarity, correctness, consistency, and feasibility

**Instructor criteria:** Eliminate ambiguity and implementation bias; maintain internal consistency. Reviewers assess clarity, alignment with goals, and technical realism within constraints.

- [ ] Replace vague expressions such as “fast” or “user-friendly” with objective criteria.
- [ ] Use the same terms, IDs, values, assumptions, and boundaries throughout the SRS.
- [ ] Resolve contradictions among requirements, scenarios, diagrams, and acceptance criteria.
- [ ] Remove redundant requirements without losing valid obligations or links.
- [ ] Describe required outcomes without unjustified implementation choices.
- [ ] Identify mandated technical constraints explicitly and explain their source.
- [ ] Check that requirements are feasible within available time, resources, dependencies, and project limits.

## 10. Professional structure and document control

**Instructor criteria:** Follow a professional standard structure, including revision history, glossary, and appendices where appropriate.

- [ ] Organize the document so scope, environment, requirements, and supporting material are easy to locate.
- [ ] Include a revision history that accurately reflects document changes.
- [ ] Define domain-specific terms and abbreviations in a glossary where appropriate.
- [ ] Use appendices where they improve access to supporting information.
- [ ] Maintain consistent headings, numbering, tables, diagram labels, and cross-references.
- [ ] Proofread for professional writing and remove unresolved placeholders before submission, or explicitly report remaining gaps.

## 11. Explicit deduction risks

The instructor identifies the following as deduction risks and indicators of weak engineering rigor:

1. Ambiguous language.
2. Redundant requirements or specifications.
3. Missing constraints.
4. Missing measurable criteria.
5. Poor traceability.

Also report unmet criteria from Sections 2–10. Use the official scoring regions in Section 1.1 for an overall band assessment. Numerical estimates must follow Section 1.2; do not invent fixed point deductions or subsection weights.

## 12. Agent review and revision workflow

This section is workflow guidance derived from the rubric, not additional grading criteria.

1. **Establish inputs.** Read the current SRS, this rubric, and relevant available course instructions and project evidence. Record missing inputs.
2. **Check submission completeness.** Review required documents, templates, status-report accuracy, timesheets, presentation, references, and AI attribution.
3. **Audit individual requirements.** Check numbering, atomicity, uniqueness, measurability, priority, acceptance criteria, and source links.
4. **Audit system coverage.** Review scope, environment, functional and quality requirements, scenarios, context diagrams, domain rules, constraints, and failure behavior.
5. **Audit traceability.** Check links in both directions and distinguish planned verification from supported execution results.
6. **Check consistency and presentation.** Review terminology, feasibility, implementation bias, document structure, and professional writing.
7. **Record findings.** Cite exact requirement IDs or document sections, identify the relevant rubric criterion, and propose a concrete correction.
8. **Revise within approved scope.** Fix supported editorial and consistency issues. Flag unresolved stakeholder decisions, priorities, thresholds, and constraints rather than inventing them.
9. **Synchronize related documents.** After approved requirement changes, update affected links, tests, status reports, and the team's Tasks/ToDo document as applicable.
10. **Report the assessment and residual gaps.** State what was reviewed, the supported scoring band and its rationale, what changed, and what remains unresolved or blocked. Apply Section 1.2 when a numerical estimate is requested.

### Review finding format

| Finding ID | Rubric section | SRS location / requirement ID | Finding and evidence | Proposed correction | Status |
| --- | --- | --- | --- | --- | --- |
| `SRS-REV-001` | `<section>` | `<location or ID>` | `<specific gap>` | `<action or decision needed>` | `<status>` |

Use **Meets**, **Partial**, **Missing**, **Blocked**, or **Not applicable (with rationale)** for criterion assessments. These are review labels, not instructor grade bands. Record improvement urgency separately from the priority of the product requirement.

### Review completion check

- [ ] Every rubric section has an evidence-based assessment or a stated limitation.
- [ ] Requirements and specifications have been checked for numbering, measurability, uniqueness, and priority order.
- [ ] Outstanding decisions and gaps are recorded in the team's task tracking document.
- [ ] No unsupported claims of compliance, completion, test success, or numerical grades have been introduced.
