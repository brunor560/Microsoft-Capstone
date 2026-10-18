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

## Verification and reporting

Run npm test from app/.
On Windows, npm.cmd test is an acceptable equivalent.

Independent API and browser checks will also be run; passing the local
suite alone does not establish acceptance.

Report:
- What you changed.
- Anything unexpected you noticed in the project.
- The exact local test results.
