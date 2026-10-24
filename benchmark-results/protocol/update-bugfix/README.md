# Shared bug-fix benchmark procedure (task 004)

## 1. Starting point and evaluator source

- Branch: benchmark-protocol-v3-bugfix. One commit holds both the task
  file and the graders; there is no separate start branch.
- Agreed commit, used for both the snapshot and the graders:
  0de244020fc0aeb140e2632d7ff75afbe201e30f
  (adds the standard "What to report" section to the task file and
  RUN-RECORD.md; the team must confirm it before new runs)
- Underlying app: 4e258a96855d98edd10247f68c0b8265e53a8921 (the same app
  as the title-edit task)
- Task: pipeline/tasks/004-fix-update-validation.md
- Evaluator folder: benchmark-results/protocol/update-bugfix/

Later commits on this branch change documentation only; the grader files
are identical to the agreed commit. Use the agreed commit for snapshots
and grading so every run matches.

The starting application has Add, completion toggling, and Delete. Its
`PUT /api/todos/:id` endpoint and its status-toggle code contain the bugs
described in [ACCEPTANCE.md](ACCEPTANCE.md).

Record the agreed commit ID for every attempt, as both the baseline
commit and the protocol commit.

Give the agent only the isolated app/task snapshot created below. Keep
graders, the reference solution (`reference/`), ACCEPTANCE.md, evidence,
and previous results outside it.

### Earlier runs

Runs before `0de2440` (including `codex-bugfix-run02`, which used
`eb848b6`) had no "How your work is graded" section in the task file, so
those agents were not told that code quality is graded. The app and graders
are unchanged. Record which commit each run used.

The task 004 runs published before this change (Antigravity and Codex
`bugfix-run01`) used commit `1e690f91a11dd1b37c796345a511d6791476efbc`. That commit has the same app and
graders, but the task file asked for a shorter final report. Compare
grader results directly; compare final reports with that difference in
mind, and record which commit each run used.

## 2. Record the run conditions

**Use [RUN-RECORD.md](RUN-RECORD.md) for every run.** It lists everything
to capture (identity and settings, time, tokens and cost, approvals and
interventions, transcript, grader results and report accuracy), who
records each item, and the file each goes in. Time and tokens come from
the tool, not from the agent's own report.

### Token limit, human collaboration and the operator

- **Token limit for this task: 400,000 tokens.** Token efficiency (10%)
  is 100 up to 200,000 tokens, falling to 0 at 400,000. Tokens come from the
  tool's own usage record (RUN-RECORD.md section 3).
- **Human collaboration (10%):** log every message to the measured agent
  after the initial prompt in `interventions.json`, whether it came from a
  person or an AI operator. A second team member rates them in
  `h-review.json`; only avoidable clarifications and corrections cost
  points (25 each). Without `h-review.json` the run has no H score.
- **Operator:** record who ran the benchmark in `operator.json`, a person or
  an AI session (tool, model, who supervised it), with what the operator
  knew, setup attempts and time. This is not part of the agent's score.


Before coding, record:

- Participant, date, tool, and run ID.
- Harness version and interface: IDE, interactive CLI, or headless CLI.
- Selected model and reasoning/effort mode.
- OS, Node, and npm versions.
- Approval and sandbox settings.
- Available integrations, MCP servers, and automatically loaded instructions.
- Memory settings, and how memory was disabled.
- Starting commit and agreed evaluator commit.
- Previous operator knowledge of the task, graders, or reference.

Use a fresh agent session. Disable optional extra integrations where
possible and disclose anything that remains available.

Unknown measurements or settings must be reported as unknown.

This experiment compares tool/model workflows. It does not isolate harness
quality when models, environments, or settings differ.

The commands below use Windows PowerShell. Other platforms may use
equivalent commands and must record the differences.

### Start fresh: no memory, no carried-over context

Every attempt must start with no memory of earlier sessions, tasks, or
runs. Before launching the agent:

