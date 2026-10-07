# Agentic Developer Tool and Pipeline Feature Matrix Specification

**Project:** CIS 4910 Senior Project, Group 3  
**Version:** 0.1  
**Status:** Draft for team and sponsor review  
**Date:** October 6, 2026

## Purpose

This specification defines an initial feature matrix for evaluating developer-facing agentic tools and composed development pipelines. The matrix will describe the capabilities available to a developer, how those capabilities are provided, and the evidence supporting each finding.

The intended audience includes developers, engineering teams, and decision-makers considering adoption. This first version provides a consistent basis for comparison and discussion with the sponsor. It does not assign an overall score or rank products.

The existing AutoGen-based evaluation prototype can contribute execution and evidence collection capabilities. The framework must also accommodate other harnesses, workflows, and integrations without assuming that every evaluated system uses AutoGen.

## Scope and terminology

- **Model:** The underlying language model used for reasoning and generation.
- **Agent:** A system that uses a model and tools to act toward a goal, observes the results, and chooses subsequent actions.
- **Harness:** The software that connects the model to tools and manages execution, context, permissions, and sessions.
- **Pipeline:** A configured combination of a harness, model, instructions, workflow tools, execution environment, repository services, checks, and deployment integrations.
- **Feature availability:** Whether a configuration provides a capability, and what is required to enable it.
- **Effectiveness:** How reliably and appropriately the configuration performs a task using that capability.
- **Enforced control:** A restriction implemented by software or an environment boundary.
- **Instruction-based behavior:** A rule the agent is asked to follow through prompts, instructions, or a specification.

Autocomplete and ordinary coding chat may be included as baselines, but they are not automatically agentic. A system must perform a tool-mediated action and feedback loop to qualify as an agent under this specification.

Feature availability and effectiveness must be recorded separately. For example, the ability to execute tests does not establish that the agent selects appropriate tests or fixes failures correctly.

## Tool and pipeline categories

The following categories organize the evaluation landscape. They are a practical taxonomy, not a ranking by market share. Categories overlap, and a product or configuration may have multiple tags.

| ID | Category | Description | Illustrative example |
| --- | --- | --- | --- |
| T1 | Agents inside an editor or IDE | Operate alongside the developer in the coding environment, gathering context, editing files, and running checks. | GitHub Copilot in VS Code |
| T2 | Terminal or command-line agents | Act on a repository through files, shell commands, and development tools, with a terminal interface. | Claude Code |
| T3 | Background or cloud coding agents | Receive delegated tasks, work in a separate environment, and return changes for review. | GitHub Copilot cloud agent |
| T4 | Integrated application builders | Combine natural-language app creation with a managed workspace, previews, services, and deployment. | Replit |
| T5 | Specialized development agents | Focus on a particular activity, such as code review, testing, failure investigation, or security fixes. | GitHub Copilot code review |
| T6 | Agent orchestration frameworks | Provide programming components for building agents and coordinating tools, roles, and interactions. | AutoGen AgentChat |
| T7 | Specification-driven workflow toolkits | Provide a structured process for requirements, planning, task decomposition, implementation, and verification using a coding agent. | GitHub Spec Kit |

Examples identify categories only. Their inclusion does not establish support for any feature in the matrix. An orchestration framework and a workflow toolkit are building blocks; they should be evaluated within a usable configuration when compared with complete development tools.

## Unit of comparison

Each matrix column must represent a specific configuration, rather than a vendor or product name alone. Each row must represent one feature from the catalog below.

For example, “VS Code + Copilot agent + Spec Kit + repository instructions + CI tests” is a different configuration from “VS Code + Copilot agent with default settings.”

Record the following for each column:

| Field | Required information |
| --- | --- |
| Configuration ID | A stable identifier, such as C01 |
| Configuration name | A short, descriptive label |
| Category tags | Applicable T1–T7 categories |
| Tool and harness | Product names and versions or release identifiers |
| Operating mode | Interactive, background, unattended, or another documented mode |
| Interface and execution location | IDE, terminal, browser, local host, remote host, or cloud environment |
| Model | Model identifier and relevant settings; record automatic routing if used |
| Account and platform | Subscription tier, operating system, and relevant organization policies |
| Workflow and integrations | Specification toolkit, skills, MCP servers, extensions, repository, and CI/CD components |
| Instructions and permissions | References to versioned instructions and relevant control settings |
| Evaluation context | Evaluation date, evaluator, repository revision, and task or demonstration identifier |

