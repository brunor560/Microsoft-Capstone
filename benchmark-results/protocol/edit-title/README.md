# Shared title-edit benchmark procedure

## 1. Starting point and evaluator source

- Starting branch: benchmark-start-v2-edit
- Fixed app/task commit: 522f9ada608b30f8801bfa4fac1a164cef3c647c
  (the same app as before; the task file now has the standard "What to
  report" section. The team must confirm it before new runs.)
- Task: pipeline/tasks/003-edit-todo-title.md
- Evaluator branch: benchmark-protocol-v2-edit
- Evaluator folder: benchmark-results/protocol/edit-title/

The starting application has Add, completion toggling, and Delete,
but no title-editing interface.

The team must agree on one published evaluator commit before running.
Record that full commit ID for every attempt.

Give the agent only the isolated app/task snapshot created below.
Keep graders, reference solutions, and previous results outside it.

### Earlier runs

The four `edit-run01` runs used commit
`4e258a96855d98edd10247f68c0b8265e53a8921`. It has the same app, but the
task file asked for a shorter final report. Compare grader results
directly; compare final reports with that difference in mind, and record
which commit each run used.

## 2. Record the run conditions

**Use [RUN-RECORD.md](RUN-RECORD.md) for every run.** It lists everything
to capture (identity and settings, time, tokens and cost, approvals and
interventions, transcript, grader results and report accuracy), who
records each item, and the file each goes in. Time and tokens come from
the tool, not from the agent's own report.


Before coding, record:

- Participant, date, tool, and run ID.
- Harness version and interface: IDE, interactive CLI, or headless CLI.
- Selected model and reasoning/effort mode.
- OS, Node, and npm versions.
- Approval and sandbox settings.
- Available integrations, MCP servers, and automatically loaded instructions.
- Starting app/task commit and agreed evaluator commit.
- Previous operator knowledge of the task, graders, or reference.

Use a fresh agent session. Disable optional extra integrations where
possible and disclose anything that remains available.

Unknown measurements or settings must be reported as unknown.

This experiment compares tool/model workflows. It does not isolate
harness quality when models, environments, or settings differ.

The commands below use Windows PowerShell. Other platforms may use
equivalent commands and must record the differences.

## 3. Create the isolated coding snapshot

Start in the Microsoft-Capstone repository directory.

```powershell
git fetch origin
git status --short

$repoRoot = (Get-Location).Path
$parentDirectory = Split-Path $repoRoot -Parent
$baseline = '522f9ada608b30f8801bfa4fac1a164cef3c647c'

# Change this for your assigned tool and attempt.
$runId = 'antigravity-edit-run01'

$runRoot = Join-Path $parentDirectory $runId
$runZip = Join-Path $parentDirectory "$runId.zip"
$evidenceDir = Join-Path $parentDirectory "$runId-evidence"

if ((Test-Path $runRoot) -or
    (Test-Path $runZip) -or
    (Test-Path $evidenceDir)) {
    throw 'Choose a new run ID; do not overwrite an existing attempt.'
}

New-Item -ItemType Directory -Path $evidenceDir | Out-Null

git archive --format=zip --output=$runZip $baseline app pipeline/tasks/003-edit-todo-title.md
if ($LASTEXITCODE -ne 0) { throw 'Baseline export failed.' }

Expand-Archive -LiteralPath $runZip -DestinationPath $runRoot
$runApp = Join-Path $runRoot 'app'
```

Use the appropriate run ID:

- antigravity-edit-run01
- copilot-edit-run01
- claude-edit-run01
- codex-edit-run01

The snapshot contains app/ and the task file, without Git metadata.

## 4. Extract the agreed evaluator version separately

From the repository directory:

```powershell
$protocolCommit = (
    git rev-parse origin/benchmark-protocol-v2-edit
).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Evaluator commit lookup failed.' }

$protocolCommit
```

Compare the printed ID with the team's agreed evaluator commit.
If the branch has advanced, set $protocolCommit to the agreed full ID.
Do not silently use different evaluator versions.

Then run:

```powershell
$graderExport = Join-Path $evidenceDir 'grader-source'
$graderZip = Join-Path $evidenceDir 'grader-source.zip'

git archive --format=zip --output=$graderZip $protocolCommit benchmark-results/protocol/edit-title
if ($LASTEXITCODE -ne 0) { throw 'Evaluator export failed.' }

Expand-Archive -LiteralPath $graderZip -DestinationPath $graderExport

$graderDir = Join-Path $graderExport 'benchmark-results\protocol\edit-title'

@(
    "baseline_commit=$baseline"
    "protocol_commit=$protocolCommit"
) | Set-Content (Join-Path $evidenceDir 'source-commits.txt')

Get-ChildItem $graderDir -File |
    Get-FileHash -Algorithm SHA256 |
    Export-Csv (Join-Path $evidenceDir 'grader-hashes.csv') -NoTypeInformation
```

Archive extraction avoids working-tree line-ending conversion.
Compare grader hashes across participants before measured coding.
Investigate any differences before proceeding.

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

Record installation outcomes and versions.
Setup time is separate from measured coding time.

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

This includes hidden files but excludes installed node_modules.
Check added or empty directories separately during scope review.

## 7. Run the assigned harness

Open only $runRoot in the assigned harness, using a fresh session.

Start timing immediately before submitting the prompt.
Stop timing when the final report is delivered.

Record the timing method. Include approval waiting in total elapsed
time, and record approval waiting separately when evidence allows.

Use this exact initial prompt:

```text
Read pipeline/tasks/003-edit-todo-title.md and complete the task
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

Give no coding hints during the original attempt.
Record necessary setup assistance separately.

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

Also review preservation of existing tests and addition of the required
local API tests. Passing tests alone does not establish scope compliance.

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
Push-Location $graderDir

try {
    node --test .\edit-title-api.test.cjs 2>&1 |
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

    Copy-Item .\browser-test-results `
        (Join-Path $evidenceDir 'original-browser-test-results') -Recurse
}
finally {
    Pop-Location
    Remove-Item Env:\BENCHMARK_APP_DIR -ErrorAction SilentlyContinue
}
```

A compliant output is expected to pass:

- All preserved and newly added local application tests.
- 12 independent API tests.
- 10 independent browser tests.

Keep suite counts separate. They are not distinct requirement counts.

Review whether error messages explain the failure.
Distinguish application defects from evaluator or setup errors.

The evaluators start the app on an available port.
There is no need to manually launch server.js for grading.

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

If an evaluator defect is discovered, record it, agree on a new
evaluator version, and regrade all preserved outputs consistently.

## 11. Publish results separately

After coding and independent grading, publish evidence on a separate
results branch. Do not modify benchmark-start-v2-edit.

Suggested results folder:

benchmark-results/<tool>/edit-run01/

Include everything on the [RUN-RECORD.md](RUN-RECORD.md) checklist, and
tick its "Final check" list before publishing. In particular:

- README describing configuration, results, and limitations.
- Baseline and evaluator commit IDs.
- Grader hashes.
- Original source snapshots and any corrected snapshots.
- Before/after manifests and scope review.
- Local, API, and browser logs with exit codes.
- Browser reports and failure traces.
- Exact prompts and conversation evidence.
- Timing, approvals, denials, and human assistance.
- Token usage or cost if available; otherwise state unavailable.

Do not commit node_modules, credentials, or unrelated personal data.
Publication happens after the measured coding attempt.

## 12. Compare outcomes

Compare:

- Requirement compliance and regressions.
- Allowed-file adherence and test preservation.
- Prompt-to-final elapsed time and its measurement method.
- Permission requests and denied actions.
- Human corrections or other assistance.
- Accuracy of the agent's final report.

Disclose model, environment, configuration, and evidence differences.
One attempt on one task does not establish a general tool winner.

See VALIDATION.md for evaluator validation results and limitations.