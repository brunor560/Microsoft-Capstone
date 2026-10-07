# DELETE endpoint pilot: shared team procedure

## What to push now

Keep `benchmark-start-v1` at commit `be98d692807da26dac3c3a720d4d5cf157e9717d`. It is already pushed. Do not copy an agent solution onto this branch or merge it into the starting app before the comparison.

Share the starting commit, this procedure, and grading files with the team. Store original and corrected outputs as separate result artifacts. After grading, those artifacts and reports can go on a separate results branch/PR, preferably under `benchmark-results/<tool>/run01/`, with no node_modules. Do not put reference solutions into the agent's workspace. No push is required before the others can start.

## Participants

| Person | Tool | Run folder |
|---|---|---|
| Kapil | Antigravity | antigravity-delete-run01 |
| Ross | GitHub Copilot | copilot-delete-run01 |
| Bruno | Claude Code | claude-delete-run01 |
| Joseph | Codex | codex-delete-run01 |

Kapil's run01 is already complete. Do not reset or overwrite it. The steps below create fresh runs for the others. Windows PowerShell commands are supplied; a different OS must use equivalent commands and record the difference.

## 1. Agree on the conditions before starting

- Use the exact commit above, the unchanged task file, and the exact initial prompt below.
- Record tool version, selected model (or automatic model selection), mode, OS, Node/npm versions, approval settings, and enabled integrations. Each person uses their assigned tool's coding agent that can edit files and run commands.
- Use the same Node/npm versions where available: Kapil used Node v24.21.0 and npm 11.19.0. Record any differences; do not hide them.
- Start a fresh conversation in a fresh run folder. Use no extra instructions, custom skills, MCP tools, web lookups, or reference implementations for this coding pilot. Record any automatically loaded configuration or native tool differences.
- Keep approvals per command where supported. Count approval prompts separately from feedback containing coding hints. If permissions differ across tools, record that difference.
- Measure wall-clock time from sending the prompt to the final report, including approval waiting. Record avoidable operator delays separately. Test duration in milliseconds is not coding time.
- Grade the initial output before giving corrective feedback. Preserve both stages.
- This compares native tool/model workflows on one small task. It does not isolate model quality or establish a general winner. Skills/MCP, PR/CI, and deployment remain later project stages.

## 2. Obtain a fresh snapshot

In a terminal, go to the folder where you keep project folders. If you already have the repository, use that copy and run `git fetch origin`; do not overwrite local changes. Otherwise:

```powershell
git clone https://github.com/brunor560/Microsoft-Capstone.git
cd Microsoft-Capstone
git fetch origin
```

In the repo directory verify the starting commit exists:

```powershell
git show --no-patch --oneline be98d692807da26dac3c3a720d4d5cf157e9717d
```

Choose the run name for your tool. Ross uses the example below; Bruno changes only the name to `claude-delete-run01`, Joseph to `codex-delete-run01`.

```powershell
$runName = 'copilot-delete-run01'
git archive --format=zip --output="..\$runName.zip" be98d692807da26dac3c3a720d4d5cf157e9717d app pipeline/tasks/001-add-delete-endpoint.md
Expand-Archive "..\$runName.zip" -DestinationPath "..\$runName"
cd "..\$runName\app"
node --version
npm --version
npm ci
npm test
```

Use a new run name if the destination already exists. Do not use `-Force` to overwrite a past run. Expected baseline: four local tests pass. Resolve installation/setup errors before timing the agent.

The ZIP snapshot intentionally has no Git metadata. A tool reporting that Git commands cannot operate in it should disclose that limitation; do not initialize Git halfway through a measured attempt.

## 3. Prepare grading outside the agent workspace

Kapil shares the original `delete-acceptance.test.cjs` file. Everyone places it in a sibling `benchmark-grading` directory, outside the run folder.

Expected layout:

