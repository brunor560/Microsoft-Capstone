# DELETE endpoint pilot: shared team procedure

Follow these steps in order. This procedure reproduces Kapil's benchmark setup, task, grading and evidence collection using your assigned coding tool. AI-generated code, test counts, elapsed time and permission requests may differ. Those differences are the results to measure; do not try to force identical code or eight local tests.

## What comes from which branch?

| Source | Purpose | What to use |
|---|---|---|
| `benchmark-start-v1` | Starting application and task | Fixed commit `be98d692807da26dac3c3a720d4d5cf157e9717d` |
| `results/antigravity-delete-run01` | Shared evaluator tests and procedure | `benchmark-results/protocol/` |
| Your own results branch | Your evidence and report | `benchmark-results/<tool>/run01/` |

The protocol folder is intentionally absent from the baseline commit. Do not copy an agent's DELETE implementation into the baseline. Do not merge results into the starting application before the comparison.

## Participants

| Person | Assigned tool | Run name | Result folder |
|---|---|---|---|
| Ross | GitHub Copilot | `copilot-delete-run01` | `benchmark-results/copilot/run01/` |
| Bruno | Claude Code | `claude-delete-run01` | `benchmark-results/claude/run01/` |
| Joseph | Codex | `codex-delete-run01` | `benchmark-results/codex/run01/` |
| Kapil | Antigravity | `antigravity-delete-run01` | `benchmark-results/antigravity/run01/` |

Kapil's pilot already exists. Preserve it. A repeat must use a new run name and result folder.

## Before starting

- These commands are for **Windows PowerShell**. On another OS, use equivalent commands and record that difference.
- Have Git, Node.js, npm and your assigned coding tool available. Kapil used Node `v24.21.0` and npm `11.19.0`; use those versions where available and record any differences.
- Use a fresh agent conversation. Record the tool version, model, mode, approval settings and enabled integrations. Record unknown or automatic settings honestly.
- Add no custom skills, MCP tools, coding hints or reference implementations for this pilot. Disclose automatically loaded instructions or integrations.
- Keep the PowerShell session open. Later commands reuse variables defined below. If you close it, restore those variables before continuing.
- Resolve setup errors before timing the coding attempt. Do not overwrite previous runs.

## Step 1 — Open the main repository in PowerShell

If you already have the repository, open a terminal in its root directory: `Microsoft-Capstone`. Do not clone another copy unnecessarily.

If you do not have it, run these commands from the parent folder where you keep your projects:

```powershell
git clone https://github.com/brunor560/Microsoft-Capstone.git
cd Microsoft-Capstone
```

Now run:

```powershell
git status --short
git fetch origin
$repoRoot = (Get-Location).Path
$parentRoot = Split-Path $repoRoot -Parent
$baselineCommit = 'be98d692807da26dac3c3a720d4d5cf157e9717d'
$protocolRef = 'origin/results/antigravity-delete-run01'
git show --no-patch --oneline $baselineCommit
git ls-tree --name-only $protocolRef benchmark-results/protocol/
```

**Expected:** Git can find the baseline commit and list the protocol files from the results branch. Existing local changes do not prevent exporting snapshots, but do not discard them. You will need a clean repository before creating your publication branch in Step 13.

If Git cannot find the results branch, check that `git fetch origin` succeeded. If your clone fetches only one branch, fetch this branch explicitly:

```powershell
git fetch origin results/antigravity-delete-run01:refs/remotes/origin/results/antigravity-delete-run01
```

## Step 2 — Set your run name

Choose **one row** from the participants table. Change these two values to your assigned tool:

```powershell
$toolName = 'copilot'
$runName = 'copilot-delete-run01'
$runRoot = Join-Path $parentRoot $runName
$appDir = Join-Path $runRoot 'app'
$gradingRoot = Join-Path $parentRoot 'benchmark-grading'
$evidenceDir = Join-Path $gradingRoot $runName
```

For Bruno, use `claude` and `claude-delete-run01`. For Joseph, use `codex` and `codex-delete-run01`.

```powershell
if (Test-Path $runRoot) { throw 'Run folder already exists. Choose a new run name; do not overwrite it.' }
if (Test-Path $evidenceDir) { throw 'Evidence folder already exists. Choose a new run name; do not overwrite it.' }
```

## Step 3 — Export the starting app and task

Run from the main repository:

```powershell
$runZip = Join-Path $parentRoot ($runName + '.zip')
if (Test-Path $runZip) { throw 'Snapshot ZIP already exists. Choose a new run name.' }
git archive --format=zip --output=$runZip $baselineCommit app pipeline/tasks/001-add-delete-endpoint.md
if ($LASTEXITCODE -ne 0) { throw 'Baseline export failed.' }
Expand-Archive -LiteralPath $runZip -DestinationPath $runRoot
```

