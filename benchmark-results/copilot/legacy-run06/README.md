# Task 007 — copilot-legacy-run06 (UNREVIEWED)

Independent per-attempt evidence. Human-review status is recorded below; publication does not confer approval.

## Configuration

- Run: copilot-legacy-run06; participant: Ross Volenec.
- Tool: GitHub Copilot CLI 1.0.114; interface: headless.
- Verified observed model: claude-sonnet-4-6; requested selector: anthropic-direct/claude-sonnet-4-6; provider: Anthropic BYOK.
- Session: f469f982-c75b-4b7c-b32d-e57be1bc1aeb; effort: medium, from owned session events.
- Approval mode: headless scoped preapproval; fresh start: fresh HOME, COPILOT_HOME, TMPDIR and owned session.
- Isolation: Copilot native MXC command sandbox with loopback access and no bypass.

## Pinned inputs

- Task snapshot: f03269bc81a1501b363f60624975bd9036c10804
- Evaluator: f03269bc81a1501b363f60624975bd9036c10804
- Quality grader: 987547d9619e0628631e8e18031fe50c63b318dc

## Independent results

| Suite | Passed | Failed | Skipped | Exit |
|---|---:|---:|---:|---:|
| [Local](original-local-tests.txt) | 21 | 0 | 0 | 0 |
| [Independent API](original-api-tests.txt) | 7 | 0 | 0 | 0 |
| [Independent browser](original-browser-tests.txt) | 2 | 0 | Unavailable | 0 |
| [Static security](original-security-scan.txt) | 4 | 0 | Not applicable | 0 |

- L1: PASS — header, CRLF line endings, empty and missing list
- L2: PASS — row order, id padding and DONE column
- L3: PASS — cutting, spreadsheet guard, and unchanged output for titles that need no quoting
- L4: PASS — tests catch the bug (with original module: 5 failed, 16 passed; with reference fix: 0 failed, 21 passed)

Skipped counts are unavailable where the log does not report them; static checks have no skipped-test counter. Nonzero exits and genuine benchmark failures are preserved. See [raw suite exits](original-test-exits.raw.json).

## Changed files and scope

- Changed: app/legacy/billing-export.js
- Changed: app/test.js

- File changes are limited to the two permitted paths. The submitted dependency tree matched the frozen installation.
- L1=PASS  header, CRLF line endings, empty and missing list
- L2=PASS  row order, id padding and DONE column
- L3=PASS  cutting, spreadsheet guard, and unchanged output for titles that need no quoting
- L4=PASS  tests catch the bug (with original module: 5 failed, 16 passed; with reference fix: 0 failed, 21 passed)
- The event audit did not establish a test command before the first recorded module edit.
- Server and page hashes are unchanged.

Scope and report-accuracy findings: [scope-review.txt](scope-review.txt). Full changes: [original-scope-diff.txt](original-scope-diff.txt); preserved code: [original/](original/).

## Timing

- Start UTC: 2026-11-19T18:42:38.600016+00:00
- End UTC: 2026-11-19T18:44:00.738Z
- Elapsed seconds: 82.138
- Method: launch-to-final-report proxy; process launch UTC to last owned final assistant.message event UTC; includes CLI startup, excludes setup/grading; not exact prompt-acceptance latency
- Approval waiting seconds: unavailable; not separately measured. No zero wait is inferred from an empty intervention log.

Supported elapsed uses UTC boundaries at millisecond precision when a final-message boundary is available. Raw submillisecond timestamps and the separate process-lifetime measurement remain in [timing.json](timing.json).

## Tokens and cost

- Input: 299,286; output: 5,842; total: 305,128.
- Cache read: 282,363; cache write: 16,908 (subsets of input).
- Reasoning output: 184 (subset of output).
- Accounting: input plus output, using one modelMetrics aggregate per model/session. Provider and agent summaries are not added again; subagents are included once.
- USD cost: unavailable — Raw Copilot metrics expose request/AI-credit counters, not verified provider USD cost.

## Approvals, interventions and review

Headless scoped preapprovals are listed in launch-arguments.json. The native shell sandbox was enabled. The owned event log showed zero interactive operator interventions.

Post-prompt interventions: 0. Human-review status: UNREVIEWED; Pending. No h-review.json exists; no human collaboration score is claimed.

## Limitations

- The native Copilot sandbox was verified for shell execution. Built-in file tools use Copilot path checks.
- Dedicated interactive /session output was unavailable for this headless completion. The owned events and usage export corroborated the session.
- Provider thinking request fields and USD cost were unavailable.
- Runtime reported enabled built-in skills despite disable settings. Observed names: customize-cloud-agent, github-pr-media, pr-stack.

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