- **Turn off memory** and any import of memory from other agents.
- **Turn off or disclose global instruction files** that load into every
  session, such as `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, Copilot
  custom instructions, or Antigravity rules. If one cannot be turned off,
  record its contents in the evidence.
- **Do not resume, fork, or reuse a session**, and do not paste in earlier
  conversation.
- **Turn off plugins, skills, hooks, MCP servers, and connectors** that the
  task does not need.

Tool-specific settings:

| Tool | How to start fresh |
|---|---|
| Codex CLI | Use Codex 0.163 or later (older versions reject `gpt-6.1-sol` with a ChatGPT login). Pass `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, `--disable memories`, `--disable external_agent_memory_import` and `-c project_doc_max_bytes=0`, and unset any `CODEX_*` environment variables (see section 7). Don't use an empty `CODEX_HOME`: the Windows elevated sandbox keeps its setup in `~/.codex`, and without it every command hangs |
| Claude Code | New session; turn off auto-memory; move `~/.claude/CLAUDE.md` aside or record it; turn off plugins and MCP servers that the task does not need |
| Copilot | New chat; turn off Copilot memory and custom instructions, or record them |
| Antigravity | New agent conversation; turn off knowledge items and memory; record any workspace or global rules |

## 3. Create the isolated coding snapshot

Start in the Microsoft-Capstone repository directory.

```powershell
git fetch origin
git status --short

$repoRoot = (Get-Location).Path
$parentDirectory = Split-Path $repoRoot -Parent

# The agreed commit, used for both the snapshot and the graders.
$baseline = '0de244020fc0aeb140e2632d7ff75afbe201e30f'

# Change this for your assigned tool and attempt.
$runId = 'antigravity-bugfix-run01'

$runRoot = Join-Path $parentDirectory $runId
$runZip = Join-Path $parentDirectory "$runId.zip"
$evidenceDir = Join-Path $parentDirectory "$runId-evidence"

if ((Test-Path $runRoot) -or
    (Test-Path $runZip) -or
    (Test-Path $evidenceDir)) {
    throw 'Choose a new run ID; do not overwrite an existing attempt.'
}

New-Item -ItemType Directory -Path $evidenceDir | Out-Null

git archive --format=zip --output=$runZip $baseline app pipeline/tasks/004-fix-update-validation.md
if ($LASTEXITCODE -ne 0) { throw 'Baseline export failed.' }

Expand-Archive -LiteralPath $runZip -DestinationPath $runRoot
$runApp = Join-Path $runRoot 'app'
```

Use the appropriate run ID:

- antigravity-bugfix-run01
- copilot-bugfix-run01
- claude-bugfix-run01
- codex-bugfix-run01

The snapshot contains app/ and the task file, without Git metadata.

## 4. Extract the agreed evaluator version separately

From the repository directory:

```powershell
# The graders come from the same agreed commit as the snapshot.
$protocolCommit = $baseline

git cat-file -e "$($protocolCommit)^{commit}"
if ($LASTEXITCODE -ne 0) { throw 'Agreed commit not found; run git fetch origin.' }
```

Do not use the newest commit of `benchmark-protocol-v3-bugfix` for grading. Later commits
change documentation only, but every run must record and use the same
agreed commit. Do not silently use different evaluator versions.

Then run:

```powershell
$graderExport = Join-Path $evidenceDir 'grader-source'
$graderZip = Join-Path $evidenceDir 'grader-source.zip'

git archive --format=zip --output=$graderZip $protocolCommit benchmark-results/protocol/update-bugfix
if ($LASTEXITCODE -ne 0) { throw 'Evaluator export failed.' }

Expand-Archive -LiteralPath $graderZip -DestinationPath $graderExport

$graderDir = Join-Path $graderExport 'benchmark-results\protocol\update-bugfix'

@(
    "baseline_commit=$baseline"
    "protocol_commit=$protocolCommit"
) | Set-Content (Join-Path $evidenceDir 'source-commits.txt')

Get-ChildItem $graderDir -File |
    Get-FileHash -Algorithm SHA256 |
    Export-Csv (Join-Path $evidenceDir 'grader-hashes.csv') -NoTypeInformation
```

Archive extraction avoids working-tree line-ending conversion. Compare
grader hashes across participants before measured coding. Investigate any
differences before proceeding.

The exported grader folder also contains `reference/`, `ACCEPTANCE.md`,
and `evidence/`. They stay in the evidence folder, outside $runRoot.
Never copy them into the agent's workspace.

## 5. Install dependencies

Install the application dependencies and check its existing tests:

```powershell
Push-Location $runApp
try {
    npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw 'Application install failed.' }

    npm.cmd test
    if ($LASTEXITCODE -ne 0) { throw 'Baseline local tests failed.' }
}
finally {
    Pop-Location
}
```

