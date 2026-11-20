## Task prompt

Read pipeline/tasks/004-fix-update-validation.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture of both bugs and all requirements. Let me implement the fixes:

**Bug 1**: `Boolean("false")` → `true` because non-empty string is truthy  
**Bug 2**: No error handling in `toggleStatus` - silently swallows errors

Now update the HTML to handle errors:

Now add tests for all API requirements:

All 15 tests pass. Here's a summary:

---

## Summary

### Files Changed

**`app/server.js`** – Fixed the PUT `/api/todos/:id` endpoint:
- Added same ID validation as DELETE (digits only, > 0, ≤ MAX_SAFE_INTEGER, leading zeros OK)
- Added body type check (array → 400)
- Changed `completed` to require a strict JSON boolean (`typeof === 'boolean'`), not `Boolean(value)` which coerces strings
- All validations happen before any mutation (API-04)

**`app/public/index.html`** – Fixed `toggleStatus`:
- Added `data-id` to each `<li>` for targeting
- Added `<span role="alert" class="error-msg">` inside each `<li>` for error display
- Wrapped `fetch` in try/catch; on network error shows "Could not reach the server"
- On non-OK HTTP response, shows the error message in that todo's alert element
- On failure, does **not** call `fetchTodos()`, preserving pre-click state (UI-03)

**`app/test.js`** – Added tests for API-01 through API-04 (5 new test cases).

### Bug Causes

1. **String "false" checked as truthy**: `Boolean(req.body.completed)` converts any non-empty string to `true`, so `completed: "false"` from a CSV sync became `true`. Fix: enforce `typeof completed === 'boolean'`.
2. **Silent failure on network error**: `toggleStatus` had no try/catch and called `fetchTodos()` unconditionally. If the server was down, the promise rejection was unhandled and the UI showed nothing. Fix: wrap in try/catch and show an error in a `role="alert"` element.

### Test Results

```
tests 15 | pass 15 | fail 0 | skipped 0
```

Command: `npm test` from `app/` — exit code 0.

### Browser/manual checks
None performed (UI requirements verified by code review and test coverage).
