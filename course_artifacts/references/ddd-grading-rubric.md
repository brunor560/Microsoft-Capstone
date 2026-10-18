# Agentic Evaluation Rubric: Detailed Design & Architecture Document

## 1. Agent Role & Directives
You are an expert Software and Systems Architecture Reviewer. Use this rubric to systematically evaluate a **Detailed Design / Architecture Document** (and accompanying presentation materials, if provided). 

### Evaluation Workflow:
1. **Verify Deliverables & Disclosures:** Check for the presence of all required architectural views, AI usage disclosures, and timesheet reflections.
2. **Assess Technical Depth & Rigor:** Evaluate the document against the Core Technical Checklist (Section 3).
3. **Check for Automatic Deductions:** Scan for anti-patterns and red flags (Section 4).
4. **Determine Scoring Tier:** Map the findings to the 200-point Scoring Matrix (Section 5) and output a structured review with actionable feedback.

---

## 2. Grade Weighting Context
* **Document & In-Class PPT Presentation (90%):** Must translate the Software Requirements Specification (SRS) into a coherent, implementable, production-grade system blueprint grounded in recognized frameworks (e.g., ISO/IEC/IEEE 42010).
* **Peer Evaluation Criteria (10%):** Focuses on architectural rigor, requirement-to-design traceability, internal consistency across diagrams, and technical feasibility.

### Team review assumptions (added by the team; not part of the rubric text above or below)
The team will include the diagrams, the timesheet, and the in-class presentation in the actual submission. When reviewing a Markdown or Word draft of the DDD before then:
* **Assume present:** Treat the diagrams, the timesheet, and the presentation as present. Do not list them as gaps, mark them missing, or lower the tier because they are absent from the draft under review.
* **Still review the text:** Check figure numbers, captions, and cross-references, and check that the prose describing each view agrees with the other views and with the SRS.
* **No judging unseen content:** Do not assess the content or notation (C4/UML) of a diagram that was not supplied, and do not apply the "Superficial Diagrams" deduction to it. Record it as "assumed present, not reviewed".
* **Assumption is not evidence:** Do not state that the timesheet reflects proper time management or that diagrams are consistent. Phrase the tier as conditional, for example "Above Average, assuming the diagrams, timesheet, and presentation meet the Excellent descriptions". Section 3.E timesheet and AI-disclosure checks that depend on supplied evidence are "assumed present, not reviewed"; AI-disclosure marking in the text is still reviewable.
* **Supplied items:** If a diagram, timesheet, or presentation is supplied, review it as the rubric describes.


---

## 3. Core Technical Checklist

### A. Framework & Architectural Style
- [ ] **Framework Grounding:** Aligns with recognized standards (e.g., ISO/IEC/IEEE 42010).
- [ ] **Style Definition:** Clearly states chosen architectural style(s) (e.g., layered, microservices, event-driven).
- [ ] **Explicit Rationale:** Ties architectural style directly to SRS requirements and system constraints.

### B. Required Architectural Views (4+1 View Model + Data View)
Supported by C4 models or UML artifacts, with zero contradictions across views:
- [ ] **Logical View:** Component decomposition and clear responsibilities.
- [ ] **Physical View:** Deployment topology and hardware/software infrastructure integration.
- [ ] **Data View (Mandatory Addition):** Database schemas, data flows, and persistence strategies.
- [ ] **Behavioral / Process View:** Sequence and/or activity diagrams for key system workflows.
- [ ] **Development / Scenarios View:** Addressed if utilizing the full 4+1 View Model.

### C. Interfaces & Engineering Rigor
- [ ] **Interface Contracts:** Precisely defines API contracts, data formats, communication protocols, and error-handling strategies between components.
- [ ] **Design Principles:** Demonstrates modularity (loose coupling, high cohesion), extensibility, SOLID principles, and separation of concerns.
- [ ] **Trade-Off Analysis:** Justifies key design decisions by analyzing trade-offs (e.g., performance vs. scalability, consistency vs. availability).
- [ ] **SRS Traceability:** Clearly maps SRS requirements to specific design elements, ensuring every major requirement is realized.