Record unknown or unavailable information explicitly. Do not infer model details or hidden behavior. Local tool execution does not imply local model processing.

## Initial feature catalog

The catalog contains 18 features across six areas. The inspection suggestions are starting points for confirming availability, not complete effectiveness or security tests.

| ID | Area | Feature | Capability to evaluate | Initial inspection or demonstration |
| --- | --- | --- | --- | --- |
| F01 | Requirements and planning | Persistent project instructions | Save coding standards, security rules, and test commands for use across tasks. | Inspect the supported instruction mechanism and demonstrate its use in a new task. |
| F02 | Requirements and planning | Planning before implementation | Produce a developer-reviewable plan before changing code. | Request a plan and observe whether implementation can wait for review. |
| F03 | Requirements and planning | Requirements traceability | Connect a requirement to implementation and verification evidence. | Follow one identified requirement through tasks, changes, and checks. |
| F04 | Development capabilities | Codebase context gathering | Locate and inspect relevant existing code without requiring all context to be supplied manually. | Give a repository-specific task and record the files or searches used. |
| F05 | Development capabilities | Coordinated changes across files | Update related code, configuration, and tests together. | Inspect a change that spans more than one relevant file. |
| F06 | Development capabilities | Execution and feedback | Run builds or tests, inspect failures, and revise work based on the results. | Introduce a controlled failure and observe the execution and revision loop. |
| F07 | Security and control | Tool and permission restrictions | Limit commands, files, external services, or network destinations accessible to the agent. | Inspect supported permission controls and safely demonstrate one denied action. Record which boundaries are actually covered. |
| F08 | Security and control | Execution isolation | Run agent actions within an environment with enforced boundaries. | Inspect the execution environment and verify a selected filesystem or network restriction. A separate branch or Git worktree alone is not a security boundary. |
| F09 | Security and control | Secrets handling | Supply credentials through a supported mechanism without placing them in prompts, generated code, or committed files. | Use a dummy credential and inspect the documented delivery mechanism and relevant outputs. Record unobservable paths as limitations. |
| F10 | Developer oversight | Approval checkpoints | Require developer approval before selected actions. | Configure a checkpoint and observe whether the action waits for approval. Record the actions covered. |
| F11 | Developer oversight | Inspection and intervention | View progress, inspect proposed changes, redirect work, and stop the agent. | Demonstrate progress inspection, redirection, and stopping a controlled task. Record which controls are available. |
| F12 | Developer oversight | Change recovery | Discard or revert code changes with clear limits on what recovery covers. | Revert a controlled change and verify the repository state. Record limits for external actions and deployed resources. |
| F13 | Customization and integration | Reusable skills and task workflows | Package, share, version, and invoke recurring procedures. | Inspect a reusable procedure and invoke it in a separate task or session. |
| F14 | Customization and integration | External tool integration | Connect to issue trackers, documentation, databases, or other systems through MCP or another interface. | Inspect a configured integration and demonstrate a tool call. Record access and authentication requirements. |
| F15 | Customization and integration | Repository and CI/CD integration | Work with branches, pull requests, automated checks, and deployment workflows. | Trace one change through the supported repository and CI/CD steps. Record each supported stage separately in the notes. |
| F16 | Evidence and cost | Action logs and audit trail | Inspect and export tool calls, commands, results, and changes associated with a task. | Capture a task record and check its contents, exportability, and association with the run. |
| F17 | Evidence and cost | Usage and cost visibility | Obtain task-level token usage, charges, or another clearly defined usage measure. | Retrieve a usage record and document its unit, granularity, and any estimation method. |
| F18 | Evidence and cost | Execution limits | Set time, iteration, or spending limits to contain runaway work. | Configure a supported limit and observe its behavior in a bounded task. Record the limits supported and how they are enforced. |

## Cell status labels

Each feature–configuration cell must contain one primary status, a concise explanation, and an evidence reference or a reason evidence is missing.

| Status | Meaning |
| --- | --- |
| Built in | The evaluated configuration provides the capability directly. |
| Configuration or extension required | The capability requires supported settings or an added integration. |
| Custom implementation required | The team must write and maintain code to provide the capability. |
| Unavailable | The capability has been confirmed absent within the evaluated scope. |
| Not verified | Support has not been established. |

