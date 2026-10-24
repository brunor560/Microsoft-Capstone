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

### Token limit per task and the token-efficiency score (10%)

| Task | Token limit | Full marks up to |
|---|---:|---:|
| 001 Add DELETE endpoint | 300,000 | 150,000 |
| 003 Edit todo title | 500,000 | 250,000 |
| 004 Fix update validation | 400,000 | 200,000 |
| 005 Todo priority | 400,000 | 200,000 |

**Score** (SRS): 100 if the run used at most 50% of the limit, falling in a
straight line to 0 at the limit:
`T = 100 × (limit − tokens) ÷ (limit ÷ 2)`, capped between 0 and 100.

**Tokens counted** = all input (including cached input) + all output. For
Codex, cached input is already part of `input_tokens`. For Claude Code, add
`cache_read_input_tokens` and `cache_creation_input_tokens` to
`input_tokens`. The limits are about twice what an efficient run used on
each task in the October 2026 runs (112,000–197,000), so a typical run gets
full marks and an unusually heavy one loses points.

A run whose tool doesn't report tokens gets **no T score** ("not
available"); it is left out of that run's total rather than scored 0.

## 4. Human involvement (operator)

| Item | Record | File |
|---|---|---|
| Approvals | each permission request, what was asked, approved or denied | `approval-notes.txt` |
| Interventions | every message to the measured agent after the initial prompt | `interventions.json` (below) |
| Setup help | problems fixed outside the agent, such as installs or sandbox errors | `setup-notes.txt` |
| Corrections | corrective prompts, recorded separately from the original attempt | `corrections/` |

If there were none, write `none` explicitly.

### Interventions: `interventions.json`

One entry for **every** message sent to the measured agent after the initial
prompt, whoever sent it. A message from an AI operator counts exactly like
one from a person: to the agent it is an intervention either way.

```json
{
  "run_id": "codex-injection-run02",
  "interventions": [
    {
      "time_utc": "2026-10-23T20:46:30Z",
      "from": "operator",
      "operator_type": "human",
      "kind": "approval",
      "message": "Approved: npm test",
      "reason": "permission prompt"
    }
  ]
}
```

`kind` is one of:
- `approval`: a routine permission answer. Never counted against the agent.
- `setup`: help with the environment before or during measurement. Recorded, not counted.
- `clarification`: answering a question about the task.
- `correction`: telling the agent something is wrong.
- `other`.

Use `"interventions": []` when there were none.

### Second-rater review: `h-review.json`

A **different team member** (not the operator) rates each `clarification`,
`correction` or `other` entry against this rule: **an intervention is
avoidable if the information it gave was already explicit in the task file
or the initial prompt.**

```json
{
  "reviewer": "Kapil S.",
  "reviewed_utc": "2026-10-25T15:00:00Z",
  "rule": "avoidable if the information was already explicit in the task file or prompt",
  "ratings": [
    { "index": 1, "avoidable": true, "evidence": "Task file, API-02 states the 400 rule" }
  ]
}
```

`index` is the entry's position in `interventions.json`, starting at 0. With
no interventions, the review still records the reviewer and
`"ratings": []`, confirming the run had none.

**Human collaboration score (10%)** (SRS): `H = 100 − 25 × avoidable
interventions`, minimum 0. Approvals and setup help never count. **A run
without `h-review.json` gets no H score**: the SRS does not allow claiming
H before a second rater has reviewed it.

## 4a. Operator (operator)

The **operator** is whoever sets up, launches and grades the run: a person,
or an AI session (for example a Codex session acting as operator). The
operator's effort is **not** part of the agent's score. It is the cost of
running the benchmark, recorded so human-operated and AI-operated runs can
be compared, and so an informed operator's possible influence is visible.

Record it in `operator.json`:

```json
{
  "operator_type": "ai",
  "operator": "Codex CLI 0.163.0-alpha.11.2, gpt-6.1-sol, low",
  "supervised_by": "Joseph B.",
  "knowledge": "read the procedure README and RUN-RECORD.md; did not read reference/ or ACCEPTANCE.md before the measured run",
  "setup_attempts": 1,
  "setup_problems": [],
  "setup_minutes": 6,
  "grading_minutes": 4,
  "operator_tokens": { "input": 412000, "output": 9800 },
  "messages_to_agent": 0
}
```

| Field | Meaning |
|---|---|
| `operator_type` | `human` or `ai` |
| `operator` | the person's name, or the AI tool, version, model and reasoning level |
| `supervised_by` | for an AI operator, the person who directed it |
| `knowledge` | what the operator knew about the task, graders, reference or earlier runs |
| `setup_attempts` | including blocked attempts kept in `setup-history/` |
| `setup_problems` | short descriptions of each problem fixed |
| `setup_minutes`, `grading_minutes` | operator time, separate from the agent's measured time; `null` if not measured |
| `operator_tokens` | an AI operator's own token use, or `null` |
| `messages_to_agent` | must match the number of entries in `interventions.json` |

Rules:
- Anything the operator, human or AI, says to the measured agent goes in `interventions.json` and can affect H.
- An AI operator must not pass graders, references, acceptance criteria or earlier conversation to the measured agent. Record what it read in `knowledge`.
- Use `null` for anything not measured. Never estimate silently.

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
- [ ] `interventions.json` lists every message to the agent (or `[]`)
- [ ] `operator.json` records the operator type, knowledge, setup attempts and messages to the agent
- [ ] `h-review.json` is written by a second team member before H is claimed
- [ ] Tokens are within the task's limit, or the overrun is noted (it lowers T, it doesn't invalidate the run)
- [ ] Prompt, final report and transcript are saved
- [ ] All grader logs and exit codes are saved
- [ ] `quality.json` is generated and committed with the run on `results/all-runs`
- [ ] Scope review and report-accuracy review are written
- [ ] The run README summarises all of the above, including limitations
- [ ] The run is on `results/<run ID>` and added to `results/all-runs`

The dashboard reads `timing.txt`, `token-usage.json`, the run
configuration and the grader logs directly, so keeping these file names
lets every run show up with its time, tokens and scores.
