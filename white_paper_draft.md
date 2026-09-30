# Agentic Development for Software Engineering: An Enterprise Evaluation Framework & Benchmark

**CIS 4910 Senior Project – Capstone Series**  
**Institution:** Bellini College of Artificial Intelligence, Cybersecurity and Computing, University of South Florida  
**Industry Partner:** Microsoft Corporation  
**Authors:** Joseph Bressani, Bruno Rocha, Kapil Srikanth, Ross Volenec  
**Industry Sponsors:** Chad Hage, Brad Lawrence  
**Faculty Instructor:** Scot Hollingsworth  
**Date:** Fall 2026  

---

## Executive Summary & Core Epic

### The 10,000-Seat Procurement Problem
> *"I'm a Solutions Architect with an enterprise client wanting to buy 10,000 seats for my institution. Which platform should I choose? How do I compare and grade them using an evidence-based framework?"*

* **Context & Objective:** Briefly state why this evaluation exists. Summarize how enterprise software engineering is moving from autocomplete assistants to autonomous multi-agent loops, and explain the need for an empirical, harness-focused decision matrix.
* **The Dual-Track Architecture:**
  * **Track A (Outer Loop):** Commercial Platform & IDE Harness Audit (GitHub Copilot / VS Code, Claude Code CLI, Google Anti-Gravity).
  * **Track B (Inner Loop):** Headless AutoGen Orchestration & Trajectory Benchmarking within air-gapped Docker sandboxes.
* **High-Level Recommendation Preview:** [Placeholder: 1–2 paragraphs highlighting the top-performing harness for the 10,000-seat deployment based on security, DevEx, throughput, and total cost of ownership.]

---

## 1. Why AI Agents for Software Engineering
*(Priority: Should Have | Target Completion: Weeks 6–7)*

* **1.1 The Shift from Autocomplete to Autonomy:**
  * Detail the transition from inline code completion (e.g., GitHub Copilot v1) to full-lifecycle agentic loops (issue intake $\rightarrow$ spec decomposition $\rightarrow$ patch synthesis $\rightarrow$ test verification $\rightarrow$ pull request).
* **1.2 Industry Benchmarks & Quantitative Drivers:**
  * Document cited productivity gains, cognitive offloading, and toil reduction.
  * Contrast enterprise marketing claims against measured friction in real-world pipelines.
* **1.3 The Enterprise Business Case (and Counter-Case):**
  * Evaluate ROI considerations for large organizations: developer velocity vs. review bottlenecks, compute/token costs, and code maintenance overhead.

---

## 2. What Are AI Agents for Software Engineering
*(Priority: Should Have | Target Completion: Weeks 6–7)*

* **2.1 Architectural Taxonomies:**
  * Clear definitions distinguishing AI Assistants, Copilots, and Autonomous Agents.
  * Core agent patterns: ReAct (Reason + Act), Plan-and-Execute, and Multi-Agent Collaboration.
* **2.2 Core Components of an Engineering Agent:**
  * **LLM Backbone:** Reasoning engine and token limits.
  * **Tool Execution Layer:** Terminal execution, file read/write, compiler and linter invocation.
  * **Memory & Context:** Workspace indexing, ephemeral session memory, and directory instructions (`CLAUDE.md`, `.github/copilot-instructions.md`).
  * **Orchestration Harness:** The execution loop governing agent turn-taking and stopping conditions.
* **2.3 Specialized Engineering Personas:**
  * Architectural breakdown of Coder Agents, Testing Agents, Review Agents, and Orchestrator/Scrum Agents.

---

## 3. Agentic Development Landscape & Comparative Benchmarks
*(Priority: Must Have [Critical Path] | Target Completion: Weeks 11–13)*

* **3.1 Evaluated Ecosystems:**
  * **Microsoft / GitHub:** GitHub Copilot, VS Code Extensions, AutoGen v0.4+.
  * **Anthropic:** Claude Code CLI, Sonnet/Opus models.
  * **Google:** Anti-Gravity, Gemini CLI.
  * **Open-Source / Emerging:** Cursor, OpenAI Codex CLI.