These labels describe delivery mechanisms, not numerical quality rankings. “Built in” does not automatically mean safer or more effective than a custom implementation. Blank cells are not permitted; use “Not verified” for unknowns.

If a feature only partially applies to a specialized tool, explain its applicability in the notes. Do not silently interpret a narrow tool's intended scope as poor performance or assign an unsupported overall penalty.

## Evidence and assessment records

For every assessed cell, retain:

1. Feature ID and configuration ID.
2. Primary status and any supported or unsupported subcapabilities.
3. Required setup, integrations, account tier, and platform constraints.
4. Evidence reference: documentation section, configuration file, screenshot, log, recorded demonstration, or repository artifact.
5. Evidence basis: documented support, observed demonstration, or tested behavior. More than one may apply.
6. Control mechanism where relevant: enforced, instruction-based, mixed, or not established.
7. Assessment date, evaluator, and material limitations.

Documentation claims must be distinguishable from observed behavior. A successful demonstration establishes behavior in the recorded conditions; it does not establish universal reliability or complete security.

Use stable evidence identifiers, such as E01, and maintain an evidence index linking each identifier to its source or artifact. Evidence should be sufficient for another group member to review the finding. Use dummy credentials for secret-handling demonstrations and keep real secrets out of evidence artifacts.

### Reusable cell record

```yaml
feature_id: F07
configuration_id: C01
status: Not verified
supported_scope: Not established
required_setup: Not established
evidence_basis: []
evidence_refs: []
control_mechanism: Not established
constraints: []
limitations: Assessment pending
evaluator: Unassigned
assessment_date: null
```

## Initial review workflow

1. Agree on the configurations to compare and record their metadata.
2. Create one column per configuration and include all 18 feature rows.
3. Initialize unassessed cells as “Not verified.”
4. Review official documentation and inspect the configured environment.
5. Run small, controlled demonstrations for selected features and collect evidence.
6. Record statuses, mechanisms, constraints, and limitations.
7. Have another group member review findings and resolve inconsistent interpretations.
8. Present the matrix and open questions to the sponsor.

The first sponsor-facing draft is ready when the configurations are clearly identified, all features have a status, and assessed findings have evidence references. Unverified cells are acceptable when explicitly marked. The presentation must not imply that availability findings are effectiveness results.

## Scoring and future extensions

Version 0.1 does not define feature weights, aggregate scores, product rankings, or claims of comparative effectiveness. These require agreement on evaluation objectives, applicability, and evidence standards.

Later versions may add:

- Effectiveness scenarios with explicit acceptance criteria and repeated trials.
- Separate measurements of task success, developer intervention, duration, cost, and security behavior.
- A controlled comparison of default configurations and configurations augmented with specifications or reusable skills.
- Weighting profiles for different adoption priorities, with visible category breakdowns.
- Additional feature rows or finer subdivisions of broad capabilities.

For example, F06 establishes whether a system can execute tests and respond to failures. A subsequent effectiveness scenario could measure whether it fixes a deliberately introduced defect without weakening the tests.

Preserve feature identifiers across revisions. New tools should add configurations; new criteria should add or refine features without changing the basic assessment structure.

## Questions for team and sponsor review

- Which configurations and categories should be included in the initial comparison?
- Which features are essential to the sponsor's adoption decision?
- Should default and augmented configurations be separate comparison columns?
- What evidence is sufficient to confirm availability for each feature?
- How should specialized tools be compared with broader development pipelines?
- What comparisons remain meaningful when the same model is not available across harnesses?
- Which effectiveness scenarios should follow the availability matrix?

## Reference documentation

These official sources illustrate the tool categories and terminology. Feature assessments must use documentation and observations specific to the evaluated version and configuration.

- [Build with AI in VS Code](https://code.visualstudio.com/docs/agents/overview)
- [Claude Code repository](https://github.com/anthropics/claude-code)
- [GitHub Copilot on GitHub.com](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github)
- [Replit Agent documentation](https://docs.replit.com/features/agent/overview)
- [GitHub Copilot code review](https://docs.github.com/copilot/concepts/agents/code-review)
- [AutoGen AgentChat documentation](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/)
- [GitHub Spec Kit documentation](https://github.github.com/spec-kit/)

This draft was developed with assistance from OpenAI ChatGPT. The team should review its definitions and findings and document AI assistance in submitted course materials as required by the course syllabus.