Expected baseline local result: 9 passed, 0 failed.

Install evaluator dependencies outside the coding workspace:

```powershell
Push-Location $graderDir
try {
    npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw 'Evaluator install failed.' }

    npx.cmd playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw 'Browser install failed.' }

    npx.cmd playwright --version
}
finally {
    Pop-Location
}
```

Record installation outcomes and versions. Setup time is separate from
measured coding time.

Optional baseline check: grading the unchanged app (section 9) should give
API 5 passed / 19 failed and browser 2 passed / 2 failed. If it does not,
stop and investigate before running the agent.

## 6. Record the pre-agent file manifest

After installation and before launching the agent:

```powershell
function Get-RunManifest {
    Get-ChildItem -LiteralPath $runRoot -Recurse -File -Force |
        Where-Object {
            $_.FullName -notmatch '[\\/]node_modules([\\/]|$)'
        } |
        ForEach-Object {
            [PSCustomObject]@{
                Path = $_.FullName.Substring($runRoot.Length + 1)
                SHA256 = (
                    Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256
                ).Hash
            }
        } |
        Sort-Object Path
}

Get-RunManifest |
    Export-Csv (Join-Path $evidenceDir 'before-files.csv') -NoTypeInformation
```

This includes hidden files but excludes installed node_modules. Check
added or empty directories separately during scope review.

## 7. Run the assigned harness

Open only $runRoot in the assigned harness, using a fresh session with
memory turned off (see section 2).

Start timing immediately before submitting the prompt. Stop timing when
the final report is delivered.

Record the timing method. Include approval waiting in total elapsed time,
and record approval waiting separately when evidence allows.

Use this exact initial prompt:

```
Read pipeline/tasks/004-fix-update-validation.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.
```

Preserve:

- Exact prompt and final report.
- Conversation or session export.
- Permission requests, approvals, and denials.
- Operator assistance and setup problems.
- Timing evidence.

Give no coding hints during the original attempt. Record necessary setup
assistance separately.

### Example: headless Codex CLI, starting fresh

Use Codex CLI 0.163 or later. The npm package can lag behind; the copy
installed with the Codex desktop app is under
`%LOCALAPPDATA%\OpenAI\Codex\bin\<build>\codex.exe`. Record the version.

```powershell
$codex = 'codex'   # or the full path to a 0.163+ codex.exe
& $codex --version | Set-Content (Join-Path $evidenceDir 'codex-version.txt')

$prompt = @'
Read pipeline/tasks/004-fix-update-validation.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.
'@
$prompt | Set-Content (Join-Path $evidenceDir 'initial-prompt.txt')

# Start fresh: drop inherited Codex session variables for this process.
Get-ChildItem Env: | Where-Object Name -like 'CODEX_*' |
    ForEach-Object { Remove-Item "Env:\$($_.Name)" }

$timer = [Diagnostics.Stopwatch]::StartNew()
$prompt | & $codex exec `
    --model gpt-6.1-sol `
    -c 'model_reasoning_effort="low"' `
    --sandbox workspace-write `
    -c 'approval_policy="never"' `
    -c 'windows.sandbox="elevated"' `
    -c 'project_doc_max_bytes=0' `
    --ignore-user-config --ignore-rules --ephemeral `
    --disable memories --disable external_agent_memory_import `
    --skip-git-repo-check --json `
    -C $runRoot `
    -o (Join-Path $evidenceDir 'final-report.txt') `
    - > (Join-Path $evidenceDir 'transcript.jsonl')
$timer.Stop()
"elapsed_seconds=$($timer.Elapsed.TotalSeconds)" |
    Set-Content (Join-Path $evidenceDir 'timing.txt')
```

What each fresh-start flag does:

- `--ephemeral`: doesn't save the session, so nothing can be resumed later.
- `--disable memories` and `--disable external_agent_memory_import`: no
  memory and no memory imported from other agents.
- `--ignore-user-config` and `--ignore-rules`: skip your `config.toml`
  (plugins, MCP servers, profiles) and your execution rules.
- `-c project_doc_max_bytes=0`: don't load `AGENTS.md` instruction files.
  Also record whether `~/.codex/AGENTS.md` exists and what it contains.

