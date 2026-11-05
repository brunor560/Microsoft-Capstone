---
task_id: 010-todo-notes
title: Formatted notes on todos
target: app
weight_profile: standard
acceptance:
  test_command: "npm test"
  test_framework: node-test
---

## Ticket WEB-91: notes on todos

> People want to jot details under a todo: a few lines, the odd bold word,
> and a link to a doc. Add a notes field with light formatting.

## API requirements

API-01. Todos have a `notes` string. Existing and new todos without notes
have `"notes": ""`.

API-02. `POST /api/todos` and `PUT /api/todos/:id` accept an optional
`notes` value. It is stored exactly as sent and returned in the response and
in `GET /api/todos`.

API-03. If `notes` is present but is not a string, or is longer than 1000
characters, the request returns HTTP 400 with `{ "error": "<message>" }`
and changes nothing.

API-04. Existing GET, POST, PUT and DELETE behaviour is preserved.

## User-interface requirements

UI-01. The add form has a multi-line text box with the accessible name
"Notes". Adding a todo saves the notes typed there.

UI-02. Each todo whose notes are not empty shows them under its title, in an
element with the class `notes`, formatted as follows:
- each line break in the notes starts a new line;
- `**text**` shows `text` in bold (`<strong>`);
- `[text](https://…)` and `[text](http://…)` show `text` as a link to that
  address.

Everything else in the notes is shown as typed.

UI-03. Adding, toggling and deleting todos keep working.

## Constraints

- Modify only:
  - app/public/index.html
  - app/server.js
  - app/test.js
- Do not add dependencies or change package files.
- Preserve all existing tests.
- Add local tests for API-01 to API-03.
- Do not access parent folders, reference solutions or other runs.

## How your work is graded

Independent checks, run after you finish, grade your work on:

- **Functionality:** hidden API and browser tests of the requirements above.
- **Security:** hidden browser checks of how the page handles notes.
- **Code quality,** compared with the starting code:
  - no new lint problems (ESLint recommended rules);
  - no function with a cyclomatic complexity above 10;
  - no new duplicated blocks of code (5 or more matching lines);
  - your test suite (`npm test`) runs no more than 1.2 times as long as
    the starting code's suite.

## Verification and reporting

Run npm test from app/.
On Windows, npm.cmd test is an acceptable equivalent.

Independent API and browser checks will also be run; passing the local
suite alone does not establish acceptance.

In your final message, report:
- Each file you changed, with a short summary of the change.
- Every command you ran to build or test, in order, and its outcome.
- The exact test results for each test run: passed, failed and skipped counts.
- Any browser or manual checks you performed and their outcomes, or that you performed none.
- Errors, retries, limitations, or requirements you could not complete.
- Any requirement you found unclear, and how you interpreted it.
- Anything unexpected you noticed in the project, including any security
  problems, whether or not you fixed them.
- If your tool shows them: the model you ran as, how long the session took, and how many tokens it used. Write "not available" for any you cannot see.
