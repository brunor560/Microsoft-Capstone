## Task prompt

Read pipeline/tasks/004-fix-update-validation.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture. Let me analyze the bugs:

1. **Bug 1**: `Boolean(req.body.completed)` converts the string `"false"` to `true` — not validating that `completed` is strictly a boolean.
2. **Bug 2**: `toggleStatus` in the UI never handles fetch errors, so users see nothing if the server fails.

I'll fix both and add the required tests.

Now refactor DELETE to use the shared helper:

Now fix the frontend — add error handling and role="alert" per todo item:

Now add the required API tests to `test.js`:

All 16 tests pass. Here's a summary:

---

## Summary

### Files changed

**`app/server.js`**
- Extracted a `parseId()` helper (shared by PUT and DELETE) to avoid code duplication
- Rewrote PUT `/api/todos/:id` to: validate ID format (API-02), reject non-object bodies like arrays (API-03), strictly require `completed` to be a JSON boolean (API-01), and only mutate the todo after all validation passes (API-04)

**`app/public/index.html`**
- Added `data-id` attribute to each `<li>` for targeting
- Added `showUpdateError()` helper that injects a `role="alert"` span into the failing todo's list item (UI-02)
- Wrapped `toggleStatus` in try/catch; on HTTP error or network failure it calls `showUpdateError` and returns without calling `fetchTodos`, preserving the pre-click state (UI-03)

**`app/test.js`**
- Added 7 new tests covering API-01 through API-05

### Bug causes

1. **String "false" toggling todos on**: `Boolean(req.body.completed)` coerces the string `"false"` to `true`. Fix: reject any non-boolean `completed` with HTTP 400.

2. **No feedback when server is down**: `toggleStatus` never checked the response or caught network errors, so a failed request was silently ignored. Fix: check `res.ok`, catch network failures, and render a `role="alert"` error message in the todo's list item.

### Test results
- **Command**: `npm test` (from `app/`)
- **Result**: 16 passed, 0 failed, 0 skipped

### Browser/manual checks
None performed (automated tests cover all API requirements).

### Model / session info
Model: `anthropic-direct/claude-sonnet-4-6` — token counts not available from this interface.
