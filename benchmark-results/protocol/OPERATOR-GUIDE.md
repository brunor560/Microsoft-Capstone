# Operator guide: recording help and interaction

For whoever runs a benchmark attempt on task 001, 003, 004 or 005: a
person, or an AI session acting as operator. Follow it on every run. It
produces the evidence for the **human collaboration** score (H, 10%) and the
**operator** record (RUN-RECORD.md sections 4 and 4a).

**The rule: write down anything at all that happened besides the agent
working on its own.** That includes help the agent got, help you gave
outside the agent, and help you needed yourself. If nothing happened, record
that explicitly. "None" is evidence; a missing file is not.

## Two separate logs

| Log | What goes in it | Affects the agent's score? |
|---|---|---|
| `interventions.json` | Every message or action **directed at the measured agent** after the initial prompt: approvals, answers, nudges, corrections, restarts of its session | Yes. Clarifications and corrections can cost H points once a second rater has reviewed them |
| `operator.json` → `operator_help` | Help **the operator** needed or received: a person helping an AI operator, a teammate helping a person, looking something up, fixing the environment outside the agent | No. It shows the cost of running the benchmark |

If you aren't sure which log something belongs in, put it in both and say
why in `reason`.

## Before the run

1. Create both files in the evidence folder, empty (templates below).
2. Fill in the operator fields you already know: type, who you are (or the
   AI tool, model and reasoning level), who supervises, and what you have
   read about this task, its graders, reference or earlier runs.
3. Start the help log at the same time as the timing.

## During the run: log as it happens

Add an entry, with the time, the moment any of these happens:

- **The agent asks for permission** (to run a command, edit a file, use the
  network). Log the request and your answer: `kind: "approval"`.
- **The agent asks a question** or stops waiting for input. Log the question
  and your answer: `kind: "clarification"`.
- **You tell the agent something is wrong**, or that it should change
  approach: `kind: "correction"`. In the original attempt this should not
  happen; if it does, it must be logged.
- **You restart, resume or nudge** the session ("continue", pressing Enter,
  re-sending the prompt): `kind: "other"`, with the reason.
- **You fix something outside the agent** while it runs (an install, a
  sandbox error, a port in use): add it to `operator_help` and, if the agent
  was told or affected, to `interventions.json` as `kind: "setup"`.
- **You need help yourself**: an AI operator asks a person, a person asks a
  teammate, or anyone looks up documentation. Add it to `operator_help`.

Write the exact words sent to the agent in `message`. Don't summarise them.

## After the run: answer every question

Answer each one yes or no in `operator.json` under `checklist`, and add a
log entry for every "yes":

| Question | If yes, log it in |
|---|---|
| Did the agent ask for any permission? | `interventions.json` (`approval`) |
| Did the agent ask any question, or stop and wait for input? | `interventions.json` (`clarification`) |
| Did anyone tell the agent it was wrong or should do something differently? | `interventions.json` (`correction`) |
| Was the agent's session restarted, resumed, nudged or re-prompted? | `interventions.json` (`other`) |
| Did anyone fix the environment, tools or files during the run? | `operator_help`, and `interventions.json` (`setup`) if the agent was involved |
| Did the operator need or receive any help? | `operator_help` |
| Did anything else unusual happen (crash, timeout, network problem, a stray file)? | `operator_help` or `interventions.json`, with the reason |

Then check:
- `messages_to_agent` in `operator.json` equals the number of entries in
  `interventions.json`.
- Every entry has a time, a `kind`, the exact `message` and a `reason`.
- Give both files to a **different** team member, who writes `h-review.json`
  (RUN-RECORD.md section 4). Until then the run has no H score.

## Templates

`interventions.json`, with none:

```json
{ "run_id": "<run ID>", "interventions": [] }
```

`interventions.json`, with entries:

