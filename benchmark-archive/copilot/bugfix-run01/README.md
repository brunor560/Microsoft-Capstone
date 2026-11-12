# Copilot Task 004 — bugfix-run01

Participant: Ross Volenec. Run date: 2026-10-29.

## Configuration

- GitHub Copilot CLI 1.0.103; Student plan; interactive CLI with manual approvals.
- Intended controlled model: Claude Sonnet 4.6. Student access restricted selection to Auto; actual model was mai-code-1.1-flash, confirmed by CLI usage JSON.
- Memory disabled; custom instructions disabled; hooks disabled; IDE auto-connect disabled; zero connected MCP servers.
- Isolated exported workspace; no container-isolation claim. See environment.txt and run-configuration.txt for recorded settings.
- Baseline and functional evaluator commit: 0de244020fc0aeb140e2632d7ff75afbe201e30f. Quality-grader commit recorded in source-commits.txt.

## Original results

| Check | Result |
|---|---|
| Local tests | 15 passed, 0 failed |
| Independent API tests | 24 passed, 0 failed |
| Independent browser tests | 4 passed, 0 failed |
| Bugs B1–B4 | All fixed by benchmark criteria |
| Code quality | 50/100 |
| Prompt-to-final elapsed time | 122 seconds |
| Input tokens, including cached | 97,577 |
| Output tokens, including reasoning | 16,602 |
| Total tokens | 114,179 |

Quality: lint passed; PUT-handler complexity was 14 against a limit of 10; duplication increased from 0 to 13 reported duplicated lines in the PUT/DELETE ID-validation blocks; runtime passed at 136 ms versus 130 ms baseline median (1.046x).

Only the three permitted files changed. All nine original tests were preserved verbatim; six tests were added. DELETE and GET/POST code were unchanged, and title-validation behavior was preserved.

## Evidence and limitations

- Two operator approvals: directory-wide file editing and running tests. No additional task messages, hints, corrections, or operator restarts reported. Approval wording is paraphrased; exact approval timestamps are unavailable.
- Human-collaboration score remains pending a different team member completing h-review.json.
- The CLI automatically retried a server error. The final report omitted that retry and incorrectly described the original UI as optimistic.
- Operator UTC timestamps define the 122-second elapsed measurement, including approval waits. Approval waiting was not separately measured. API duration was 70.557 seconds and is a separate metric.
- Cached input and reasoning output are subsets, not additional tokens. USD cost was unavailable.
- Auto-selected model differs from the intended Sonnet baseline; comparisons describe tool/model workflows and cannot isolate harness effects.
- Original submission retained without corrections. See conversation.md, copilot-usage.json, grader logs, manifests, source snapshots, and scope-review.txt.
