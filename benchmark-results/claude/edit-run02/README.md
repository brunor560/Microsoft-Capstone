# claude-edit-run02 — Claude Code headless CLI, Sonnet 4.6, title-edit task (003)

## Configuration
- Tool: Claude Code 2.1.309, headless CLI (`claude -p`), model `claude-sonnet-4-6`, effort default.
- Baseline (app/task) commit: `522f9ada608b30f8801bfa4fac1a164cef3c647c`
- Evaluator commit: `67dd8864e4776f5e536aec97e072c6a402f47c46` (protocol branch head on 2026-10-23; **team confirmation pending**)
- Environment: Ubuntu 24.04 cloud container, Node 22.22.0, npm 10.9.4, Playwright 1.64.1 with Chromium 141 (see limitations).
- Permissions: edits and Bash pre-approved (no prompts). Tools limited to Bash, Read, Edit, Write, Glob, Grep. MCP, skills and Chrome disabled. Fresh session.
- Full details: `run-configuration.txt`, command in `run-command.txt`.

## Results (original attempt, no corrections)
| Suite | Result | Exit |
|---|---|---|
| Local (`npm test`) | 15 passed, 0 failed (9 preserved + 6 new) | 0 |
| Hidden API | 12 passed, 0 failed | 0 |
| Hidden browser | 10 passed, 0 failed | 0 |

- Scope: only `app/server.js`, `app/test.js`, `app/public/index.html` changed; no files added or removed.
- Elapsed: 118.9 s (operator timer around the CLI call); approval wait 0 s.
- Tokens: input 10 + cache write 26,588 + cache read 120,796; output 9,184; 10 turns. Cost $0.334 (CLI list price). Cached tokens are part of input.
- Approvals/denials/interventions: none. Corrections: none needed.
- Report accuracy: accurate; listed all files, counts match, no unsupported claims (`scope-review.txt`).

## Limitations
- Linux/bash run, not Windows PowerShell; manifests use `sha256sum` text format instead of CSV.
- Browser grading used pre-installed Chromium 141 via an operator wrapper config (`playwright.local-browser.config.cjs`) because the browser download was blocked; grader files themselves were unmodified (hashes verified). Other participants likely used the Playwright-bundled Chromium.
- The CLI ran inside a host-managed Claude Code container; managed settings and host system prompt could not be fully removed, so this is not identical to a stock local install.
- Interface (headless) and permission mode differ from interactive runs; one attempt on one task does not establish a general ranking.
- Evaluator commit not yet confirmed by the team; regrade if a different commit is agreed.