```json
{
  "run_id": "codex-bugfix-run03",
  "interventions": [
    { "time_utc": "2026-10-25T14:02:11Z", "from": "operator", "operator_type": "human",
      "kind": "approval", "message": "Allow: npm.cmd test", "reason": "permission prompt" },
    { "time_utc": "2026-10-25T14:03:40Z", "from": "operator", "operator_type": "ai",
      "kind": "clarification", "message": "Yes, leading zeros are allowed.", "reason": "the agent asked whether 01 is a valid id" }
  ]
}
```

`operator.json`:

```json
{
  "operator_type": "ai",
  "operator": "Codex CLI 0.163.0-alpha.11.2, gpt-6.1-sol, low",
  "supervised_by": "Joseph B.",
  "knowledge": "read the procedure README, RUN-RECORD.md and OPERATOR-GUIDE.md; did not read reference/ or ACCEPTANCE.md before the measured run",
  "setup_attempts": 1,
  "setup_problems": [],
  "setup_minutes": 6,
  "grading_minutes": 4,
  "operator_tokens": { "input": 412000, "output": 9800 },
  "messages_to_agent": 0,
  "operator_help": [
    { "time_utc": "2026-10-25T13:55:00Z", "from": "Joseph B.", "what": "confirmed which commit to use" }
  ],
  "checklist": {
    "agent_asked_permission": false,
    "agent_asked_question_or_waited": false,
    "agent_was_corrected": false,
    "session_restarted_or_nudged": false,
    "environment_fixed_during_run": false,
    "operator_needed_help": true,
    "anything_else_unusual": false
  },
  "notes": "none"
}
```

Use `null` for anything not measured, and `[]` or `"none"` for "nothing
happened". Never leave a field out.

## PowerShell helper (optional)

Paste once into the operator's PowerShell window, after `$evidenceDir` is
set. It creates the files and adds timestamped entries:

```powershell
function Start-HelpLog($runId) {
  $iv = Join-Path $evidenceDir 'interventions.json'
  if (-not (Test-Path $iv)) { @{ run_id = $runId; interventions = @() } | ConvertTo-Json -Depth 5 | Set-Content $iv }
}
function Add-Intervention($kind, $message, $reason, $operatorType = 'human') {
  $iv = Join-Path $evidenceDir 'interventions.json'
  $log = Get-Content $iv -Raw | ConvertFrom-Json
  $entry = [ordered]@{ time_utc = (Get-Date).ToUniversalTime().ToString('o'); from = 'operator'
    operator_type = $operatorType; kind = $kind; message = $message; reason = $reason }
  $log.interventions = @($log.interventions) + [pscustomobject]$entry
  $log | ConvertTo-Json -Depth 5 | Set-Content $iv
}
```

Example:

```powershell
Start-HelpLog 'codex-bugfix-run03'
Add-Intervention 'approval' 'Allow: npm.cmd test' 'permission prompt'
```

## If the operator is an AI

Give the AI operator this block, in addition to the task procedure:

```text
You are the operator, not the coder. Besides running and grading the
measured session, keep two logs in the evidence folder, following
OPERATOR-GUIDE.md in the grader folder:

1. interventions.json: every message or action directed at the measured
   agent after the initial prompt, with the UTC time, kind (approval,
   clarification, correction, setup, other), the exact message and the
   reason. If there were none, write "interventions": [].
2. operator.json: your tool, model and reasoning level; who supervises you;
   exactly what you read beforehand; setup attempts and problems; setup and
   grading minutes; your own token use if you can see it; the number of
   messages to the agent; operator_help (every time you asked the person
   supervising you for anything, or they told you anything); and the
   checklist of yes/no answers.

Do not send the measured agent any hints or corrections. If you must answer
it, answer only from the task file, and log it. Record everything,
including things that seem trivial; write "none" or [] when nothing
happened, and null when something wasn't measured. Report both files in
your final message.
```

The person supervising an AI operator also adds to `operator_help` anything
they told the AI operator that isn't in its own record.
