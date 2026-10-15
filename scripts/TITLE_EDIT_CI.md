# Title-edit correctness regrade

The workflow restores three preserved source files for each tool onto the same frozen app commit. It exports the API/browser evaluators and dependency lockfiles from the fixed protocol commit. Full commits are constants in `prepare_title_edit.py`; branch movement does not change the selected sources. Each tool runs in its own Ubuntu 24.04 job using Node 24.21.0 and the protocol's pinned Playwright/Chromium.

Checks are separate: the exact nine-test baseline suite against the restored implementation, that implementation's local test file, 12 independent API tests, and 10 independent browser tests. The baseline suite is copied beside server.js under a separate test filename to preserve its relative require unchanged. Its presence is verification instrumentation, not agent output. Running the baseline suite verifies regression behavior; it does not establish that the agent preserved all original test text or followed workspace rules.

Results include step outcomes, source hashes, versions, logs and the HTML browser report. All suites are attempted after successful setup even if another suite fails. A failed setup stays failed; later suites are skipped. Normal Bash pipefail preserves test failures through tee. No models or paid model APIs are called. GitHub Actions usage is subject to repository billing/quotas.

This is a regrade, not a new experiment. It does not reproduce original generation conditions, compare coding speed, establish model-independent harness quality, run the broader security/license graders, or prove repeatability over new tasks. Local test counts vary. Ubuntu runner updates and package registries remain external dependencies; the runner image itself is not digest-pinned.

## Windows preflight

From the CI worktree, with Python 3 available:

```powershell
py -3 scripts/prepare_title_edit.py --tool antigravity --output "$env:TEMP\title-edit-antigravity-check"
```

The destination must be new. Repeat with other tool names and fresh output paths as needed. Missing commits require fetching the corresponding results and protocol branches.

## Run on GitHub

Commit only the workflow, script and this guide. Push branch `ci/title-edit-verification`; the push event runs all four jobs without first merging. The workflow also checks PRs to master that change its code. The Actions Run workflow button is available after the workflow is present on the default branch. Re-run an existing run before then if required. Inspect four green jobs and download each tool's artifact before describing the common regrade as complete.

Do not merge result branches into the frozen baseline. These files do not change the preserved submissions or existing referee workflow. AI assistance: ChatGPT/Codex prepared these verification files; team review and actual GitHub execution remain required.

## Preparation checks

The restoration script was exercised against all four fixed submissions. The restored source files were checked against their Git blobs. On the preparation host (Node 24.19.0, npm 11.9.0), all four restored apps passed the nine baseline tests and 12 API tests. Tool-local suites passed with counts 16 (Antigravity), 14 (Claude), 13 (Codex), and 12 (Copilot). YAML parsing and Bash syntax checks passed. These are preflight results, not a GitHub Actions run or validation of Node 24.21.0 on the runner.

The protocol-matching Chromium download returned an invalid/truncated archive on the preparation host; the browser suites were not executed there. No substitute browser was used. Kapil separately verified Antigravity's 10 browser tests on Windows. All four browser suites and the complete workflow still need to succeed in GitHub before the common CI regrade is called verified.
