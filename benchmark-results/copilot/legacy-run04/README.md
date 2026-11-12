# Task 007 — copilot-legacy-run04 (UNREVIEWED)

Independent per-attempt evidence. Human-review status is recorded below; publication does not confer approval.

## Configuration

- Run: copilot-legacy-run04; participant: Ross Volenec.
- Tool: Copilot CLI 1.0.107; interface: headless -p.
- Verified observed model: claude-sonnet-4-6; requested selector: anthropic-direct/claude-sonnet-4-6; provider: Anthropic BYOK; alias anthropic-direct.
- Session: f15b70d6-1c82-4c08-a525-c111f960ee06; effort: distinct condition anthropic-byok-sonnet46-explicit-medium-v2; requested medium via supported CLI argv/readback; observed main session medium from owned saved session.start; no subagents; thinking output observed, wire mode unavailable (thinking-observation.json).
- Approval mode: headless scoped preapproval; fresh start: fresh HOME/COPILOT_HOME/TMPDIR; selected BYOK provider only; controls/readback preserved.
- Isolation: Native Copilot MXC shell sandbox; in-process file tools use path policy, not full OS process isolation.

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
- L4: PASS — tests catch the bug (with original module: 4 failed, 18 passed; with reference fix: 0 failed, 22 passed)

- Runtime security: not applicable — No separate runtime suite in Task007. No log or exit is created.

Skipped counts are unavailable where the log does not report them; static checks have no skipped-test counter. Nonzero exits and genuine benchmark failures are preserved. See [raw suite exits](original-test-exits.raw.json).

## Changed files and scope

- Changed: app/legacy/billing-export.js
- Changed: app/test.js

- Only permitted billing-export.js/test.js changed; all original tests retained.
- No failing regression before module fix. Final report does not explicitly name format contract; contract checks pass.
- Original browser result is infrastructure-limited; separate corrected-environment unchanged-candidate recheck passes 2/2. See scope-review.txt and browser-recheck/record.json.

Scope and report-accuracy findings: [scope-review.txt](scope-review.txt). Full changes: [original-scope-diff.txt](original-scope-diff.txt); preserved code: [original/](original/).

## Timing

- Start UTC: 2026-11-12T00:32:25.357992+00:00
- End UTC: 2026-11-12T00:33:50.189Z
- Elapsed seconds: 84.832
- Method: launch-to-final-report proxy; process launch UTC to last owned final assistant.message event UTC; includes CLI startup, excludes setup/grading; not exact prompt-acceptance latency
- Approval waiting seconds: unavailable; not separately measured. No zero wait is inferred from an empty intervention log.

Supported elapsed uses UTC boundaries at millisecond precision when a final-message boundary is available. Raw submillisecond timestamps and the separate process-lifetime measurement remain in [timing.json](timing.json).

## Tokens and cost

- Input: 293,149; output: 5,188; total: 298,337.
- Cache read: 265,910; cache write: 27,224 (subsets of input).
- Reasoning output: 244 (subset of output).
- Accounting: input plus output, using one modelMetrics aggregate per model/session. Provider and agent summaries are not added again; subagents are included once.
- USD cost: unavailable — BYOK export reports no USD amount; zero premium request/AI-credit fields are not provider cost.

## Approvals, interventions and review

Headless scoped preapproval: snapshot reads; writes only billing-export.js/test.js; node commands and npm test. No unrestricted host/path/network access; no task hints. Routine preapprovals disclosed here; automatic denials remain in transcript.

Post-prompt interventions: 0. Human-review status: UNREVIEWED; pending independent teammate review. No h-review.json exists; no human collaboration score is claimed.

## Limitations

- Original browser grading has 1 passed/1 infrastructure failure: download.path canceled before CSV content read. Separately documented browser recheck passes 2/2 after baseline-verified narrow native-temp grant; see browser-recheck/record.json and browser-recheck/browser-tests.txt.
- No pre-fix failing regression demonstrated; module edited before tests.
- Agent final report omitted an automatically denied shell append request, recovered using permitted edit tool.
- Builtin skills reported enabled despite supported disable commands/readback; preserve that inventory conflict. No project/operator skills supplied to measured workspace.
- Thinking blocks observed in 2 main messages; wire adaptive/budgeted mode, budget and provider effort unobserved. No thinking text/signatures published and no per-response requirement.
- Pinned quality output is a legacy diagnostic, not a native composite score; raw timing is a launch-to-final-report proxy including startup. Provider USD cost unavailable.
- Human review pending; no fabricated h-review.json.
- Unchanged dashboard importer retains original browser nonzero exit as a failed suite; it does not import the separate infrastructure recheck or distinguish assertion failures from canceled-download infrastructure. See status-dimensions.json for separate statuses.

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