### D. Operational Viability & Quantitative Targets
- [ ] **Cross-Cutting Concerns:** Addresses security architecture, observability (logging, monitoring, tracing), fault tolerance, and configuration management.
- [ ] **Quantitative Metrics:** Includes estimated load, scaling strategies, latency budgets, and capacity planning.
- [ ] **Risk & Validation:** Identifies technical risks, assumptions, mitigation strategies, and validation approaches (e.g., prototyping, simulation, benchmarking).

### E. Administrative & Compliance Requirements
- [ ] **AI Usage Disclosure:** Explicitly marks AI-assisted sections, diagrams, or decisions (via footnotes, inline tags, or appendix) to distinguish human judgment from AI generation.
- [ ] **Timesheet:** Accurately reflects proper time management and matches the level of demonstrated work.

---

## 4. Red Flags & Deduction Triggers
Apply point deductions if any of the following anti-patterns are present:
* **SRS Restatement:** Document merely repeats requirements without providing an implementable design.
* **Component Deficit:** Fewer than 4 components are properly addressed.
* **Superficial Diagrams:** Diagrams lack detail, standard notation (C4/UML), or contradict the explanatory text/other diagrams.
* **Missing Interfaces:** Components are shown interacting without defined API contracts, protocols, or data formats.
* **Unjustified Decisions:** Technologies or patterns are selected without trade-off analysis or link to requirements.
* **Ignored Non-Functional Requirements (NFRs):** Failure to address operational viability, quantitative targets, or cross-cutting concerns.

---

## 5. Scoring Matrix (200 Points Total)

| Tier | Point Range | Evaluation Criteria |
| :--- | :--- | :--- |
| **Excellent** | **200 to >185 pts** | • **Architecture:** Production-grade, rigorous, fully traceable to SRS, and internally consistent across all views.<br>• **Documentation:** Comprehensive hardware/software architecture, clear diagrams, proper decomposition, detailed modules, and an ideal balance of diagrams and explanatory text.<br>• **Depth:** All components, trade-offs, quantitative targets, and cross-cutting concerns are justified with genuine depth.<br>• **Timesheet:** Reflects proper time management. |
| **Above Average** | **185 to >160 pts** | • **Architecture:** Sound and traceable with good engineering decomposition; only minor gaps in consistency or justification.<br>• **Documentation:** Well-documented with adequate diagrams and clear explanations for most components.<br>• **Depth:** Most cross-cutting concerns and trade-offs are addressed, though not always with equal depth.<br>• **Timesheet:** Reflects good time management. |
| **Average** | **160 to >140 pts** | • **Architecture:** Functional and covers required views/sections, but lacks detail or clarity in some areas.<br>• **Documentation:** Some engineering principles evident; diagrams are present but may be incomplete.<br>• **Depth:** Justification is thin in places; cross-cutting concerns and trade-offs are only superficially addressed.<br>• **Timesheet:** Does not accurately reflect demonstrated work. |
| **Below Average** | **140 to >120 pts** | • **Architecture:** Significant gaps, weak traceability, or poor integration between hardware and software components.<br>• **Documentation:** Minimal documentation, unclear presentation, and several required sections present in name only.<br>• **Depth:** Missing or shallow interface definitions; key decisions stated without justification.<br>• **Timesheet:** Does not match the level of work. |
| **Failing** | **120 to >0 pts** | • **Architecture:** Missing, incomplete, internally inconsistent, incomprehensible, or effectively a restatement of the SRS.<br>• **Documentation:** Fewer than 4 components properly addressed, or unacceptable quality in others.<br>• **Depth:** Required views, interfaces, or justifications are largely absent; fails to demonstrate a real design.<br>• **Timesheet:** Poorly reflects the work event. |

---

## 6. Recommended Agent Output Format
When completing a review using this file, structure the evaluation report as follows:
1. **Assigned Tier & Score:** `[Tier Name] ([X] / 200 pts)`
2. **Executive Summary:** High-level assessment of whether the document reads as a production-grade blueprint.
3. **Checklist Audit:** Summary of passed/failed items from Section 3 (Views, Interfaces, Operational Viability, Compliance).
4. **Identified Red Flags:** Specific contradictions, missing interfaces, or superficial areas.
5. **Actionable Recommendations:** Prioritized list of improvements required to reach the next scoring tier.