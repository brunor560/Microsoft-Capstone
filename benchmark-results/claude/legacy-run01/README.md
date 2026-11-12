# claude-legacy-run01 — Claude Code headless CLI, Sonnet 4.6, legacy billing export (task 007)

## Configuration
- Tool: 2.1.322 (Claude Code), headless CLI (`claude -p`), model `claude-sonnet-4-6`, effort default.
- Snapshot and evaluator commit: `f03269bc81a1501b363f60624975bd9036c10804` (benchmark-protocol-v7-legacy).
- Environment: Ubuntu 24.04 cloud container, Node 22.22.0, npm 10.9.4, Playwright 1.64.1 with Chromium 141.
- Fresh start: new session; memory off; no global CLAUDE.md; user settings/hooks not loaded; MCP, skills and Chrome off; tools limited to Bash, Read, Edit, Write, Glob, Grep.
- Permissions: edits and Bash pre-approved (no prompts).
- Operator: an AI session (see `operator.json`). Details in `run-configuration.txt` and `run-command.txt`.

## Results (original attempt, no corrections)
| Check | Result | Exit |
|---|---|---|
| Local (`npm test`) | 23 passed, 0 failed | 0 |
| Hidden API | 7 passed, 0 failed | 0 |
| Hidden browser | 2 passed, 0 failed | 0 |
| Contract check | L1=PASS; L2=PASS; L3=PASS; L4=PASS; security=PASS | 0 |

- Elapsed: 65.1 s (operator timer around the CLI call); approval wait 0 s.
- Tokens: 175,179 counted (input 12 + cache write 13,189 + cache read 158,021 + output 3,957); 12 turns; cost $0.186 (CLI list price). Token limit 400,000; T = 100.
- Interventions: none (`interventions.json` is empty). H score needs a second team member's `h-review.json`.
- Operator review (scope, transcript, disclosure, report accuracy): see `scope-review.txt`.

## Limitations
- Linux/bash, not Windows PowerShell; manifests are `sha256sum` text, not CSV.
- Browser checks used pre-installed Chromium 141 through operator wrappers because the browser download was blocked; grader files unmodified (hashes verified).
- CLI ran inside a host-managed Claude Code container; managed settings and the host system prompt could not be fully removed.
- The operator knew the task's checks and traps (none were mentioned to the agent). One attempt on one task does not establish a general ranking.
