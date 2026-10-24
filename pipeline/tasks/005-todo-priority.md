---
task_id: 005-todo-priority
title: Add a priority to todos
target: app
weight_profile: standard
acceptance:
  test_command: "npm test"
  test_framework: node-test
---

## Objective

Users want to mark how important each todo is. Add a priority to every
todo, in the API and in the page.

## API requirements

API-01. `POST /api/todos` accepts an optional `priority` of `"low"`,
`"medium"` or `"high"`. When it is omitted, the new todo gets `"medium"`.
Any other value, including other strings, numbers and null, returns
HTTP 400 and creates nothing.

API-02. `PUT /api/todos/:id` can change `priority`, using the same allowed
values. An invalid priority returns HTTP 400 and changes nothing, even when
the same request also contains other valid fields.

API-03. Every todo returned by the API includes `priority`. Existing todos
start with `"medium"`.

API-04. Preserve all existing GET, POST, PUT and DELETE behaviour.

Error responses use the existing JSON shape: `{ "error": "<message>" }`.

## User-interface requirements

UI-01. Each todo in the list shows its priority as visible text
(low, medium or high).

UI-02. The add form has a priority control with the accessible name
"Priority", offering low, medium and high, with medium selected by default.

UI-03. Adding a todo with a chosen priority shows that priority in the
list, and it is still shown after a page reload.

UI-04. Toggling, adding and deleting todos keep working.

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

- **Functionality:** hidden tests of the requirements above.
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
- Anything unexpected you noticed in the project.
- If your tool shows them: the model you ran as, how long the session took, and how many tokens it used. Write "not available" for any you cannot see.
