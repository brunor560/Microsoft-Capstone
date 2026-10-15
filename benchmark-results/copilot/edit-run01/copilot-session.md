user.message

Read pipeline/tasks/003-edit-todo-title.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.

assistant.message

I’ll update the API validation and browser editor within the three allowed files, add focused API coverage, then run the required `npm test` from `app/`.

assistant.message

The required suite passes (11/11). I’m tightening the valid-update assertions to verify unrelated todos remain unchanged and the update is reflected by a subsequent GET, then I’ll rerun the required suite.

assistant.message

Implemented todo title editing and API validation.

- `app/public/index.html`: Added per-todo Edit/Save/Cancel controls, keyboard-accessible inline editing, visible validation/save errors, and safe text rendering for titles.
- `app/server.js`: Validates supplied PUT titles before changing any todo state; valid titles are trimmed while preserving completion when omitted.
- `app/test.js`: Added API coverage for valid and invalid title updates, state preservation, completion-only updates, persistence via GET, and PUT 404 behavior.

**Verification:** `npm test` from `app/` passed: **12 tests, 12 passed, 0 failed**. The inline browser script syntax check also passed. No browser interaction checks were performed. No other errors or unresolved requirements identified; no commit or push was made.
