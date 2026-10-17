# Codex task 004 bug-fix benchmark

Joseph B. ran GPT-6.1 Sol (`gpt-6.1-sol`) with light/`low` reasoning through headless Codex CLI `0.163.0-alpha.10.2` on October 17, 2026. The fresh attempt completed in 57.874 seconds. No corrective coding prompt was required.

| Suite | Passed | Failed | Exit |
|---|---:|---:|---:|
| Baseline local tests | 9 | 0 | 0 |
| Agent and independent local tests | 15 | 0 | 0 |
| Independent API tests, including subtests | 24 | 0 | 0 |
| Independent browser tests | 4 | 0 | 0 |

B1, B2, B3 and B4 were fully fixed under the published evaluator. Counts are separate suites, not distinct requirements.

## Sources and protocol limitations

Start snapshot and evaluator were pinned to published commit `1e690f91a11dd1b37c796345a511d6791476efbc` from `origin/benchmark-protocol-v3-bugfix`. Its app tree `298ef7c3346517369fbefb2e8802f7e416ed953b` exactly matches app commit `4e258a96855d98edd10247f68c0b8265e53a8921`. Only app/ and pipeline/tasks/004-fix-update-validation.md were exported into the coding workspace.

The requested benchmark-start-v3-bugfix branch was not published. After being told this, Joseph directed following the consistent existing pattern. The protocol commit was therefore used for both exports; explicit team-wide agreement on this substitute was not established. Grader SHA-256 hashes were saved, but cross-participant comparison was not verified. Application results are verified; strict shared-protocol comparability remains conditional on those confirmations.

The setup assistant inspected the existing title-edit package and an earlier unofficial task-004 trial README to follow established evidence conventions. It did not pass trial code, grader source, reference source, acceptance text, earlier conversation or coding hints to the measured agent. Joseph's previous knowledge of the task, graders or reference is unknown. This run is separate from the earlier codex-bugfix-trial01.

## Fresh session and environment

Windows; Node v24.22.0; npm 11.19.1; Playwright 1.64.1 with managed Chromium. Approval policy never, workspace-write sandbox, Windows backend elevated. All inherited CODEX_* variables were removed from the child environment. The real default Codex home was retained for authentication and Windows sandbox setup.

The CLI started a new ephemeral session with user config and rules ignored, memories and external memory import disabled, and project_doc_max_bytes=0. Global AGENTS.md exists; its contents are retained outside this repository in codex-bugfix-run01-evidence/global-AGENTS-disabled.txt. Apps, plugins, hooks and multi-agent tools were disabled, and host skill discovery skipped. No MCP servers/connectors were configured by the launch. Unexpected auto-loaded capabilities were not independently inventoried. Exact flags and removed environment variable names are included; no environment values or credentials are published.

## Timing, usage and assistance

A PowerShell Stopwatch started immediately before sending the exact prompt and stopped at CLI process return: 57.8742672 seconds. Final process shutdown is included; exact prompt-to-final-event latency was not separately measured. There was no human approval waiting and no corrective coding assistance. Setup and grading time are excluded.

The final turn reported 137,466 input tokens, including 121,600 cached input tokens, and 3,432 output tokens. The raw record additionally reports 198 reasoning output tokens. Cached input is part of input, not an additional total. Monetary cost is unavailable.

## Scope and reporting

Only app/server.js, app/test.js and app/public/index.html changed. All nine baseline tests were preserved after line-ending normalization. Five API tests and one simulated DOM test were appended. Package files, task file, dependencies, DELETE handler and existing title-validation condition were preserved; no extra project directories were added.

The final report correctly identified Boolean("false") coercion and invisible HTTP/network toggle failures, and reported additional ID/body validation. Its 15-test count was independently confirmed. It accurately disclosed using a simulated DOM instead of a real browser. The independent Playwright checks ran after original output was preserved. No grader/reference/other-run access appears in recorded shell commands; this is not a complete filesystem audit.

## Evidence

The package follows the previous compact benchmark layout: original source snapshots, manifests and scope review, source commit IDs and grader hashes, run configuration/launch arguments, exact prompt and final report, one JSONL transcript, timing and usage, suite logs/exit codes, successful browser report and screenshots. Full setup evidence, grader source, reference and installed dependencies remain outside the repository.

Results are prepared on results/codex-bugfix-run01. No commit or push has been performed. One run on one task does not establish a general tool winner.
