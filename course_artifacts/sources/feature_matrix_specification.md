# Agentic Developer Tool and Pipeline Feature Matrix Specification

**Project:** CIS 4910 Senior Project, Group 3  
**Version:** 0.2  
**Status:** Draft for team and sponsor review  
**Date:** October 9, 2026  
**Assessment method:** Documentation review only

## Purpose

This specification defines a feature matrix for comparing the documented capabilities of developer-facing agentic tools and composed development pipelines. It records what a tool supports, how that support is provided, its documented conditions and limitations, and the sources supporting each finding.

The intended audience includes developers, engineering teams, and decision-makers considering adoption. The initial matrix supports discussion with the sponsor. It does not assign an overall score, rank products, or measure how well they perform development tasks.

The existing AutoGen-based model evaluation prototype is a separate project track. This feature matrix does not execute tools or use prototype execution results to validate feature claims. A documentation-based assessment is a complete deliverable; it does not require subsequent live validation.

## Scope and terminology

### Assessment boundary

**In scope:** Reviewing official product documentation, reference manuals, security documentation, release notes, and documentation in official repositories. Published examples can explain a documented capability, but are evidence of a published claim rather than behavior observed by the team.

**Out of scope:** Installing or configuring tools for assessment; inspecting running environments; conducting live sessions, demonstrations, or feature tests; collecting team-generated screenshots, execution logs, or task results; benchmarking task success, duration, cost, or reliability; and testing security boundaries. These activities are not required deliverables or planned extensions of this matrix.

The initial comparison covers the Copilot baseline in VS Code and Copilot CLI. Define each as a documented capability profile, with its relevant operating modes and platform constraints. Spec Kit and other add-ons are excluded from the core comparison. A separate add-on component may be considered later, but is not needed to complete the core matrix.

### Definitions

- **Model:** The underlying language model used for reasoning and generation.
- **Agent:** A system that uses a model and tools to act toward a goal, observes results, and chooses subsequent actions.
- **Harness:** Software connecting a model to tools and managing execution, context, permissions, and sessions.
- **Pipeline:** A combination of a harness, model, instructions, workflow tools, execution environment, repository services, checks, and deployment integrations.
- **Feature availability:** Documented support for a capability and the requirements for enabling it within the assessed profile.
- **Effectiveness:** How reliably and appropriately a configuration performs a task using a capability. Effectiveness is outside this matrix's scope.
- **Enforced control:** A restriction described as implemented by software or an environment boundary. This classification records the documented mechanism, not an independently verified guarantee.
- **Instruction-based behavior:** A rule the agent is asked to follow through prompts, instructions, or a specification.

Autocomplete and ordinary coding chat may be included as baselines, but are not automatically agentic. Classify a system as agentic only when its documentation describes a tool-mediated action and feedback loop.

Documented availability does not establish effectiveness. For example, documented test execution does not show that an agent selects appropriate tests or fixes failures correctly. Documented approval or isolation mechanisms likewise do not establish complete security.

## Tool and pipeline categories

These categories organize the evaluation landscape. They are a practical taxonomy, not a ranking by market share. Categories overlap, and a product or profile may have multiple tags.

| ID | Category | Description | Illustrative example |
| --- | --- | --- | --- |
| T1 | Agents inside an editor or IDE | Operate alongside the developer in the coding environment, gathering context, editing files, and running checks. | GitHub Copilot in VS Code |
| T2 | Terminal or command-line agents | Act on a repository through files, shell commands, and development tools, with a terminal interface. | Claude Code |
| T3 | Background or cloud coding agents | Receive delegated tasks, work in a separate environment, and return changes for review. | GitHub Copilot cloud agent |
| T4 | Integrated application builders | Combine natural-language app creation with a managed workspace, previews, services, and deployment. | Replit |
| T5 | Specialized development agents | Focus on an activity such as code review, testing, failure investigation, or security fixes. | GitHub Copilot code review |
| T6 | Agent orchestration frameworks | Provide programming components for building agents and coordinating tools, roles, and interactions. | AutoGen AgentChat |
| T7 | Specification-driven workflow toolkits | Provide a structured process for requirements, planning, task decomposition, implementation, and verification using a coding agent. | GitHub Spec Kit |