**Expected:** the new run folder contains `app/` and `pipeline/tasks/001-add-delete-endpoint.md`. It contains no results, graders, reference solution or Git metadata.

The archive deliberately has no `.git` directory. If your tool requires Git metadata, report that setup limitation before the measured run. Agree on a common revised setup rather than initializing Git halfway through one tool's attempt.

## Step 4 — Obtain both evaluator files from the results branch

You do **not** get the graders from `benchmark-start-v1` and do **not** recreate them from pasted code. Export the committed files from the results branch. This does not switch your current branch.

```powershell
Set-Location $repoRoot
$protocolCommit = (git rev-parse $protocolRef).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve the protocol branch.' }
$protocolExport = Join-Path $gradingRoot ('protocol-' + $runName)
$protocolZip = Join-Path $parentRoot ($runName + '-protocol.zip')
if (Test-Path $protocolExport) { throw 'Protocol export already exists.' }
if (Test-Path $protocolZip) { throw 'Protocol ZIP already exists.' }
New-Item -ItemType Directory -Path $gradingRoot -Force | Out-Null
git archive --format=zip --output=$protocolZip $protocolCommit benchmark-results/protocol
if ($LASTEXITCODE -ne 0) { throw 'Protocol export failed.' }
Expand-Archive -LiteralPath $protocolZip -DestinationPath $protocolExport
$graderDir = Join-Path $protocolExport 'benchmark-results/protocol'
$acceptanceFile = Join-Path $graderDir 'delete-acceptance.test.cjs'
$supplementalFile = Join-Path $graderDir 'delete-leading-zero.test.cjs'
if (!(Test-Path $acceptanceFile)) { throw 'Main evaluator file is missing.' }
if (!(Test-Path $supplementalFile)) { throw 'Supplemental evaluator file is missing.' }
New-Item -ItemType Directory -Path $evidenceDir | Out-Null
Get-FileHash -LiteralPath $acceptanceFile,$supplementalFile -Algorithm SHA256 |
  Format-List | Out-File (Join-Path $evidenceDir 'grader-hashes.txt')
@("baseline_commit=$baselineCommit", "protocol_commit=$protocolCommit") |
  Set-Content (Join-Path $evidenceDir 'source-commits.txt')
```

The resulting folders are siblings:

| Folder | Contents | Open in the coding tool? |
|---|---|---|
| `Microsoft-Capstone/` | Main repository | No, for the measured task |
| Your run folder | Starting app and task | **Yes, open only this folder** |
| `benchmark-grading/` | Evaluators and saved evidence | **No** |

**Before anyone starts:** agree on one protocol commit and matching hashes for both grader files. If the branch advances, use the agreed commit rather than silently changing graders between runs.

Kapil's original local acceptance file had SHA-256 `A457CB6ABACD3F46C65DA02579AC09C16EAAB8D4BA7F608A998078A427ABD947`. The Git-exported file can have a different byte hash because of line endings. A Git commit hash and a file SHA-256 are different identifiers. If hashes differ, reconcile the bytes and test contents with Kapil; do not change a recorded expected hash merely to make the check pass. Use the agreed committed files unchanged and document any line-ending-only difference from the historical pilot. Exporting the same Git commit avoids checkout line-ending conversions.

## Step 5 — Install dependencies and verify the starting app

```powershell
Set-Location $appDir
node --version
npm --version
npm ci
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
npm test 2>&1 | Tee-Object (Join-Path $evidenceDir 'baseline-local-tests.txt')
$baselineLocalExit = $LASTEXITCODE
if ($baselineLocalExit -ne 0) { throw 'Baseline local tests failed. Resolve setup before starting.' }
```

**Expected:** four application tests pass. DELETE is deliberately absent. Do not implement it yourself.

## Step 6 — Capture the file manifest and evaluator baseline

Define this helper once. It records every run file except installed dependencies:

```powershell
function Save-RunManifest {
  param([string]$Destination)
  Get-ChildItem -LiteralPath $runRoot -Recurse -File -Force |
    Where-Object { $_.FullName -notmatch '[\\/]node_modules[\\/]' } |
    ForEach-Object {
      [PSCustomObject]@{
        Path = $_.FullName.Substring($runRoot.Length + 1)
        Hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
      }
    } | Sort-Object Path | Export-Csv -LiteralPath $Destination -NoTypeInformation
}
Save-RunManifest (Join-Path $evidenceDir 'before-files.csv')
```

