# claude-bugfix-run01 — Claude Code headless CLI, Sonnet 4.6, update-validation bug fix (task 004)

## Configuration
- Tool: Claude Code 2.1.309, headless CLI (`claude -p`), model `claude-sonnet-4-6`, effort default.
- Baseline and evaluator commit: `eb848b67ad0fcbdcb35c5058d13773de9cfaa6cd` (agreed commit); app `4e258a9`.
- Environment: Ubuntu 24.04 cloud container, Node 22.22.0, npm 10.9.4, Playwright 1.64.1 with Chromium 141.
- Fresh start: new session; memory off (`autoMemoryEnabled:false`, memory MCP removed); no global CLAUDE.md; user settings/hooks not loaded; MCP, skills and Chrome off; tools limited to Bash, Read, Edit, Write, Glob, Grep.
- Permissions: edits and Bash pre-approved (no prompts). Details in `run-configuration.txt`, `run-command.txt`.

## Results (original attempt, no corrections)
| Suite | Result | Exit |
|---|---|---|
| Local (`npm test`) | 22 passed, 0 failed (9 preserved + 13 new) | 0 |
| Hidden API | 24 passed, 0 failed | 0 |
| Hidden browser | 4 passed, 0 failed | 0 |

- Bugs fully fixed: B1, B2, B3, B4 (`bugs-fixed.txt`).
- Scope: only the three allowed app files changed; DELETE, title validation and packages unchanged.
- Elapsed: 111.0 s (operator timer around the CLI call); approval wait 0 s.
- Tokens: input 12 + cache write 15,951 + cache read 163,617; output 7,877; 12 turns. Cost $0.263 (CLI list price). Cached tokens are part of input.
- Approvals/denials/interventions: none. Corrections: none.
- Report accuracy: files and counts accurate; causes accurate for B1 and B4, incomplete for B2 (does not name parseInt accepting "5abc"/"1.0") and not stated for B3 (`scope-review.txt`).

## Limitations
- Linux/bash, not Windows PowerShell; manifests are `sha256sum` text, not CSV.
- Browser grading used pre-installed Chromium 141 through an operator wrapper config because the browser download was blocked; grader files unmodified (hashes verified).
- CLI ran inside a host-managed Claude Code container; managed settings and the host system prompt could not be fully removed.
- Headless interface with pre-approved permissions differs from interactive runs. One attempt on one task does not establish a general ranking.
