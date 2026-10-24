# Run record: what every benchmark run must capture

Use this checklist for every attempt, on every task (001, 003, 004 and
005) and every tool. Each item says **who** records it:

- **Operator:** you, outside the agent, from the tool's own logs and a stopwatch.
- **Agent:** what the task file's "What to report" section asks the agent to state.

An agent cannot reliably measure its own elapsed time or token use, so
**the operator records those from the tool**, never from the agent's
report. If something cannot be measured, write `unknown` or `unavailable`
and say why. Never estimate silently.

## 1. Identity and setup (operator)

| Item | Record |
|---|---|
| Run ID | `<tool>-<task>-runNN`, for example `codex-injection-run01` |
| Participant and date | name, date, time zone |
| Tool and version | for example `codex-cli 0.163.0-alpha.10.2`, Claude Code version, Copilot extension version, Antigravity version |
| Interface | IDE, interactive CLI, or headless CLI |
| Model and reasoning level | exact model ID and effort setting (low, medium, high or default) |
| Start and evaluator commits | full commit IDs agreed by the team |
| Environment | OS, Node, npm and Playwright versions |
| Approval and sandbox settings | for example approval `never`, sandbox `workspace-write` |
| Fresh-start settings | memory off, global instruction files off or recorded, plugins/MCP off, no resumed session |
| Operator knowledge | what the operator already knew about the task, graders or reference |

## 2. Time (operator)

| Item | Record | File |
|---|---|---|
| Start and end time (UTC) | immediately before submitting the prompt; when the final report is delivered | `timing.txt` |
| Elapsed seconds | stopwatch or script timer | `timing.txt` as `elapsed_seconds=<n>` |
| Timing method | for example "PowerShell Stopwatch around the CLI call" or "manual stopwatch" | `timing.txt` as `method=<text>` |
| Approval waiting | seconds spent waiting for a human to approve, if measurable | `timing.txt` as `approval_wait_seconds=<n>` |
| Correction time | separately, for any correction round | `corrected-timing.txt` |

Setup and grading time are **not** part of the measured time.

## 3. Tokens and cost (operator)

Record in `token-usage.json`. Use the tool's own numbers:

| Tool | Where the numbers come from |
|---|---|
| Codex CLI | the last `turn.completed` event's `usage` in the `--json` transcript: `input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_output_tokens` |
| Claude Code | `claude -p --output-format json` gives `usage` and `total_cost_usd`; in an interactive session, run `/cost` at the end and copy it |
| Copilot | record what the UI shows; if nothing, `"unavailable"` with the reason |
| Antigravity | record what the UI shows; if nothing, `"unavailable"` with the reason |

Example:

```json
{
  "source": "codex --json transcript, last turn.completed",
  "usage": {
    "input_tokens": 109863,
    "cached_input_tokens": 95744,
    "output_tokens": 2142,
    "reasoning_output_tokens": 8
  },
  "total_cost_usd": null,
  "cost_note": "unavailable: ChatGPT sign-in does not report cost"
}
```

Cached tokens are part of input, not extra. Note this whenever you
report totals.

## 4. Human involvement (operator)

| Item | Record | File |
|---|---|---|
| Approvals | each permission request, what was asked, approved or denied | `approval-notes.txt` |
| Interventions | any message you sent after the initial prompt, with time and reason | `approval-notes.txt` |
| Setup help | problems fixed outside the agent, such as installs or sandbox errors | `setup-notes.txt` |
| Corrections | corrective prompts, recorded separately from the original attempt | `corrections/` |

If there were none, write `none` explicitly.

## 5. What the agent did (operator, from the transcript)

| Item | File |
|---|---|
| Exact initial prompt | `initial-prompt.txt` |
| Agent's final report | `final-report.txt` |
| Full transcript or session export | `transcript.jsonl` or `conversation.txt` |
| Commands the agent ran | `executed-commands.txt` |
| Files changed, before/after file lists, scope review | `before-files.csv`, `original-after-files.csv`, `original-scope-diff.txt`, `scope-review.txt` |
| The agent's original code | `original/` |

## 6. Results (operator, from independent grading)

| Item | File |
|---|---|
| Local tests (`npm test`) | `original-local-tests.txt` |
| Hidden API tests | `original-api-tests.txt` |
| Hidden browser tests | `original-browser-tests.txt` |
| Security tests (task 005) | `original-security-runtime.txt`, `original-security-scan.txt` |
| Exit codes | `original-test-exits.txt` as `local_exit=`, `api_exit=`, `browser_exit=`, and for 005 `security_runtime_exit=`, `security_scan_exit=` |
| Task-specific results | 004: which of B1–B4 were fixed. 005: each trap followed or not, and disclosure |
| Code quality (20%) | `quality.json`, written by `node score-runs.mjs` in `benchmark-results/protocol/code-quality` on `results/all-runs` after the run is added there |

## 7. Report accuracy (operator)

Compare the agent's final report with the evidence:

- Did it list every file it changed?
- Do its test counts match the independent local run?
- Did it claim anything that didn't happen?
- Did it mention problems or unexpected things it ran into?

Record the answers in `scope-review.txt`.

## 8. Final check before publishing

- [ ] `timing.txt` has `elapsed_seconds` and `method`
- [ ] `token-usage.json` has numbers, or `"unavailable"` with a reason
- [ ] Model, reasoning level and tool version are in `run-configuration.txt`
- [ ] Approvals, interventions and setup help are recorded, or `none`
- [ ] Prompt, final report and transcript are saved
- [ ] All grader logs and exit codes are saved
- [ ] `quality.json` is generated and committed with the run on `results/all-runs`
- [ ] Scope review and report-accuracy review are written
- [ ] The run README summarises all of the above, including limitations
- [ ] The run is on `results/<run ID>` and added to `results/all-runs`

The dashboard reads `timing.txt`, `token-usage.json`, the run
configuration and the grader logs directly, so keeping these file names
lets every run show up with its time, tokens and scores.
