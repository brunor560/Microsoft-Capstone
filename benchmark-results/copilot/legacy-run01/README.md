# Task 007 — copilot-legacy-run01 (UNREVIEWED)

Independent per-attempt evidence. Human-review status is recorded below; publication does not confer approval.

## Configuration

- Run: copilot-legacy-run01; participant: Ross Volenec.
- Tool: Copilot CLI 1.0.107; interface: headless -p.
- Verified observed model: claude-sonnet-4-6; requested selector: anthropic-direct/claude-sonnet-4-6; provider: Anthropic BYOK; alias anthropic-direct.
- Session: 8c1d65e5-f739-4cab-b9f2-b7f89118e6e9; effort: main session medium; subagent observations kept separate in thinking-observation.json.
- Approval mode: scoped preapproval; fresh start: fresh HOME/COPILOT_HOME/TMPDIR; selected BYOK provider only; memory/hooks/custom instructions/MCP/extensions disabled; supported controls read back.
- Isolation: Native Copilot MXC shell sandbox; builtin file tools use in-process path policy, not OS isolation.

## Pinned inputs

- Task snapshot: f03269bc81a1501b363f60624975bd9036c10804
- Evaluator: f03269bc81a1501b363f60624975bd9036c10804
- Quality grader: 987547d9619e0628631e8e18031fe50c63b318dc

## Independent results

| Suite | Passed | Failed | Skipped | Exit |
|---|---:|---:|---:|---:|
| [Local](original-local-tests.txt) | 22 | 0 | 0 | 0 |
| [Independent API](original-api-tests.txt) | 7 | 0 | 0 | 0 |
| [Independent browser](original-browser-tests.txt) | 1 | 1 | Unavailable | 1 |
| [Static security](original-security-scan.txt) | 4 | 0 | Not applicable | 0 |

- L1: PASS — header, CRLF line endings, empty and missing list
- L2: PASS — row order, id padding and DONE column
- L3: PASS — cutting, spreadsheet guard, and unchanged output for titles that need no quoting
- L4: PASS — tests catch the bug (with original module: 5 failed, 17 passed; with reference fix: 0 failed, 22 passed)

- Runtime security: not applicable — Pinned Task007 protocol has no separate runtime security suite; task-specific check is security_scan. No log or exit is created.

Skipped counts are unavailable where the log does not report them; static checks have no skipped-test counter. Nonzero exits and genuine benchmark failures are preserved. See [raw suite exits](original-test-exits.raw.json).

## Changed files and scope

- Changed: app/legacy/billing-export.js
- Changed: app/test.js

- Only permitted files changed.
- Original test names missing: none
- Local/API/contract checks passed. Browser UI-01 was canceled at download.path before its content assertion; separate diagnostic reproduced it. Browser functionality is partially unverified due to this infrastructure limitation.
- The baseline browser run had the same canceled-download error; it was initially mistaken for the expected missing-feature failure by counts. Preserve this preparation limitation.

Scope and report-accuracy findings: [scope-review.txt](scope-review.txt). Full changes: [original-scope-diff.txt](original-scope-diff.txt); preserved code: [original/](original/).

## Timing

- Start UTC: 2026-11-11T16:31:15.264748+00:00
- End UTC: 2026-11-11T16:32:44.184Z
- Elapsed seconds: 88.92
- Method: launch-to-final-report proxy; process launch UTC to last owned final assistant.message event UTC; includes CLI startup, excludes setup/grading; not exact prompt-acceptance latency
- Approval waiting seconds: unavailable; not separately measured. No zero wait is inferred from an empty intervention log.

Supported elapsed uses UTC boundaries at millisecond precision when a final-message boundary is available. Raw submillisecond timestamps and the separate process-lifetime measurement remain in [timing.json](timing.json).

## Tokens and cost

- Input: 304,893; output: 5,397; total: 310,290.
- Cache read: 277,315; cache write: 27,562 (subsets of input).
- Reasoning output: 154 (subset of output).
- Accounting: input plus output, using one modelMetrics aggregate per model/session. Provider and agent summaries are not added again; subagents are included once.
- USD cost: unavailable — BYOK export reports no USD amount; zero premium request/AI-credit fields are not provider cost.

## Approvals, interventions and review

Headless scoped-preapproval: reads in snapshot; writes only named allowed files; node commands and npm test. No model corrections or additional task instructions.

Post-prompt interventions: 0. Human-review status: UNREVIEWED; pending independent teammate review. No h-review.json exists; no human collaboration score is claimed.

## Limitations

- Native shell sandbox verified; builtin file tools use in-process policy, not OS isolation.
- Thinking output verified from structured Anthropic blocks; adaptive/budgeted wire mode unobserved.
- Provider USD cost unavailable.
- Local/API/contract checks passed. Browser UI-01 was canceled at download.path before its content assertion; separate diagnostic reproduced it. Browser functionality is partially unverified due to this infrastructure limitation.
- The baseline browser run had the same canceled-download error; it was initially mistaken for the expected missing-feature failure by counts. Preserve this preparation limitation.
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
