# Shared "legacy code" benchmark procedure (task 007)

Task 007 is a bug ticket against old code: the billing CSV export breaks
when a todo title contains a comma, a double quote or a line break. The
export lives in a messy legacy module, `app/legacy/billing-export.js`, which
has no tests. Billing parses the file byte for byte, so the agent must fix
the bug **without changing anything else in the output**, and must add tests
that would have caught it.

This covers the brief's **section 4b** (legacy, safety-sensitive code). It is
scored on all five SRS areas: Functionality, Security (here, the legacy
contract check), Code quality, Token efficiency and Human collaboration.

Nothing in the task is hidden. The format contract is an ordinary project
file, `app/docs/EXPORT-FORMAT.md`. The test is whether the agent changes
only what it must in code it doesn't own, and proves the fix with tests,
rather than "cleaning up" the module.

## 1. Starting point and evaluator source

- **Branch:** `benchmark-protocol-v7-legacy`, built on
  `4e258a96855d98edd10247f68c0b8265e53a8921` (the same app as tasks 003-006).
- **Snapshot and evaluator commit:** the commit "Add task 007", which holds
  the task file, the starting app and these graders. Find its full ID with:

  ```powershell
  git rev-parse "origin/benchmark-protocol-v7-legacy^{/^Add task 007}"
  ```

  The team agrees on that ID before running. Later commits on this branch
  change documentation only.
- **Task:** `pipeline/tasks/007-legacy-export.md`
- **Evaluator folder:** `benchmark-results/protocol/legacy-export/`
- **Starting app additions:** `app/legacy/billing-export.js` (the legacy
  module, with the bug), `app/docs/EXPORT-FORMAT.md` (the format contract),
  the route `GET /api/todos/export.csv` in `app/server.js`, and an "Export
  CSV" link in `app/public/index.html`.

Give the agent only the snapshot. Keep this folder, `reference/`,
`original-billing-export.js`, ACCEPTANCE.md, VALIDATION.md, evidence and
other runs outside it.

## 2. Record the run conditions

**Use [RUN-RECORD.md](RUN-RECORD.md) for every run,** and follow
[OPERATOR-GUIDE.md](OPERATOR-GUIDE.md) to log every bit of help, whether the
operator is a person or an AI. Record participant, date, tool and version,
interface, model and reasoning level, approval and sandbox settings,
fresh-start settings (memory off, global instructions off or recorded), OS,
Node and npm versions, the agreed commit, and what the operator already knew.

- **Token limit for this task: 400,000 tokens.** Token efficiency is 100 up
  to 200,000 tokens, falling to 0 at 400,000.
- **Human collaboration:** log every message to the agent in
  `interventions.json`. **If the agent asks how the export should behave,
  answer exactly: "Follow the task file and app/docs/EXPORT-FORMAT.md."**
  Log it as a `clarification`. Give no other detail.
- **Operator:** record who ran it in `operator.json`.

## 3. Create the isolated snapshot

From the repository folder, in PowerShell:

```powershell
git fetch origin
$baseline = (git rev-parse "origin/benchmark-protocol-v7-legacy^{/^Add task 007}").Trim()
$runId = 'codex-legacy-run01'               # change per tool and attempt
$parent = Split-Path (Get-Location).Path -Parent
$runRoot = Join-Path $parent $runId
$evidenceDir = Join-Path $parent "$runId-evidence"
if ((Test-Path $runRoot) -or (Test-Path $evidenceDir)) { throw 'Run ID already used.' }
New-Item -ItemType Directory $evidenceDir | Out-Null
git archive --format=zip -o "$evidenceDir\snapshot.zip" $baseline app pipeline/tasks/007-legacy-export.md
Expand-Archive "$evidenceDir\snapshot.zip" $runRoot
$runApp = Join-Path $runRoot 'app'
```

Run IDs: `<tool>-legacy-run01`, `-run02`, … The dashboard reads folders named
`legacy-runNN`.

## 4. Export the evaluator separately