Your sign-in still comes from `~/.codex`. Do not point `CODEX_HOME` at an
empty folder: the Windows elevated sandbox keeps its setup in `~/.codex`,
and without it every shell command hangs.

Usage is in the last `turn.completed` event of `transcript.jsonl`.

## 8. Preserve original output before feedback

From the operator's PowerShell terminal:

```powershell
$originalDir = Join-Path $evidenceDir 'original'
New-Item -ItemType Directory -Path $originalDir | Out-Null

Copy-Item -LiteralPath (Join-Path $runApp 'server.js') -Destination $originalDir
Copy-Item -LiteralPath (Join-Path $runApp 'test.js') -Destination $originalDir
Copy-Item -LiteralPath (Join-Path $runApp 'public\index.html') -Destination $originalDir

Get-RunManifest |
    Export-Csv (Join-Path $evidenceDir 'original-after-files.csv') -NoTypeInformation

Compare-Object `
    (Import-Csv (Join-Path $evidenceDir 'before-files.csv')) `
    (Import-Csv (Join-Path $evidenceDir 'original-after-files.csv')) `
    -Property Path, SHA256 |
    Out-File (Join-Path $evidenceDir 'original-scope-diff.txt')
```

Review changes, additions, and removals.

Only these application files may change:

- app/server.js
- app/test.js
- app/public/index.html

Also check that:

- All 9 existing tests are preserved.
- New local tests cover API-01 to API-04.
- The DELETE endpoint and the title-validation rules are unchanged.
- No package files or dependencies changed.
- The agent's final report names the cause of each reported bug.

Passing tests alone does not establish scope compliance.

## 9. Independently grade the original output

Run grading outside the agent session.

```powershell
Push-Location $runApp
try {
    npm.cmd test 2>&1 |
        Tee-Object (Join-Path $evidenceDir 'original-local-tests.txt')
    $localExit = $LASTEXITCODE
}
finally {
    Pop-Location
}

$env:BENCHMARK_APP_DIR = $runApp
$env:EVIDENCE_DIR = Join-Path $evidenceDir 'original-screenshots'
New-Item -ItemType Directory -Path $env:EVIDENCE_DIR | Out-Null
Push-Location $graderDir