Examples identify categories only; they do not establish support for matrix features. Frameworks and workflow toolkits are building blocks. Any later assessment must distinguish their documented mechanisms from capabilities supplied by a host tool or integration. T7 remains in the landscape taxonomy but is excluded from the initial core comparison.

## Unit of comparison

Each matrix column represents a specific documented capability profile, rather than a vendor name alone. Each row represents one feature from the catalog. A profile describes the product, modes, platform, and allowed components under review; it is not an installed or tested configuration.

For the initial comparison, use “Copilot baseline in VS Code” and “Copilot CLI,” defining the modes covered in each column. Exclude Spec Kit, user-authored skills, added MCP servers, and custom orchestration. Assess native support for instructions, skills, and integrations where documented, while recording that optional integrations are not enabled in the baseline profile. Support for a mechanism is distinct from including an add-on that uses it.

Record the following for each column:

| Field | Required information |
| --- | --- |
| Configuration ID | Stable identifier, such as C01; retained for compatibility with matrix records |
| Configuration name | Short label for the documented capability profile |
| Category tags | Applicable T1–T7 categories |
| Tool and harness | Product names and documented versions or release identifiers, if provided |
| Operating modes | Modes covered by the documentation review, including any mode-specific restrictions |
| Interface and execution location | Documented IDE, terminal, browser, local, remote, or cloud operation |
| Model support | Documented model compatibility or routing where relevant; record unknown details explicitly |
| Account and platform | Documented subscription, operating system, and organization-policy requirements |
| Included components | Native components included in the profile and explicit exclusions |
| Instructions and permissions | Documented mechanisms, defaults, optional settings, and relevant limits |
| Documentation coverage | Reviewed source set, source versions or update dates where available, and access dates |
| Assessment context | Assessment date and evaluator |

Do not require a task, repository revision, runtime settings, or a common model across profiles. No execution comparison is being conducted. If documentation is unversioned, identify it as such and record the access date rather than inventing a product version. Local tool execution does not imply local model processing.

## Initial feature catalog

The catalog retains 18 features across six areas. The final column specifies documentation to examine, not actions to perform. Execution, testing, and deployment in feature descriptions refer to capabilities of the assessed tool, not activities of the assessment team.