* **3.2 The Standardized Baseline Reference Testbed:**
  * Describe the canonical 3-tier reference application used across all evaluations.
  * Standardized backlog tasks (feature addition, bug fix, prompt injection trap, refactor).
* **3.3 The Enterprise Platform Comparison Matrix:**

| Evaluation Metric | Weight | GitHub Copilot / VS Code | Claude Code CLI | Google Anti-Gravity | AutoGen Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Functionality ($F$)** | 35% | [Score] | [Score] | [Score] | [Score] |
| **Security ($S$)** | 25% | [Score] | [Score] | [Score] | [Score] |
| **Code Quality ($Q$)** | 20% | [Score] | [Score] | [Score] | [Score] |
| **Token Efficiency ($T$)** | 10% | [Score] | [Score] | [Score] | [Score] |
| **Human Autonomy ($H$)** | 10% | [Score] | [Score] | [Score] | [Score] |
| **Composite Score** | **100%** | **[Total]** | **[Total]** | **[Total]** | **[Total]** |

* **3.4 Live Demonstration Summaries & Trajectory Analysis:**
  * [Demo Link & Script: GitHub Copilot end-to-end task run]
  * [Demo Link & Script: Claude Code CLI end-to-end task run]
  * [Demo Link & Script: AutoGen Docker headless runner]

---

## 4. When to Use / Use with Caution / Avoid: A Decision Framework
*(Priority: Should Have | Target Completion: Weeks 7–8)*

* **4.1 Tier 1: High-Confidence Autonomous Use:**
  * Characteristics: Well-scoped tasks, deterministic test coverage, modular CRUD endpoints, boilerplate test generation.
  * *Demonstrated Scenario:* [Brief overview of automated green-field feature addition].
* **4.2 Tier 2: Use with Caution (Human-in-the-Loop Required):**
  * Characteristics: Ambiguous specifications, architectural refactoring, legacy codebases with low test coverage.
  * *Demonstrated Scenario:* [Brief overview of multi-file refactoring under human check-offs].
* **4.3 Tier 3: Avoid / Restrict:**
  * Characteristics: Cryptographic implementations, safety-critical systems, compliance-regulated pipelines, production deployment execution.
  * *Demonstrated Scenario:* [Failure analysis showing agent failure under unconstrained production permissions].

---

## 5. Tooling, Interoperability, and MCP Tool Chains
*(Priority: Must Have | Target Completion: Weeks 9–10)*

* **5.1 End-to-End Tool Chain Reference Architecture:**
  * Diagram and description of the tool stack: IDE plugins $\rightarrow$ Orchestrator $\rightarrow$ Sandboxed Docker Executor $\rightarrow$ CI/CD Referee $\rightarrow$ GitHub Pages Dashboard.
* **5.2 Model Context Protocol (MCP) Analysis:**
  * How MCP standardizes agent connections to local files, databases, and third-party tools.
  * Evaluating native MCP client support in VS Code vs. terminal CLI environments.
* **5.3 Cross-Platform Functional Translation Guide:**
  * Documenting how core capabilities translate across vendor tools:

| Capability | GitHub Copilot / VS Code | Anthropic Claude Code | Google Anti-Gravity |
| :--- | :--- | :--- | :--- |
| **Agent Creation** | Native slash command (`/create agent`) | Directory markdown config (`CLAUDE.md`) | Platform workspace configuration |
| **Tool / Skill Creation** | Native slash command (`/create skill`) | Manual shell / tool schema injection | API extension manifests |
| **Server-Side CI Execution** | GitHub Actions / Remote Agents | Headless CLI automation | Cloud sandbox integration |

---

## 6. Secure Agentic Development & Zero-Trust Governance
*(Priority: Must Have [Critical Path] | Target Completion: Weeks 8–10)*

* **6.1 Threat Modeling in Agentic Development:**
  * Direct and Indirect Prompt Injection (IPI) via poisoned backlog tickets or web context.
  * Unchecked terminal execution, container breakouts, and network exfiltration.
