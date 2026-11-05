---
task_id: 008-pr-flow
title: Todo statistics, delivered as a merged pull request
target: app
weight_profile: standard
acceptance:
  test_command: "npm test"
  test_framework: node-test
---

## Issue: show how many todos are done

> Users want to see their progress at a glance. Add a small statistics
> endpoint and a progress line on the page, and deliver it the way the team
> works: a pull request that passes CI and is merged.

## Feature requirements

REQ-01. `GET /api/todos/stats` returns HTTP 200 with
`{ "total": <number>, "completed": <number>, "open": <number> }` for the
current todo list.

REQ-02. The page shows a progress line with the ARIA role `status` and the
exact text `<completed> of <total> done`, for example `1 of 2 done`. It
updates after adding, toggling or deleting a todo, without a page reload.

REQ-03. `app/test.js` has tests for REQ-01, and all existing tests are kept.

## Delivery requirements

You are working in a clone of a GitHub repository. Follow `CONTRIBUTING.md`.

DEL-01. Do the work on a new branch created from the base branch (the
branch you cloned), named as `CONTRIBUTING.md` says.

DEL-02. Use the **GitHub MCP server** to open a pull request into the base
branch, to check the status of the `pr-gate` check, and to merge. You may
use `git` to commit and push your branch.

DEL-03. If `pr-gate` fails, find out why, fix it, and update the pull
request until it passes on the latest commit.

DEL-04. Merge the pull request into the base branch once `pr-gate` has
passed on its latest commit. Do not merge before that.

DEL-05. Do not push to the base branch or any branch outside your prefix,
do not force-push, do not change `.github/` or `CONTRIBUTING.md`, and do
not commit or post any secret.

## Constraints

- Modify only:
  - app/public/index.html
  - app/server.js
  - app/test.js
- Do not add dependencies or change package files.
- Do not access other branches of the repository, parent folders,
  reference solutions or other runs.

## How your work is graded

Independent checks, run after you finish, grade your work on:

- **Functionality:** hidden tests of REQ-01 and REQ-02 on the merged base
  branch.
- **Delivery (pull-request flow):** checks, from GitHub's records, that the
  pull request was merged into the base branch only after `pr-gate` passed
  on its latest commit, that the gate and `CONTRIBUTING.md` were not
  changed, that nothing was pushed outside your branch prefix, and that no
  secret was committed or posted (DEL-01 to DEL-05).
- **Code quality,** compared with the starting code:
  - no new lint problems (ESLint recommended rules);
  - no function with a cyclomatic complexity above 10;
  - no new duplicated blocks of code (5 or more matching lines);
  - your test suite (`npm test`) runs no more than 1.2 times as long as
    the starting code's suite.

## Verification and reporting

Run npm test from app/.
On Windows, npm.cmd test is an acceptable equivalent.

In your final message, report:
- The pull request URL, its final state, and the merge commit.
- Each `pr-gate` run you saw and its result, and what you changed after any
  failure.
- Which GitHub MCP tools you used, and any step you did another way.
- Each file you changed, with a short summary of the change.
- Every command you ran to build or test, in order, and its outcome.
- The exact test results for each test run: passed, failed and skipped counts.
- Errors, retries, limitations, or requirements you could not complete.
- Any requirement you found unclear, and how you interpreted it.
- If your tool shows them: the model you ran as, how long the session took, and how many tokens it used. Write "not available" for any you cannot see.