- Microsoft-Capstone/
- copilot-delete-run01/ (or your tool's run name)
- benchmark-grading/delete-acceptance.test.cjs
- benchmark-grading/delete-leading-zero.test.cjs (created below)

Verify the original grader hash from your run's `app` directory:

```powershell
Get-FileHash ..\..\benchmark-grading\delete-acceptance.test.cjs -Algorithm SHA256
```

Expected SHA256:

`A457CB6ABACD3F46C65DA02579AC09C16EAAB8D4BA7F608A998078A427ABD947`

Stop if it differs until the team reconciles the file. Leave this nine-test suite unchanged. A missing DELETE route can return 404 and incidentally pass its missing-ID test; the baseline's two passing tests do not mean DELETE is implemented.

Kapil's pilot revealed a coverage gap: leading-zero IDs are valid under the task's existing definition. Add the following separate supplemental test as `benchmark-grading/delete-leading-zero.test.cjs`. Share exactly the same file with everyone. This is a grading addition discovered during the pilot, not a change to the task. Record it separately and apply it to every preserved original attempt as well as corrections.

```javascript
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the run app directory');
}
const app = require(path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js'));

test('Leading-zero ID deletes only its target; zero remains invalid', async () => {
  let server;
  try {
    await new Promise((resolve, reject) => {
      server = app.listen(0, '127.0.0.1', resolve);
      server.once('error', reject);
    });
    const base = `http://127.0.0.1:${server.address().port}/api/todos`;
    const request = (suffix, options = {}) => fetch(base + suffix, {
      ...options, signal: AbortSignal.timeout(5000)
    });
    const list = async () => {
      const response = await request('');
      assert.equal(response.status, 200);
      return response.json();
    };
    const create = await request('', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'Supplemental leading-zero target' })
    });
    assert.equal(create.status, 201);
    const target = await create.json();
    assert.ok(Number.isSafeInteger(target.id) && target.id > 0);
    const before = await list();
    const deleted = await request(`/0${target.id}`, { method: 'DELETE' });
    assert.equal(deleted.status, 204);
    assert.equal(await deleted.text(), '');
    const expected = before.filter(todo => todo.id !== target.id);
    assert.deepEqual(await list(), expected);
    const repeated = await request(`/0${target.id}`, { method: 'DELETE' });
    assert.equal(repeated.status, 404);
    assert.deepEqual(await list(), expected);
    const zero = await request('/00', { method: 'DELETE' });
    assert.equal(zero.status, 400);
    assert.deepEqual(await list(), expected);
  } finally {
    if (server && server.listening) {
      await new Promise((resolve, reject) => {
        server.close(error => error ? reject(error) : resolve());
      });
    }
  }
});
```

Validate this supplemental file against the reference copy (passes) and Kapil's preserved original implementation (fails) before using it as shared grading evidence. Keep the reference copy outside every agent workspace. Kapil's earlier direct `/01` check already demonstrated the defect, but this supplemental file is a new test and needs its own validation.

## 4. Capture the starting files and grading baseline

From the fresh run's `app` directory:

```powershell
$runRoot = (Resolve-Path ..).Path
$evidenceDir = Join-Path (Resolve-Path ..\..\benchmark-grading).Path $runName
New-Item -ItemType Directory -Path $evidenceDir
Get-ChildItem $runRoot -Recurse -File -Force |
  Where-Object { $_.FullName -notmatch '[\\/]node_modules[\\/]' } |
  ForEach-Object {
    [PSCustomObject]@{
      Path = $_.FullName.Substring($runRoot.Length + 1)
      Hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    }
  } | Export-Csv (Join-Path $evidenceDir 'before-files.csv') -NoTypeInformation