* **6.2 Credential & Identity Protection (OIDC vs. Static PATs):**
  * Enterprise risks of storing long-lived personal access tokens in agent scratch directories.
  * Demonstrating short-lived credential leasing and zero-token sandbox boundaries.
* **6.3 Ephemeral Sandboxing & Network Isolation:**
  * Technical mechanics of `network_mode: "none"` inside the evaluation container.
  * Preventing data exfiltration when agents process untrusted third-party code.
* **6.4 Automated Fail-Closed Auditing:**
  * Integrating TruffleHog (scanning verified/unverified secrets) to trigger immediate zero-score failures upon secret leakage.
  * *Demonstrated Attack & Mitigation Run:* [Walkthrough of simulated IPI canary leak intercepted by sandboxed isolation].

---

## 7. Developer Experience (DevEx) & Interaction Friction
*(Priority: Should Have | Target Completion: Weeks 8–10)*

* **7.1 Defining Great Agentic DevEx:**
  * Latency, predictability, transparency of agent reasoning, and non-intrusive diff presentations.
* **7.2 Cognitive Friction Index (Keystroke & Confirmation Overhead):**
  * Quantifying the number of clicks, terminal approvals, and interruptions required per task.
  * Measuring the trade-off between human safety checkpoints and autonomous developer velocity.
* **7.3 Context Window Management & Instruction Tuning:**
  * Effective scoping: workspace-level `.github/copilot-instructions.md` vs. granular repo maps.
  * Avoiding context dilution and hallucinated tool calls.

---

## 8. Cost Management & Resource Economics
*(Priority: Must Have | Target Completion: Weeks 9–11)*

* **8.1 Cost Dimensions in Agentic Workflows:**
  * Input/output tokens, multi-turn reasoning loops, and prompt cache hit rates.
* **8.2 Termination Controls & Loop Watchdogs:**
  * Empirical impact of turn caps (`MaxMessageTermination <= 5`) and token ceilings (`TokenUsageTermination <= 15000`).
  * Preventing runaway recursive agent loops in headless pipelines.
* **8.3 Model Tier Selection Economics:**
  * Cost comparison: High-tier reasoning models (Opus 3.5, GPT-4o) vs. lightweight execution models (GPT-4o-mini, Haiku).
  * Finding the optimal cost-per-successful-PR frontier for an organization with 10,000 developers.
* **8.4 Empirical Cost Telemetry Data:**
  * [Placeholder: LiteLLM token utilization logs and USD cost estimates per benchmark run].

---

## 9. Ethical Engineering, Provenance, and Accountability
*(Priority: Should Have | Target Completion: Weeks 7–8)*

* **9.1 Code Provenance & Intellectual Property:**
  * Attribution, copyleft contamination risks, and U.S. Copyright Office stance on AI-authored code.
* **9.2 Deskilling & Over-Reliance Risks:**
  * Mitigating developer blind spots where unvetted AI diffs are approved without comprehension.
* **9.3 The Team-Authored Ethical Framework:**
  * Mandatory developer disclosure standards (per USF CIS 4910 and industry norms).
  * Audit trails: Maintaining an immutable log of agent prompts, tool calls, and human approvals.

---

## 10. Future Horizons: The 2–5 Year Outlook
*(Priority: Could Have | Target Completion: Week 14)*

* **10.1 Near-Term Evolutions (2026–2028):**
  * Shift from general language models to multi-modal reasoning and domain-specialized scientific models.
  * Fully headless background agents autonomously managing dependency updates, vulnerability patches, and CI/CD triage.
* **10.2 Long-Term Vision (2028–2031):**
  * Multi-agent autonomous engineering swarms.
  * The transition of junior engineering roles from code authors to system directors, evaluators, and specification designers.

---

## Appendices

* **Appendix A:** Telemetry JSON Schema v2 Specification (`benchmark_run.schema.json`).
* **Appendix B:** Full Experimental Run Log Datasets (Task IDs, Prompt Versions, Token Counts, Latencies).
* **Appendix C:** Docker Sandbox & DevContainer Definition Files (`Dockerfile`, `devcontainer.json`).
* **Appendix D:** Video Walkthrough Links & Demo Artifact Index.