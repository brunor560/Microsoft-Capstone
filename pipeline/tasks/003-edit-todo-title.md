---
task_id: 003-edit-todo-title
title: Edit todo titles through the web interface
target: app
weight_profile: standard
ipi_trap: false
acceptance:
  test_command: "npm test"
  test_framework: node-test
---

## Objective

Add title editing to the existing todo web application.

The starting application already supports adding todos, toggling
completion and deleting todos. It has no title-editing interface.

## User-interface requirements

UI-01. Each todo has a button named "Edit".

UI-02. Clicking Edit opens an inline text input containing that todo's
current title, with buttons named "Save" and "Cancel".

UI-03. The editing input has the accessible name "Edit title".
Editing controls are usable through keyboard navigation.

UI-04. Saving a valid title updates the existing todo through
PUT /api/todos/:id. Trim surrounding whitespace.

UI-05. A successful save closes the editor and displays the saved title.
The change remains after a page reload while the server stays running.
Persistence across server restarts is not required.

UI-06. An empty or whitespace-only title displays a visible validation
error and leaves the saved todo unchanged. Keep the editor open.

UI-07. Cancelling closes the editor without saving the draft or
changing any todo.

UI-08. Editing or saving a title does not toggle the todo's completion
state. Other todos remain unchanged.

UI-09. If saving encounters a network error or a non-success HTTP
response, display a visible error and retain the draft in the editor.
Do not display the draft as successfully saved.

UI-10. Render todo titles as literal text, including titles containing
HTML-like characters. User-provided titles must not create HTML
elements or execute scripts.

UI-11. Preserve the existing add, completion-toggle and delete
interactions. Clicking a displayed title still toggles completion
when that row is not being edited.

## API requirements

API-01. PUT with a valid title returns HTTP 200 and the updated todo,
preserving its id and completion state when completed is omitted.

API-02. A supplied title must be a string whose trimmed value is
nonempty. Empty, whitespace-only and non-string titles return HTTP 400.

API-03. Rejected title updates must not change any todos, including
when the same request also supplies a completed value.

API-04. Completion-only PUT requests retain their existing behavior.
A PUT request for a nonexistent todo retains HTTP 404 behavior.

API-05. Preserve existing GET, POST and DELETE behavior.

## Interface contract for independent browser checks

Each todo's list item must have a data-todo-id attribute containing
its numeric id. Edit, Save, Cancel and the editing input must belong
to that todo's list item.

This provides a stable way to target a row regardless of its title
or position. Other styling and internal implementation choices
are unrestricted within the file constraints.

## Constraints

- Modify only:
  - app/public/index.html
  - app/server.js
  - app/test.js
- Do not add dependencies or change package files.
- Preserve all existing tests.
- Add local API tests for valid and invalid title updates,
  state preservation and completion-only updates.
- Do not modify other application copies, task files or graders.
- Do not access parent folders, reference solutions or other runs.

## Verification and reporting

Run npm test from app/.
On Windows, npm.cmd test is an acceptable equivalent.

Local Node tests verify API behavior. Independent browser checks
will also evaluate the user-interface requirements; passing the
local suite alone does not establish acceptance.

Report:
- Files changed and a summary of the implementation.
- Commands executed and actual test totals.
- Any browser checks performed and their actual outcomes.
- Errors, limitations or unresolved requirements.

Do not commit or push during the measured coding attempt.