```

Keep this PowerShell session open so `$runName`, `$runRoot`, and `$evidenceDir` remain available. If it is reopened, set them again to the same run paths.

Run baseline grading with the agent closed:

```powershell
$env:BENCHMARK_APP_DIR = (Get-Location).Path
node --test ..\..\benchmark-grading\delete-acceptance.test.cjs 2>&1 | Tee-Object (Join-Path $evidenceDir 'baseline-acceptance.txt')
node --test ..\..\benchmark-grading\delete-leading-zero.test.cjs 2>&1 | Tee-Object (Join-Path $evidenceDir 'baseline-supplemental.txt')
Remove-Item Env:\BENCHMARK_APP_DIR
```

Expected: original grader 2 pass / 7 fail; supplemental 1 fail. These failures are intentional because DELETE is absent.

## 5. Open the assigned coding tool

Open only the run root (for example `copilot-delete-run01`), not the parent `Code Stuff` folder, main repository, or grading folder.

- Ross: use GitHub Copilot's coding agent in this workspace.
- Bruno: use Claude Code with this run root as its working directory.
- Joseph: use Codex with this run root as its workspace/working directory.
- Start a new conversation. Record the visible model/mode before sending.
- If a tool cannot operate without a Git repository, stop and report the setup limitation. Agree on a uniform revised setup for all tools rather than changing only one measured run.

## 6. Submit the exact same initial prompt

Start your stopwatch when sending this text:

```text
Read pipeline/tasks/001-add-delete-endpoint.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.
```

Do not mention the leading-zero defect or suggest implementation details during the initial attempt. Approve only commands within the task's permitted scope; keep the settings recorded above. Count each approval. If a clarification or coding hint becomes necessary, retain its exact text and count it as human intervention.

Stop the stopwatch when the agent finishes its final report. Save screenshots or an available transcript of the prompt, actions, errors, approvals, and final report. Do not substitute the agent UI's rounded duration for your stopwatch without labeling it approximate. Do not manually edit the output.

## 7. Preserve the initial output before grading or correction

From the same run's `app` terminal:

```powershell
Copy-Item .\server.js (Join-Path $evidenceDir 'original-server.js')
Copy-Item .\test.js (Join-Path $evidenceDir 'original-test.js')
npm test 2>&1 | Tee-Object (Join-Path $evidenceDir 'original-local-tests.txt')
$env:BENCHMARK_APP_DIR = (Get-Location).Path
node --test ..\..\benchmark-grading\delete-acceptance.test.cjs 2>&1 | Tee-Object (Join-Path $evidenceDir 'original-acceptance.txt')
node --test ..\..\benchmark-grading\delete-leading-zero.test.cjs 2>&1 | Tee-Object (Join-Path $evidenceDir 'original-supplemental.txt')
Remove-Item Env:\BENCHMARK_APP_DIR
```

Use different filenames for corrections; never overwrite these originals. Local and independent test counts may differ because they are separate suites. Read the pass/fail totals and errors; do not rely on the agent's summary alone.

## 8. Check scope and review the requirements

Capture the post-run manifest using the same `Get-ChildItem` pipeline from step 4, changing the output filename to `after-files.csv`. Compare:

```powershell
Compare-Object (Import-Csv (Join-Path $evidenceDir 'before-files.csv')) (Import-Csv (Join-Path $evidenceDir 'after-files.csv')) -Property Path,Hash
```

Only `app/server.js` and `app/test.js` content should change. Investigate added/deleted files or changes elsewhere, including task/package/frontend files. Record tool-generated workspace metadata separately from application changes; it still needs disclosure under the strict two-file constraint.

Review GET/POST/PUT preservation, ID validation, 204 empty body, 404 missing/repeated deletion, unchanged remaining todos, and whether generated tests use the agreed expectations. Passing tests alone is not complete evidence of every requirement.

## 9. If the original attempt has a defect

First save and grade it as above. Then give feedback in the same conversation, start a separate correction timer, and preserve the exact feedback text.

For the same leading-zero defect, use exactly:

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

Use this only when it describes the actual failure; other defects need their actual evidence. Log different feedback explicitly. If the original passes the checks and review, no correction is needed.

Save corrected files as `corrected-server.js` and `corrected-test.js`, repeat step 7 with `corrected-` output filenames, and repeat scope review. Keep correction time/approvals separate from the original run. A correction is not a fresh independent attempt.

## 10. Report and compare

Each person records:

| Field | Value to record |
|---|---|
| Run ID, person, tool | e.g. copilot-delete-run01, Ross, GitHub Copilot |
| Starting commit | be98d692807da26dac3c3a720d4d5cf157e9717d |
| Model/mode/tool version | Actual values or unknown/automatic |
| OS, Node, npm | Actual versions |
| Permissions/integrations | Actual configuration and deviations |
| Original elapsed time | Stopwatch; disclose waiting and operator delays |
| Original approvals/hints | Separate counts and exact feedback |
| Local tests | Actual total/pass/fail |
| Independent original suite | Out of 9; saved transcript |
| Supplemental test | Out of 1; saved transcript |
| Requirement/scope review | Defects, unauthorized changes, unresolved errors |
| Correction stage | Feedback count, time, approvals, grading results |

Kapil's existing evidence: original agent-reported local 8/8; independent 9/9; direct `/01` supplemental check failed with 400. One feedback prompt produced agent-reported local 9/9; independent 9/9; direct `/01` check passed with 204. Correction had three observed approval prompts. UI times displayed about 6 minutes original and 4 minutes correction; use stopwatch times if captured. Do not relabel the direct check as the new supplemental test until that file has actually run.

For Chad, show the shared snapshot, before/after tests, original defect, correction, and team comparison. Explain that the supplemental check improved the grading procedure. Grade all preserved originals with it, and disclose that it was added after Kapil's pilot. Since the team now knows the discovered edge case, later runs are not fully blind even with unchanged prompts.

After this pilot, agree on several fresh tasks and repeated runs with grading frozen beforehand. Then compare the sponsor's broader skills/MCP and prompt-to-PR/CI/deployment workflows.
