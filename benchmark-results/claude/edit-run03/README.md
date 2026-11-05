# claude-edit-run03 — Claude Code headless CLI, Sonnet 4.6, title-edit task (003), original baseline

## Configuration
- Tool: Claude Code 2.1.318, headless CLI (`claude -p`), model `claude-sonnet-4-6`, effort default.
- Baseline (app/task) commit: `4e258a96855d98edd10247f68c0b8265e53a8921` — the commit the four original edit-run01 runs used.
- Evaluator: head of `benchmark-protocol-v2-edit` on 2026-11-04 (full ID in `source-commits.txt`); grader code byte-identical to `0299644` and `67dd886`. Team confirmation pending.
- Environment: Ubuntu 24.04 cloud container, Node 22.22.0, npm 10.9.4, Playwright 1.64.1 with Chromium 141.
- Fresh start: new session; memory off; no global CLAUDE.md; user settings/hooks not loaded; MCP, skills and Chrome off; tools limited to Bash, Read, Edit, Write, Glob, Grep.
- Permissions: edits and Bash pre-approved (no prompts). Details in `run-configuration.txt`, `run-command.txt`.

## Results (original attempt, no corrections)
| Suite | Result | Exit |
|---|---|---|
| Local (`npm test`) | 16 passed, 0 failed (9 preserved + 7 new) | 0 |
| Hidden API | 12 passed, 0 failed | 0 |
| Hidden browser | 10 passed, 0 failed | 0 |

- Scope: only `app/server.js`, `app/test.js`, `app/public/index.html` changed.
- Elapsed: 134.0 s (operator timer around the CLI call); approval wait 0 s.
- Tokens: input 9 + cache write 28,356 + cache read 113,164; output 10,857; 9 turns. Cost $0.367 (CLI list price). Cached tokens are part of input.
- Approvals/denials/interventions: none. Corrections: none needed.
- Report accuracy: accurate (`scope-review.txt`).

## Comparison with claude-edit-run02
Same tool, model, settings and app; run02 used task commit `522f9ad` (longer required final report), this run uses `4e258a9`. Both passed every suite. Treat the pair as a small repeatability check, not as evidence about the task-file wording.

## Limitations
- Linux/bash, not Windows PowerShell; manifests are `sha256sum` text, not CSV.
- Browser grading used pre-installed Chromium 141 through an operator wrapper config because the browser download was blocked; grader files unmodified (hashes verified).
- The CLI updated itself between run02 (2.1.309) and this run (2.1.318).
- CLI ran inside a host-managed Claude Code container; managed settings and host system prompt could not be fully removed.
- The operator had seen run02's output on the same app (no hints were given). One attempt on one task does not establish a general ranking.