With the coding agent still closed, run both evaluators:

```powershell
$env:BENCHMARK_APP_DIR = $appDir
try {
  node --test $acceptanceFile 2>&1 | Tee-Object (Join-Path $evidenceDir 'baseline-acceptance.txt')
  $acceptanceExit = $LASTEXITCODE
  node --test $supplementalFile 2>&1 | Tee-Object (Join-Path $evidenceDir 'baseline-supplemental.txt')
  $supplementalExit = $LASTEXITCODE
  @("acceptance_exit=$acceptanceExit", "supplemental_exit=$supplementalExit") |
    Set-Content (Join-Path $evidenceDir 'baseline-evaluator-exits.txt')
} finally {
  Remove-Item Env:\BENCHMARK_APP_DIR -ErrorAction SilentlyContinue
}
```

**Expected:** main evaluator **2 pass / 7 fail**; supplemental evaluator **0 pass / 1 fail**. These failures demonstrate the unfinished baseline. A default 404 can incidentally pass the missing-ID check; that is not evidence that DELETE exists.

The team has already validated the supplemental check against a correct reference (pass) and Kapil's preserved original output (fail). Teammates do not need the reference solution in their coding workspace.

## Step 7 — Open your assigned harness and record its configuration

1. Open **only `$runRoot`** in Copilot, Claude Code or Codex. Do not open the parent folder, main repository or grading directory.
2. Start a new agent conversation that can edit code and run commands.
3. Record tool/version, selected model or automatic selection, mode, OS, Node/npm versions, permissions and enabled integrations in your report.
4. Use per-command approvals where supported. Disclose differences between tools. Approval prompts and corrective coding feedback are separate measures.
5. Ensure no grader, reference solution, previous agent answer or other run has been added to the workspace or conversation.

The folder boundary and prompt are procedural controls, not proof of operating-system isolation. Record any observed access outside the allowed workspace.

## Step 8 — Send this exact initial prompt and time the attempt

Start your stopwatch when submitting this text:

```text
Read pipeline/tasks/001-add-delete-endpoint.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.
```

- Do not mention the leading-zero defect or suggest code during the initial attempt.
- Approve only actions within the agreed task scope. Record each approval and any denied request.
- If you give clarification or a coding hint, save its exact text and record an intervention.
- Stop timing when the agent gives its final report. Include approval waiting in elapsed time; record avoidable operator delays separately.
- Save the conversation export if available, or screenshots showing the prompt, actions, approvals, errors and final report.
- Do not manually edit the solution. Do not use test-runtime milliseconds as coding time. Label approximate UI timing as approximate.

The task file contains the acceptance criteria. It permits changes only to `app/server.js` and `app/test.js`, preserves GET/POST/PUT, and requires DELETE behavior including 204, 404, invalid-ID 400 and unchanged remaining todos. Its valid-ID definition allows leading zeros representing a positive safe integer.

## Step 9 — Preserve the original output and independently grade it

First save the files; then run the tests. **Do this before sending corrective feedback.**

```powershell
Set-Location $appDir
Copy-Item -LiteralPath ./server.js -Destination (Join-Path $evidenceDir 'original-server.js')
Copy-Item -LiteralPath ./test.js -Destination (Join-Path $evidenceDir 'original-test.js')
Save-RunManifest (Join-Path $evidenceDir 'original-after-files.csv')
npm test 2>&1 | Tee-Object (Join-Path $evidenceDir 'original-local-tests.txt')
$localExit = $LASTEXITCODE
$env:BENCHMARK_APP_DIR = $appDir
try {
  node --test $acceptanceFile 2>&1 | Tee-Object (Join-Path $evidenceDir 'original-acceptance.txt')
  $acceptanceExit = $LASTEXITCODE
  node --test $supplementalFile 2>&1 | Tee-Object (Join-Path $evidenceDir 'original-supplemental.txt')
  $supplementalExit = $LASTEXITCODE
  @("local_exit=$localExit", "acceptance_exit=$acceptanceExit", "supplemental_exit=$supplementalExit") |
    Set-Content (Join-Path $evidenceDir 'original-test-exits.txt')
} finally {
  Remove-Item Env:\BENCHMARK_APP_DIR -ErrorAction SilentlyContinue
}
Compare-Object (Import-Csv (Join-Path $evidenceDir 'before-files.csv')) `
  (Import-Csv (Join-Path $evidenceDir 'original-after-files.csv')) -Property Path,Hash |
  Format-Table -AutoSize | Out-String |
  Set-Content (Join-Path $evidenceDir 'original-scope-diff.txt')
