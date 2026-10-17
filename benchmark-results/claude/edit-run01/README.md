# Claude Code title-edit benchmark — claude-edit-run01

Claude Code (`claude-sonnet-5-5`, Claude Code's default model) passed every independent check on its first attempt:

| Suite | Passed | Failed | Exit code |
|---|---|---|---|
| Local app tests (9 original + 5 new) | 14 | 0 | 0 |
| Independent API tests | 12 | 0 | 0 |
| Independent browser tests | 10 | 0 | 0 |

Only the three allowed files changed. All nine original tests were preserved. No correction was needed. Elapsed time was 87.3 s from prompt to final report.

## Run conditions
- Participant: Bruno Rocha (Claude Code).
- Operator: Claude, an AI assistant, working on Bruno's behalf in a claude.ai cloud workspace. No person was at the keyboard during the run. Bruno should review this report before the team relies on it.
- Date: 2026-10-14 (America/New_York); run start 2026-10-15T00:00:21Z UTC.
- Run ID: claude-edit-run01.
- Harness and interface: Claude Code CLI 2.1.300, headless (`claude -p`), fresh session with no session persistence. The exact command is in `conversation/command.txt`.
- Model and effort: no model was chosen, so Claude Code used its default, `claude-sonnet-5-5`, as reported by the session's init message. Reasoning/effort was Claude Code's default; the exact level is unknown. `token-usage.json` lists every model the CLI called.
- OS / Node / npm: Linux cloud sandbox / Node v22.22.0 / npm 10.9.4. The procedure was written for Windows PowerShell; equivalent bash commands were used. See `environment.txt`.
- Approval and sandbox settings:
  - **Permission mode:** `--permission-mode default`. Headless mode cannot show approval prompts.
  - **Pre-approved tools:** Read, Edit, Write, Glob, Grep, `npm test`, `npm ci`, `npm install`, `node`, `ls`, `cat`. Everything else was denied automatically and logged.
  - **Isolation:** there is no OS-level sandbox beyond the cloud container. These settings are the same as in claude-delete-run01.
- Integrations, MCP servers and automatically loaded instructions:
  - **Settings:** `--setting-sources project`; the run folder contains no project settings or CLAUDE.md. `--strict-mcp-config` loaded no MCP config files.
  - **Chrome:** the Chrome browser tools were explicitly disallowed. The workspace's Claude in Chrome connection still showed as connected in the init message, but it was never used.
  - **Built-ins:** Claude Code's built-in skills and plugins loaded automatically. None were invoked.
  - **Workspace environment:** the session ran inside the claude.ai cloud workspace, so it inherited that environment's extra tools and its scratchpad instructions. It is not a stock local Claude Code install. The full list is in the init line of `conversation/transcript.jsonl`.
- Starting app/task commit: 4e258a96855d98edd10247f68c0b8265e53a8921.
- Evaluator commit: 02996447e01bb284939d9b1a83c45ab033c22fb9, the same as the antigravity-edit-run01 and codex-edit-run01 runs.
- Grader hashes: `grader-hashes.csv` was hashed with LF line endings, so the values differ from the Windows runs. Converting the files to CRLF reproduces the teammates' published hashes exactly for all seven files. The content is identical. See `grader-hash-reconciliation.txt`.
- Operator's prior knowledge: the operator read this procedure, VALIDATION.md and the teammates' published results before the run, but no reference solution. No hints were given to the agent.

## Setup
- **Local baseline:** 9 passed, 0 failed, as expected (`baseline-local-tests.txt`).
- **Evaluator install:** `npm ci` succeeded and Playwright is 1.64.1.
- **Browser deviation:** `npx playwright install chromium` failed because this workspace's network blocks the download. The workspace's preinstalled Playwright Chromium (headless shell 141.0.7390.37, build 1194) was mapped in place of the expected 156.0.8078.4 (build 1248). Only the browser binary differs; the evaluator code and config are unchanged.
- **Setup check of the untouched starting app:**
  - API: 5 passed / 7 failed, matching VALIDATION.md.
  - Browser: 0 / 10. All ten failures occur at the missing `li[data-todo-id]` row attribute, as documented. See `baseline-api-tests.txt`, `baseline-browser-tests.txt` and `baseline-browser-report/`.
- **Setup time:** not counted in coding time.

## Original attempt
- Prompt: the exact Step 7 text (`conversation/initial-prompt.txt`).
- Elapsed time: 87.3 s, measured with `date` around the CLI process, from launch with the prompt to process exit. Claude Code reported 85.7 s session duration and 18 turns. There was no approval waiting (headless) and no operator delay. Stdin was redirected from /dev/null, so the 3 s stdin wait seen in claude-delete-run01 did not occur.
- Permission requests and denials: 0 interactive approvals. Five Bash commands were denied, all automatically by Claude Code's command-safety checks or by the pre-approved list:
  1. A `cat >> test.js` heredoc, blocked as "brace with quote character".
  2. The same append combined with an inline Python script, blocked for the same reason.
  3. Append plus a Python patch script, which needed approval.
  4. Output redirection to `app/test.js`, which needed approval.
  5. `python3 patch.py`, which needed approval.

  The agent then made all edits with the Edit tool. Full details are in `token-usage.json` (`permission_denials`).
- Access outside the workspace: the agent wrote three scratch files (`append.js`, `new_js.txt`, `patch.py`) into its harness-provided scratchpad under `/tmp`, outside the run folder. That scratchpad is a convention of this cloud environment, and the agent's attempts to run them were all denied. The files contain only draft code for the allowed files. Copies are in `outside-workspace-files/`. No access to parent folders, graders or other runs was observed.
- Human assistance and coding hints: none.
- Agent's final report: "14 tests, 14 passed, 0 failed"; only the three allowed files changed. It noted that it did not check the interface in a real browser (`conversation/final-report.txt`). The independent rerun confirms 14/14, so the report is accurate.
- Independent grading: `original-test-exits.txt`, `original-local-tests.txt`, `original-api-tests.txt`, `original-browser-tests.txt`, `original-browser-report/`, `original-browser-test-results/`.

## Scope and requirement review
- **Changed files:** only `app/public/index.html`, `app/server.js` and `app/test.js` (`original-scope-diff.txt`). No directories were added or removed.
- **Existing tests:** all nine original tests are preserved; no line of the original test.js was removed.
- **New tests:** five new local API tests cover a valid trimmed update, invalid titles rejected with 400 and nothing changed, completion-only updates, other todos unchanged, and 404 for a missing todo. This meets the task's local-test requirement.
- **Server:** the only server lines removed are the old PUT body handling, which the task requires replacing. A supplied title that is not a non-empty string now returns 400 before any field changes.
- **Error messages:**
  - A blank title shows "Title cannot be empty."
  - A failed save shows "Could not save title: Server responded with status 500", or "Could not save title: Failed to fetch" for a network error.

  Both appear in a `role="alert"` inside the row and explain the problem. The network wording is the browser's own, so it is somewhat technical.
- **Out-of-scope observation:** PUT still parses the ID with `parseInt`, which is pre-existing behaviour that the task does not cover, so `/api/todos/1abc` resolves to todo 1. This is not counted as a defect for this task.

## Correction
Not required: every grader passed and the review found no defects.

## Token usage
`token-usage.json`: Sonnet used 18 turns, about US$0.31 at list price. A small Haiku call was also made by the CLI.

## Limitations
- Platform, mode and approvals differ from the other runs:
  - **Antigravity:** Windows, interactive, Gemini 3.8 Flash Medium, about 533 s.
  - **Codex:** Windows, headless, GPT-6.1 Sol low, 72.6 s.
  - **This run:** Linux, headless, Claude Code's default Sonnet model, with a pre-approved tool list instead of interactive approvals.
- Browser grading used Chromium 141 instead of the pinned 156.
- The CLI version moved from 2.1.296 (delete run) to 2.1.300 between runs; updates are automatic.
- One attempt on one task does not establish a general tool winner.