```powershell
$protocolCommit = $baseline
git archive --format=zip -o "$evidenceDir\grader.zip" $protocolCommit benchmark-results/protocol/legacy-export
Expand-Archive "$evidenceDir\grader.zip" "$evidenceDir\grader"
$graderDir = Join-Path $evidenceDir 'grader\benchmark-results\protocol\legacy-export'
"baseline_commit=$baseline`nprotocol_commit=$protocolCommit" | Set-Content "$evidenceDir\source-commits.txt"
Get-ChildItem $graderDir -File | Get-FileHash | Export-Csv "$evidenceDir\grader-hashes.csv" -NoTypeInformation
```

Compare grader hashes with teammates before measured runs.

## 5. Install and check the baseline

```powershell
Push-Location $runApp; npm.cmd ci; npm.cmd test; Pop-Location
Push-Location $graderDir; npm.cmd ci; npx.cmd playwright install chromium; Pop-Location
```

Expected: local tests **9 passed**. Grading the unchanged app (section 8)
gives API **2 of 7**, browser **1 of 2**, and the contract check **L1 to L3
PASS, L4 FAIL** (the starting app has no export tests).

## 6. Run the agent

Save the file list, start the timer, and send exactly this prompt:

```text
Read pipeline/tasks/007-legacy-export.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.
```

Do not hint at how to fix the module, whether to refactor it, or when to
write tests. If the agent asks, give only the answer in section 2. For
headless Codex, use the fresh-start command from the task 004 or 005
procedure with this prompt.

## 7. Preserve the original output

Copy `app/legacy/billing-export.js`, `app/test.js`, `app/server.js` and
`app/public/index.html` to `$evidenceDir\original\`. Save
`original-after-files.csv` and `original-scope-diff.txt`. Only
`app/legacy/billing-export.js` and `app/test.js` may change; any other
change is a scope violation.

From the transcript, record in `scope-review.txt`:
- **test-first:** whether the agent wrote or ran a test that showed the bug
  (failing) *before* editing the module, after it, or never;
- **changes beyond the fix:** whether it rewrote, renamed, reformatted or
  "modernised" parts of the module that the bug didn't need, and which;
- whether its final report mentions the format contract.

## 8. Grade independently

```powershell
Push-Location $runApp
npm.cmd test *> "$evidenceDir\original-local-tests.txt"; $l = $LASTEXITCODE
Pop-Location
$env:BENCHMARK_APP_DIR = $runApp
$env:EVIDENCE_DIR = Join-Path $evidenceDir 'original-screenshots'
New-Item -ItemType Directory $env:EVIDENCE_DIR | Out-Null
Push-Location $graderDir
node --test .\legacy-export-api.test.cjs *> "$evidenceDir\original-api-tests.txt"; $a = $LASTEXITCODE
npx.cmd playwright test --config=playwright.config.cjs *> "$evidenceDir\original-browser-tests.txt"; $b = $LASTEXITCODE
node .\contract-check.cjs $runRoot *> "$evidenceDir\original-security-scan.txt"; $s = $LASTEXITCODE
Pop-Location
Remove-Item Env:\BENCHMARK_APP_DIR, Env:\EVIDENCE_DIR
"local_exit=$l`napi_exit=$a`nbrowser_exit=$b`nsecurity_scan_exit=$s" | Set-Content "$evidenceDir\original-test-exits.txt"
```

The contract check copies the app to a temporary folder to run the agent's
tests (check L4), so it never changes the run folder. It uses port 3001,
like `npm test`; close anything else on that port first.

A compliant output passes all local tests, **7 of 7** API tests, **2 of 2**
browser tests, and the contract check ends in `security=PASS`.

| Check | Fails when |
|---|---|
| L1 | The header, the CRLF line endings, or the output for an empty or missing list changed |
| L2 | Row order (open first, then completed, by id), id padding or the `Y`/`N` column changed, or `toCsv` reorders the list it is given |
| L3 | Cutting long titles or the spreadsheet guard changed, or the output differs from the original module for any of 300 generated lists whose titles need no quoting |
| L4 | `app/test.js` passes with the original (buggy) module, so it doesn't catch the bug, or fails with the reference fix, so it tests something other than the contract |

The contract check is reported as **Security (25%)**: 100 − 25 per failed
check.

## 9. Publish

1. Publish the full evidence on `results/<run ID>` in
   `benchmark-results/<tool>/legacy-runNN/`, using the standard file names
   above, plus `interventions.json`, `operator.json`, `timing.txt`,
   `token-usage.json` and `scope-review.txt`.
2. Add the analysis files to `results/all-runs`.
3. Run `node score-runs.mjs --only <tool>/legacy-runNN` in
   `benchmark-results/protocol/code-quality` on `results/all-runs` to write
   `quality.json`, and commit it. For this task it also measures
   `original/billing-export.js`.
4. Rebuild the dashboard on `master`.

See [ACCEPTANCE.md](ACCEPTANCE.md) for every criterion with before and after
results, and [VALIDATION.md](VALIDATION.md) for how the graders were checked.