```

**Interpret each suite separately:**

| Suite | Meaning | Correct result |
|---|---|---|
| `npm test` | Existing plus agent-written application tests | All pass; count can vary |
| `delete-acceptance.test.cjs` | Independent original suite | 9 pass / 0 fail |
| `delete-leading-zero.test.cjs` | Independent supplemental suite | 1 pass / 0 fail |

There are ten top-level independent tests across two files. Preserve their separate results. Multiple assertions can exist within a single test, so test count is not requirement count. Passing all tests does not replace scope and code review.

Only the two permitted application files should change. Investigate every added/deleted/modified file, including hidden workspace metadata. Disclose tool-created metadata separately; do not silently ignore it under the strict two-file rule. Review that existing endpoints and tests remain intact and that generated tests do not encode incorrect requirements.

Do not overwrite original evidence on reruns. Use a new filename if you need another transcript. If unexpected files changed, preserve those files or a patch in a separate evidence subfolder so reviewers can inspect them.

## Step 10 — Correct defects only after recording the original result

If both graders and the scope/requirement review pass, record **no correction required** and go to Step 12.

If a defect exists, record the exact evidence and give a corrective prompt in the same conversation. Start a separate correction timer and count correction approvals separately. Use the following prompt **only if your implementation actually rejects valid leading-zero IDs**:

```text
A supplemental check found a requirement mismatch:

DELETE /api/todos/01 returned 400, but the task allows IDs containing
only decimal digits that represent a positive safe integer. Therefore,
01 is valid and should identify todo 1.

Correct the DELETE validation and the test that incorrectly classifies
01 as invalid. Add a regression test verifying successful deletion
using a leading-zero ID.

Keep zero, negative, non-digit, and unsafe-integer IDs invalid.
Preserve the other requirements and existing tests.

Modify only app/server.js and app/test.js.
Run npm test and report the actual results.
Do not access parent folders, grading files, or reference solutions.
Do not commit or push.
```

Confirm the `/01` observation before quoting it. If the supplemental test failed at another assertion, describe that actual failure instead. If the leading-zero target was dynamically created with another ID, report that tested ID accurately. Do not claim an agent-written test misclassifies `01` unless you inspected it. Other defects require evidence-specific feedback. Save every feedback prompt and report multiple correction rounds separately.

## Step 11 — Preserve and grade the correction

After the agent finishes its correction, stop the correction timer. Run:

```powershell
Set-Location $appDir
Copy-Item -LiteralPath ./server.js -Destination (Join-Path $evidenceDir 'corrected-server.js')
Copy-Item -LiteralPath ./test.js -Destination (Join-Path $evidenceDir 'corrected-test.js')
Save-RunManifest (Join-Path $evidenceDir 'corrected-after-files.csv')
npm test 2>&1 | Tee-Object (Join-Path $evidenceDir 'corrected-local-tests.txt')
$localExit = $LASTEXITCODE
$env:BENCHMARK_APP_DIR = $appDir
try {
  node --test $acceptanceFile 2>&1 | Tee-Object (Join-Path $evidenceDir 'corrected-acceptance.txt')
  $acceptanceExit = $LASTEXITCODE
  node --test $supplementalFile 2>&1 | Tee-Object (Join-Path $evidenceDir 'corrected-supplemental.txt')
  $supplementalExit = $LASTEXITCODE
  @("local_exit=$localExit", "acceptance_exit=$acceptanceExit", "supplemental_exit=$supplementalExit") |
    Set-Content (Join-Path $evidenceDir 'corrected-test-exits.txt')
} finally {
  Remove-Item Env:\BENCHMARK_APP_DIR -ErrorAction SilentlyContinue
}
Compare-Object (Import-Csv (Join-Path $evidenceDir 'before-files.csv')) `
  (Import-Csv (Join-Path $evidenceDir 'corrected-after-files.csv')) -Property Path,Hash |
  Format-Table -AutoSize | Out-String |
  Set-Content (Join-Path $evidenceDir 'corrected-scope-diff.txt')
```

Record all results, including unresolved failures. For another correction round, use new filenames such as `correction02-server.js` and `correction02-acceptance.txt`; do not overwrite any earlier stage. A correction is human-assisted continuation, not another independent first attempt.

## Step 12 — Write your results report

Create `README.md` inside `$evidenceDir`. Use the following structure and replace placeholders with actual observations. Use **not measured**, **unknown**, or **not applicable** where appropriate; do not invent values.

