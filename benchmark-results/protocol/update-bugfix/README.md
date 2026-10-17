# Shared bug-fix benchmark procedure (task 004)

## 1. Starting point and evaluator source

- Starting branch: benchmark-start-v3-bugfix
- Starting app commit: 4e258a96855d98edd10247f68c0b8265e53a8921
  (the same app as the title-edit task)
- Start-branch commit, which adds the task file: record the full ID of
  `origin/benchmark-start-v3-bugfix` once the team agrees on it
- Task: pipeline/tasks/004-fix-update-validation.md
- Evaluator branch: benchmark-protocol-v3-bugfix
- Evaluator folder: benchmark-results/protocol/update-bugfix/

The starting application has Add, completion toggling, and Delete. Its
`PUT /api/todos/:id` endpoint and its status-toggle code contain the bugs
described in [ACCEPTANCE.md](ACCEPTANCE.md).

The team must agree on one published start commit and one published
evaluator commit before running. Record both full commit IDs for every
attempt.

Give the agent only the isolated app/task snapshot created below. Keep
graders, the reference solution (`reference/`), ACCEPTANCE.md, evidence,
and previous results outside it.

## 2. Record the run conditions

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

# Set this to the agreed full commit ID of benchmark-start-v3-bugfix.
$baseline = '<agreed start commit>'

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
$protocolCommit = (
    git rev-parse origin/benchmark-protocol-v3-bugfix
).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Evaluator commit lookup failed.' }

$protocolCommit
```

Compare the printed ID with the team's agreed evaluator commit. If the
branch has advanced, set $protocolCommit to the agreed full ID. Do not
silently use different evaluator versions.

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
benchmark-start-v3-bugfix.

Suggested results folder:

    benchmark-results/<tool>/bugfix-run01/

Include:

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