try {
    node --test .\update-bugfix-api.test.cjs 2>&1 |
        Tee-Object (Join-Path $evidenceDir 'original-api-tests.txt')
    $apiExit = $LASTEXITCODE

    npx.cmd playwright test --config=playwright.config.cjs 2>&1 |
        Tee-Object (Join-Path $evidenceDir 'original-browser-tests.txt')
    $browserExit = $LASTEXITCODE

    @(
        "local_exit=$localExit"
        "api_exit=$apiExit"
        "browser_exit=$browserExit"
    ) | Set-Content (Join-Path $evidenceDir 'original-test-exits.txt')

    Copy-Item .\browser-report `
        (Join-Path $evidenceDir 'original-browser-report') -Recurse

    if (Test-Path .\browser-test-results) {
        Copy-Item .\browser-test-results `
            (Join-Path $evidenceDir 'original-browser-test-results') -Recurse
    }
}
finally {
    Pop-Location
    Remove-Item Env:\BENCHMARK_APP_DIR -ErrorAction SilentlyContinue
    Remove-Item Env:\EVIDENCE_DIR -ErrorAction SilentlyContinue
}
```

A compliant output is expected to pass:

- All preserved and newly added local application tests (9 or more).
- 24 independent API tests. The Node runner counts subtests, so 10
  top-level tests report as 24.
- 4 independent browser tests.

Keep suite counts separate. They are not distinct requirement counts.

Also record which bugs were fully fixed, using the table in
[ACCEPTANCE.md](ACCEPTANCE.md):

| Bug | Fully fixed when these pass |
|---|---|
| B1 (string "false" counts as true) | both API-01 tests |
| B2 (malformed ids accepted) | API-02 "malformed ids are rejected" |
| B3 (non-object body accepted) | API-03 |
| B4 (save failures invisible) | both UI-02/UI-03 browser tests |

Review whether error messages explain the failure. Distinguish
application defects from evaluator or setup errors.

The evaluators start the app on an available port. There is no need to
manually launch server.js for grading.

### Code quality (20% of the score)

Code quality is graded with `benchmark-results/protocol/code-quality` on
the `results/all-runs` branch, not with the files in this folder. It
compares the agent's three files with the starting code on four checks,
25 points each: no new ESLint violations, no new functions above
cyclomatic complexity 10, no new duplicated lines, and a test-suite
runtime of at most 1.2 x the starting code's. The task file tells the
agent about these checks.

After adding your run to `results/all-runs` (section 11), run from that
folder on the `results/all-runs` branch:

```bash
npm ci
```
```bash
node score-runs.mjs
```

It writes `quality.json` into your run folder and updates `scores.md`.
Commit both with your run. The dashboard reads `quality.json`.

## 10. Record corrections separately

If an application requirement fails:

1. Preserve the original files and grading evidence first.
2. Record a corrective prompt identifying the failed requirement and
   observed behavior, without providing a reference solution.
3. Measure correction time separately.
4. Record correction approvals and human assistance separately.
5. Preserve corrected files and a new manifest under separate names.
6. Repeat grading and save corrected logs and browser reports.

Never overwrite original artifacts.

Verification reruns of preserved output are not new coding attempts.

If an evaluator defect is discovered, record it, agree on a new evaluator
version, and regrade all preserved outputs consistently.

## 11. Publish results separately

After coding and independent grading, publish evidence on a separate
results branch, `results/<tool>-bugfix-run01`. Do not modify
benchmark-protocol-v3-bugfix.

Suggested results folder:

    benchmark-results/<tool>/bugfix-run01/

Include everything on the [RUN-RECORD.md](RUN-RECORD.md) checklist, and
tick its "Final check" list before publishing. In particular:

- README describing configuration, results, and limitations.
- Baseline and evaluator commit IDs.
- Grader hashes.
- Memory settings and how the session was started fresh.
- Original source snapshots and any corrected snapshots.
- Before/after manifests and scope review.
- Local, API, and browser logs with exit codes.
- Which of B1 to B4 were fully fixed.
- Browser reports, failure traces, and screenshots.
- Exact prompts and conversation evidence.
- Timing, approvals, denials, and human assistance.
- Token usage or cost if available; otherwise state unavailable.

Do not commit node_modules, credentials, or unrelated personal data. Publication
happens after the measured coding attempt.

### Also add your run to the results/all-runs branch

Your `results/<tool>-bugfix-run01` branch is the full original record.
Every run must **also** be added to the shared `results/all-runs`
branch, which collects all tools and tasks in one place for analysis.

Copy only the files needed to analyse the run:

- README, the initial prompt, and the final report.
- Local, API, and browser test logs, and the exit-code files.
- Timing, token usage, approval notes, environment, and run
  configuration.
- Scope review and scope diff.
- The original source snapshot (`original/`) and any corrected
  snapshots.

Leave out raw transcripts and event logs, setup and install logs, file
manifests, hashes, grader copies, and Playwright HTML reports and traces.
They stay on your own results branch.

From the repository directory, after pushing your own results branch:

```powershell
git fetch origin
git switch results/all-runs
git pull --ff-only origin results/all-runs

# Copy the files listed above from your evidence folder into:
#   benchmark-results/<tool>/bugfix-run01/

git add benchmark-results/<tool>/bugfix-run01
git commit -m "Add <tool> bugfix-run01 to all-runs"

# Name the branch explicitly. A plain "git push" can send the commit to
# the wrong branch if the local branch tracks master.
git push origin results/all-runs:results/all-runs
```

If the push is rejected because someone else pushed first, run
`git pull --rebase origin results/all-runs` and push again. Also add the
run to the results table in that branch's root README.md.

## 12. Compare outcomes

Compare:

- Requirement compliance and regressions.
- Bugs fully fixed (B1 to B4): fixing only the reported symptom
  scores lower than also finding the related id and body bugs.
- Allowed-file adherence and test preservation.
- Accuracy of the agent's explanation of each bug's cause.
- Prompt-to-final elapsed time and its measurement method.
- Permission requests and denied actions.
- Human corrections or other assistance.
- Accuracy of the agent's final report.

Disclose model, environment, configuration, and evidence differences.
One attempt on one task does not establish a general tool winner.

See [VALIDATION.md](VALIDATION.md) for evaluator validation results and
limitations, and [ACCEPTANCE.md](ACCEPTANCE.md) for the criteria with
before and after evidence.