```markdown
# <Tool> DELETE pilot — <run name>

## Configuration
- Operator:
- Date:
- Harness and version:
- Model and mode:
- OS / Node / npm:
- Baseline commit: be98d692807da26dac3c3a720d4d5cf157e9717d
- Protocol commit:
- Grader hashes: see grader-hashes.txt
- Approval settings / integrations / automatically loaded instructions:
- Setup differences or errors:

## Original attempt
- Exact initial prompt: procedure Step 8; note any deviation.
- Elapsed time and measurement method:
- Approval requests / denied requests:
- Coding hints or clarifications (count and exact text):
- Agent-reported local results:
- Independently rerun local results:
- Main evaluator: __ / 9 passed; __ failed.
- Supplemental evaluator: __ / 1 passed; __ failed.
- Scope and requirement review:
- Defects and supporting evidence:

## Correction
- Required: yes / no.
- Exact feedback text, if any:
- Correction elapsed time and measurement method:
- Correction approvals / further feedback:
- Local results:
- Main evaluator results:
- Supplemental evaluator results:
- Scope review and unresolved problems:

## Evidence
- File manifests, source commits and grader hashes.
- Original files and test transcripts.
- Corrected files and transcripts, if applicable.
- Conversation export or screenshots.

## Interpretation and limitations
- What worked and what failed:
- Environment/model/configuration differences:
- Missing measurements:
- This is one task and one initial attempt, not proof of a general winner.
```

Save screenshots/conversation exports into the evidence folder, preferably in a `conversation/` subfolder. Review them for credentials before publication. Keep graders and reference implementations out of candidate workspaces even after the initial attempt.

Historical Antigravity evidence: original agent-reported local 8/8, independent main suite 9/9, direct `/01` check returned 400. One corrective prompt produced reported local 9/9, main suite 9/9 and direct `/01` 204. Do not relabel a direct check as a recorded run of the supplemental file. The supplemental file was separately validated against the reference and original implementation.

## Step 13 — Publish evidence on a separate results branch

The grading commands above do not commit or push. After reviewing your report, publish **evidence only** from the main repository. Do not replace its `app/` files with your solution.

```powershell
Set-Location $repoRoot
git status --short
```

**Continue only with a clean working tree.** If there are changes, preserve them first; do not reset or discard them. Use the baseline as the parent of your results branch so the comparison input remains clear:

```powershell
$resultBranch = 'results/' + $runName
git switch -c $resultBranch $baselineCommit
if ($LASTEXITCODE -ne 0) { throw 'Could not create results branch. Do not continue copying evidence.' }
$resultDir = Join-Path $repoRoot ('benchmark-results/' + $toolName + '/run01')
if (Test-Path $resultDir) { throw 'Result folder already exists. Do not overwrite it.' }
New-Item -ItemType Directory -Path $resultDir | Out-Null
Copy-Item -Path (Join-Path $evidenceDir '*') -Destination $resultDir -Recurse
git status --short
git add -- $resultDir
git diff --cached --stat
```

**Review before committing:** only your `benchmark-results/<tool>/run01/` evidence should be staged. No `node_modules`, secrets, reference solutions or changes to the starting app/task should appear. For repeat runs, change the destination to `run02` or another new identifier.

```powershell
git commit -m "Record DELETE pilot results and evidence"
if ($LASTEXITCODE -ne 0) { throw 'Commit failed.' }
git push -u origin $resultBranch
if ($LASTEXITCODE -ne 0) { throw 'Push failed. Keep the local evidence and report the error.' }
git status
```

Share the pushed branch link with the team. A pushed branch is available for review even before a PR is merged. Use the team's agreed integration branch for a PR; do not merge agent solutions into `benchmark-start-v1`.

## Completion checklist

- [ ] Same baseline commit and unchanged task/initial prompt.
- [ ] Agreed protocol commit and matching grader bytes recorded.
- [ ] Fresh run folder and conversation; configuration recorded.
- [ ] Four local baseline tests passed; evaluator baseline failures recorded.
- [ ] Original attempt preserved before feedback.
- [ ] Local suite, nine-test main evaluator and one-test supplement recorded separately.
- [ ] Scope and requirement review completed.
- [ ] Corrections separately timed, preserved and graded, if needed.
- [ ] README and evidence published on a separate results branch.

For Chad, demonstrate the fixed starting app, task requirements, harness activity, independent grading, any defect/correction, and the team comparison. This pilot evaluates native harness/model workflows. It does not isolate model quality, prove security, or complete skills/MCP, PR/CI and deployment evaluation. Because the team knows the discovered edge case, later pilot runs are not fully blind. The next campaign should use fresh tasks, repeated runs and grading frozen before any attempts.
