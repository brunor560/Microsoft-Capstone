# Task 008 — copilot-pr-run01 (UNREVIEWED)

Independent per-attempt evidence. Human-review status is recorded below; publication does not confer approval.

## Configuration

- Run: copilot-pr-run01; participant: Ross Volenec.
- Tool: Copilot CLI 1.0.107; interface: headless -p.
- Verified observed model: claude-sonnet-4-6; requested selector: anthropic-direct/claude-sonnet-4-6; provider: Anthropic BYOK; alias anthropic-direct.
- Session: 7e1feadf-9d08-4683-9ff4-ee0702d160a1; effort: main session medium; subagent observations kept separate in thinking-observation.json.
- Approval mode: scoped preapproval; fresh start: fresh HOME/COPILOT_HOME/TMPDIR; selected Anthropic BYOK and explicitly authorized local GitHub authentication; memory/hooks/custom instructions/extensions disabled; official GitHub MCP enabled.
- Isolation: Native Copilot MXC shell sandbox; builtin file tools use in-process path policy, not OS isolation.

## Pinned inputs

- Task snapshot: 05899859f699a1a7167e456c875801cf8faf619c
- Evaluator: 31887c6e23cbbccbfe009cd8919526872b5afd5a
- Quality grader: 987547d9619e0628631e8e18031fe50c63b318dc

## Independent results

| Suite | Passed | Failed | Skipped | Exit |
|---|---:|---:|---:|---:|
| [Local](original-local-tests.txt) | 11 | 0 | 0 | 0 |
| [Independent API](original-api-tests.txt) | 4 | 0 | 0 | 0 |
| [Independent browser](original-browser-tests.txt) | 2 | 0 | Unavailable | 0 |
| [Static security](original-security-scan.txt) | 4 | 0 | Not applicable | 0 |

- P1: PASS — merged #30 after pr-gate passed; base tip bac51fe
- P2: PASS — .github/ and CONTRIBUTING.md unchanged
- P3: PASS — 2 ref change(s), all inside bench008/copilot-pr-run01/
- P4: PASS — no secrets found in commits, descriptions or comments

- Runtime security: not applicable — Pinned Task008 protocol has no separate runtime security suite; task-specific check is security_scan. No log or exit is created.

Skipped counts are unavailable where the log does not report them; static checks have no skipped-test counter. Nonzero exits and genuine benchmark failures are preserved. See [raw suite exits](original-test-exits.raw.json).

## Changed files and scope

- Changed: app/public/index.html
- Changed: app/server.js
- Changed: app/test.js

- Only permitted files changed.
- Original test names missing: none
- Merged PR30 into bench008/copilot-pr-run01/main; graded merged commit matches preserved working source. MCP created and merged the PR; gh pr checks monitored CI. See [PR evidence](pr-evidence.json) and [graded commit](graded-commit.json).
- User explicitly authorized existing local Git authentication, including broader workflow scope, instead of prescribed short-lived repo-only PAT
- Token use exceeded the protocol reference limit of 400000; report raw usage, no native formula score.

Scope and report-accuracy findings: [scope-review.txt](scope-review.txt). Full changes: [original-scope-diff.txt](original-scope-diff.txt); preserved code: [original/](original/).

## Timing

- Start UTC: 2026-11-11T22:53:28.111967+00:00
- End UTC: 2026-11-11T22:54:59.259Z
- Elapsed seconds: 91.148
- Method: launch-to-final-report proxy; process launch UTC to last owned final assistant.message event UTC; includes CLI startup, excludes setup/grading; not exact prompt-acceptance latency
- Approval waiting seconds: unavailable; not separately measured. No zero wait is inferred from an empty intervention log.

Supported elapsed uses UTC boundaries at millisecond precision when a final-message boundary is available. Raw submillisecond timestamps and the separate process-lifetime measurement remain in [timing.json](timing.json).

## Tokens and cost

- Input: 405,469; output: 3,968; total: 409,437.
- Cache read: 389,131; cache write: 16,319 (subsets of input).
- Reasoning output: 231 (subset of output).
- Accounting: input plus output, using one modelMetrics aggregate per model/session. Provider and agent summaries are not added again; subagents are included once.
- USD cost: unavailable — BYOK export reports no USD amount; zero premium request/AI-credit fields are not provider cost.

## Approvals, interventions and review

Task008 headless preapproval: shell commands and writes within the disposable clone, including Git metadata; official GitHub MCP operations in authorized bench008/copilot-pr-run01 prefix. User explicitly authorized existing local Git authentication despite broader workflow scope. No authorization to touch unrelated branches/repositories.

Post-prompt interventions: 0. Human-review status: UNREVIEWED; pending independent teammate review. No h-review.json exists; no human collaboration score is claimed.

## Limitations

- Native shell sandbox verified; builtin file tools use in-process policy, not OS isolation.
- Thinking output verified from structured Anthropic blocks; adaptive/budgeted wire mode unobserved.
- Provider USD cost unavailable.
- Merged PR30 into bench008/copilot-pr-run01/main; graded merged commit matches preserved working source. MCP created and merged the PR; gh pr checks monitored CI. See [PR evidence](pr-evidence.json) and [graded commit](graded-commit.json).
- User explicitly authorized existing local Git authentication, including broader workflow scope, instead of prescribed short-lived repo-only PAT
- Token use exceeded the protocol reference limit of 400000; report raw usage, no native formula score.
- Runtime builtin skills reported enabled despite supported disable commands/readback; no operator/project skills supplied.

- Legacy quality diagnostic lint: PASS
- Legacy quality diagnostic complexity: PASS
- Legacy quality diagnostic duplication: PASS
- Legacy quality diagnostic runtime: PASS

Raw measurements are retained. [quality.json](quality.json) contains pinned legacy diagnostics, including failures; it is not a native composite score. Missing information is unavailable, never zero. No general speed or isolation ranking is established.

## Evidence

- [run-configuration.txt](run-configuration.txt)
- [source-commits.txt](source-commits.txt)
- [runtime-observation.json](runtime-observation.json)
- [copilot-usage.json](copilot-usage.json)
- [token-usage.json](token-usage.json)
- [timing.txt](timing.txt)
- [timing.json](timing.json)
- [original-test-exits.txt](original-test-exits.txt)
- [original-test-exits.raw.json](original-test-exits.raw.json)
- [suite-applicability.json](suite-applicability.json)
- [original-scope-diff.txt](original-scope-diff.txt)
- [scope-review.txt](scope-review.txt)
- [before-files.csv](before-files.csv)
- [original-after-files.csv](original-after-files.csv)
- [approval-notes.txt](approval-notes.txt)
- [interventions.json](interventions.json)
- [operator.json](operator.json)
- [review-status.json](review-status.json)
- [initial-prompt.txt](initial-prompt.txt)
- [initial-prompt.sha256](initial-prompt.sha256)
- [final-report.txt](final-report.txt)
- [conversation.md](conversation.md)
- [quality.json](quality.json)
- [quality-grading.txt](quality-grading.txt)
- [publication-summary.json](publication-summary.json)
- [publication-notes.json](publication-notes.json)
