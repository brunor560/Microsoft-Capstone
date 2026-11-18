## Task prompt

Read pipeline/tasks/004-fix-update-validation.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture. Let me implement the fixes:

**Bug 1 root cause:** `Boolean(req.body.completed)` converts string `"false"` to `true` (truthy string).  
**Bug 2 root cause:** `toggleStatus` never checks if the fetch failed — it always calls `fetchTodos()`.

Now fix the UI for error handling:

Now add tests for the API requirements to `test.js`:

All 15 tests pass. Here's the summary:

---

## Summary

### Files changed

**`app/server.js`** — Fixed the `PUT /api/todos/:id` endpoint:
- Added same ID validation as DELETE (digits-only, >0, ≤MAX_SAFE_INTEGER, leading zeros ok)
- Added body validation (must be a plain JSON object, not array)
- Changed `completed` to require a strict boolean (`typeof === 'boolean'`), rejecting strings, numbers, and null
- Validation occurs before any mutation (API-04)

**`app/public/index.html`** — Fixed toggle error handling:
- Added `currentTodos` state to track the last-fetched list
- Extracted `renderTodos(todos, errorMap)` function that optionally renders a `role="alert"` error span inside a todo's `<li>`
- `toggleStatus` now catches network errors and non-OK responses, re-renders with the original `currentTodos` (restoring prior state) plus an error message for that item

**`app/test.js`** — Added tests for API-01 through API-04 (5 new tests)

### Bug causes
1. **"Todos it un-checks end up checked"** — `Boolean("false")` returns `true` because non-empty strings are truthy. Fixed by requiring `completed` to be an actual JSON boolean.
2. **"Nothing happens when server is down"** — `toggleStatus` never awaited the response or checked `res.ok`; it always called `fetchTodos()` silently. Fixed with try/catch + `!res.ok` check that shows a `role="alert"` error and restores prior state.

### Test results
```
Command: npm test (from app/)
tests: 15, pass: 15, fail: 0, skipped: 0
```

### Browser/manual checks
None performed (automated tests only).

### Model info
Powered by `anthropic-direct/claude-sonnet-4-6`. Token/duration counts: not available.