| ID | Area | Feature | Capability to assess | Documentation to examine |
| --- | --- | --- | --- | --- |
| F01 | Requirements and planning | Persistent project instructions | Save coding standards, security rules, and test commands for use across tasks. | Supported instruction formats, discovery rules, precedence, persistence, and scope. |
| F02 | Requirements and planning | Planning before implementation | Produce a developer-reviewable plan before changing code. | Planning modes, review steps, and documented transition from planning to implementation. Distinguish optional planning from a required approval gate. |
| F03 | Requirements and planning | Requirements traceability | Connect a requirement to implementation and verification evidence. | Explicit linking of requirements, tasks, changes, and checks. A plan or task list alone does not establish traceability. |
| F04 | Development capabilities | Codebase context gathering | Locate and inspect relevant existing code without requiring all context to be supplied manually. | Repository search, indexing, file inspection, context selection, and documented limits. |
| F05 | Development capabilities | Coordinated changes across files | Update related code, configuration, and tests together. | Multi-file editing support, relevant modes, and documented restrictions. |
| F06 | Development capabilities | Execution and feedback | Run builds or tests, inspect failures, and revise work based on results. | Command and test execution, access to results, and documented feedback or revision loops. Do not infer successful defect correction. |
| F07 | Security and control | Tool and permission restrictions | Limit commands, files, external services, or network destinations accessible to the agent. | Allow/deny controls and their command, filesystem, service, and network coverage. Distinguish approval prompts from access restrictions. |
| F08 | Security and control | Execution isolation | Run agent actions within an environment with enforced boundaries. | Documented sandbox mechanisms, defaults, filesystem/network boundaries, platform restrictions, and exceptions. A branch or Git worktree alone does not establish isolation. |
| F09 | Security and control | Secrets handling | Supply credentials through a supported mechanism without placing them in prompts, generated code, or committed files. | Credential delivery, storage, redaction, exposure boundaries, and documented limits. Product sign-in alone does not establish safe handling of application secrets. |
| F10 | Developer oversight | Approval checkpoints | Require developer approval before selected actions. | Actions requiring approval, defaults, configuration, bypasses, and mode-specific exceptions. |
| F11 | Developer oversight | Inspection and intervention | View progress, inspect proposed changes, redirect work, and stop the agent. | Progress and diff views, steering and cancellation controls, and limits on interrupting ongoing actions. Record each subcapability separately. |
| F12 | Developer oversight | Change recovery | Discard or revert code changes with clear limits on recovery coverage. | Checkpoints, undo, restore, or Git-based recovery; coverage of files, shell effects, external actions, and deployed resources. |
| F13 | Customization and integration | Reusable skills and task workflows | Package, share, version, and invoke recurring procedures. | Native formats, discovery and invocation rules, sharing mechanisms, and documented requirements. Assess the mechanism without adding a skill to the profile. |
| F14 | Customization and integration | External tool integration | Connect to issue trackers, documentation, databases, or other systems through MCP or another interface. | Supported interfaces or protocols, authentication, configuration, permission controls, and limits. Assess native integration support without connecting a service. |
| F15 | Customization and integration | Repository and CI/CD integration | Work with branches, pull requests, automated checks, and deployment workflows. | Explicit support for each stage. Branch or pull-request support alone does not establish a complete CI/CD or deployment pipeline. |
| F16 | Evidence and cost | Action logs and audit trail | Inspect and export tool calls, commands, results, and changes associated with a task. | Recorded events, run association, export formats, retention, and integrity guarantees where documented. Distinguish chat history from an audit trail. |
| F17 | Evidence and cost | Usage and cost visibility | Obtain task-level token usage, charges, or another clearly defined usage measure. | Units, granularity, reporting and estimation methods. Distinguish context usage, tokens, request allowances, and monetary charges. |
| F18 | Evidence and cost | Execution limits | Set time, iteration, or spending limits to contain runaway work. | Supported limits, defaults, scope, overrides, and documented enforcement. Distinguish hard limits from estimates, warnings, and instruction-based requests. |

## Cell status labels

Each feature–profile cell contains one primary status, a concise explanation, and source references or a reason the documentation does not establish support.

| Status | Meaning |
| --- | --- |
| Built in | Official documentation establishes native support within the profile. A native feature may still require an optional setting; record activation separately. |
| Configuration or extension required | Official documentation establishes support through an additional integration or separately assembled configuration outside the native capability assessed. Identify the dependency and whether it is excluded from the profile. |
| Custom implementation required | Documentation explicitly describes implementation work needed to supply the capability. Identify the code and maintenance responsibility. Do not infer this status from a documentation gap. |
| Unavailable | Official documentation explicitly establishes that the capability is unsupported within the assessed profile. |
| Not established from documentation | Reviewed sources are silent, ambiguous, conflicting, or insufficient to establish support or absence. |

These labels describe delivery mechanisms, not quality rankings. “Built in” does not mean enabled by default, more effective, or safer. Record activation separately as default, optional, policy-dependent, or not established. Use “Not established from documentation” for unknowns; blank cells are not permitted. This replaces the earlier “Not verified” label so that uncertainty does not imply a pending live test.

Broad features may have partial support. Preserve one primary status while identifying supported, explicitly unsupported, and unestablished subcapabilities in the notes. Do not present partial support as complete coverage. For specialized tools, explain applicability without assigning an unsupported performance penalty.

## Evidence and assessment records

For every cell, retain:

1. Feature ID and configuration ID.
2. Primary status, supported scope, and unsupported or unestablished subcapabilities.
3. Required setup, activation state, integrations, tier, platform, and policy constraints.
4. Stable evidence references to official documentation supporting the finding, or a documented gap reason.
5. Evidence basis: documented support, documented absence, documentation gap, or documentation conflict.
6. Documented control mechanism where relevant: enforced, instruction-based, mixed, or not established.
7. Assessment date, evaluator, and material limitations, including preview or deprecated status.

Maintain an evidence index with identifiers such as E01. Each entry includes the publisher, page title, canonical URL, relevant heading or section, access date, and source version or update date when available. Retain short claim summaries that another group member can review. An archived copy or revision link may be included when available, but an automated archival system is not required.

