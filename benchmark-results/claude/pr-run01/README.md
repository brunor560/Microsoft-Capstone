# claude-pr-run01 — Claude Code headless CLI, Sonnet 4.6, requirements to merged pull request (task 008)

## Configuration
- Tool: 2.1.323 (Claude Code), headless CLI (`claude -p`), model `claude-sonnet-4-6`, effort default.
- Start commit `05899859f699a1a7167e456c875801cf8faf619c`; evaluator commit `31887c6e23cbbccbfe009cd8919526872b5afd5a`; base branch `bench008/claude-pr-run01/main`.
- GitHub MCP: official `github/github-mcp-server` v2.1.0, local stdio, default toolsets; account brunor560 (credential injected by the session proxy, no PAT). Ruleset off.
- Permissions: edits, Bash and all GitHub MCP tools pre-approved (headless, no prompts). Preflight passed with the same settings.
- Fresh start: new session; memory off; no global CLAUDE.md; user settings/hooks not loaded; only the GitHub MCP server; skills and Chrome off.
- Environment: Ubuntu 24.04 cloud container, Node 22.22.0. Operator: an AI session (`operator.json`). Details: `run-configuration.txt`, `run-command.txt`.

## Results (original attempt, no corrections)
| Check | Result | Exit |
|---|---|---|
| Local (`npm test`, merged commit) | 11 passed, 0 failed | 0 |
| Hidden API | 4 passed, 0 failed | 0 |
| Hidden browser | 2 passed, 0 failed | 0 |
| Flow check (Security) | P1=PASS; P2=PASS; P3=PASS; P4=PASS; security=PASS | 0 |

- Code quality (code-quality 1.0.0, `score-runs.mjs --only claude/pr-run01` on results/all-runs): 100 — lint 0→0, complexity 0→0, duplication 0→0, test runtime 1.008×. See `quality.json`.
- PR #39 merged as `1e78689` after one passing `pr-gate` run; no gate failures.
- Elapsed: 366.6 s (operator timer around the CLI call, including the CI wait); approval wait 0 s.
- Tokens: 818,747 counted (input 27 + cache write 16,876 + cache read 796,950 + output 4,894) over the main session (25 turns) and one extra turn after a background task ended; cost $0.414 (CLI list price). Token limit 400,000; T = 0.
- Interventions: none. H score needs a second team member's `h-review.json`.
- Operator review: `scope-review.txt` (all GitHub steps through MCP; one failed background `gh api` poll noted).

## Limitations
- No classic PAT: the session proxy supplied brunor560's credentials, so token scopes differ from the procedure's `repo`-only token.
- Linux/bash, not Windows PowerShell; manifests are `sha256sum` text.
- Browser checks used pre-installed Chromium through operator wrappers; pr-check ran with NODE_USE_ENV_PROXY=1. Grader files unmodified.
- CLI ran inside a host-managed Claude Code container. One attempt on one task does not establish a general ranking.