Use sources specific to the product, mode, and platform assessed. Do not transfer a capability claim between IDE, CLI, cloud, or review surfaces without supporting documentation. Distinguish explicit claims from assessor interpretation. If sources conflict, record both and explain the unresolved version or scope issue; do not resolve it through live testing. Missing documentation is not evidence of absence.

### Reusable cell record

```yaml
feature_id: F07
configuration_id: C01
status: Not established from documentation
supported_scope: Not established
unsupported_scope: []
unestablished_scope: [Command, filesystem, service, and network restrictions]
required_setup: Not established
activation_state: Not established
evidence_basis: documentation_gap
evidence_refs: []
gap_reason: Assessment pending; replace with the reviewed scope and unresolved question
control_mechanism: Not established
constraints: []
limitations: Documentation-only assessment; runtime behavior is not evaluated
evaluator: Unassigned
assessment_date: null
```

## Initial review workflow

1. Define the two core profiles and their included modes, components, and exclusions.
2. Create a column per profile and include all 18 feature rows.
3. Initialize cells as “Not established from documentation.”
4. Review official documentation and record source coverage and access dates.
5. Extract feature claims, delivery mechanisms, defaults, requirements, and limitations; identify gaps and conflicts.
6. Assign statuses and populate the evidence index and cell notes.
7. Have another group member review source-to-claim alignment and consistent use of statuses.
8. Present the matrix, documented differences, and unresolved documentation questions to the sponsor.

The sponsor-facing draft is complete when profiles are identified, all 18 features have a status, findings of support or absence have source references, and uncertain cells explain the documentation gap or conflict. Uncertain cells are acceptable completed findings. No live demonstration or feature test is a completion criterion. The presentation must describe documented capabilities and avoid claims of measured effectiveness or verified security.

## Scoring and future extensions

Version 0.2 does not define feature weights, aggregate scores, product rankings, or comparative effectiveness claims. Any later weighting must remain explicit about documentation coverage, feature applicability, and uncertainty; unknowns must not silently become zero capability scores.

Potential extensions within this scope include additional tool profiles, finer subdivisions of broad features, applicability filters, and sponsor-defined priorities. Preserve feature identifiers across revisions.

A separate, optional add-on component may later describe Spec Kit, reusable skills, or additional integrations. It should identify the host requirements and capabilities attributable to the add-on, with documentation references, while leaving the core tool comparison independently complete. Add-on assessments use the same documentation-only method. Live sessions, benchmarks, and effectiveness trials are outside this framework's scope rather than deferred matrix work.

## Questions for team and sponsor review

- Are the Copilot baseline and CLI profiles clearly defined enough for a useful first comparison?
- Which documented capabilities are essential to the sponsor's adoption decision?
- Which broad features need subcapability detail to avoid misleading summaries?
- How should preview features and differences in documentation versions be presented?
- Are the uncertainty labels and source references sufficiently clear for review?
- Which additional tool categories should follow once the core matrix is solid?
- Is a separate add-on component useful later, without expanding the current deliverable?

## Reference documentation

These official sources illustrate the tool categories and terminology. They are starting points, not completed feature assessments. Each matrix finding requires sources specific to its assessed profile and documentation coverage.

- [Build with AI in VS Code](https://code.visualstudio.com/docs/agents/overview)
- [Claude Code repository](https://github.com/anthropics/claude-code)
- [GitHub Copilot on GitHub.com](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github)
- [Replit Agent documentation](https://docs.replit.com/features/agent/overview)
- [GitHub Copilot code review](https://docs.github.com/copilot/concepts/agents/code-review)
- [AutoGen AgentChat documentation](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/)
- [GitHub Spec Kit documentation](https://github.github.com/spec-kit/)

## Revision note

Version 0.2 replaces inspection and demonstration requirements with documentation review; removes runtime evidence and future effectiveness trials; separates the AutoGen evaluation track; and defers add-ons to an optional separate component. The 18 feature identifiers and seven landscape categories are retained.

This draft was developed with assistance from OpenAI ChatGPT. The team should review its definitions and findings and document AI assistance in submitted course materials as required by the course syllabus.
