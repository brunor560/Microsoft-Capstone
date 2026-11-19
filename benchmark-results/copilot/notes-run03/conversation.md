## Task prompt

Read pipeline/tasks/010-todo-notes.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture. Let me implement all three files:

Now update index.html:

Now add API tests to test.js:

All 17 tests pass. Here's a summary:

---

## Summary

### Files changed

**`app/server.js`**
- Added `notes: ''` to seed todos
- `POST /api/todos`: accepts optional `notes`, validates it's a string ≤ 1000 chars, stores it (defaults to `''`)
- `PUT /api/todos/:id`: accepts optional `notes`, same validation, updates the field

**`app/public/index.html`**
- Restructured form to column layout; added `<label for="notes-input">Notes</label>` + `<textarea id="notes-input">` (accessible name "Notes")
- Added `escapeHtml()` and `formatNotes()` functions that safely escape HTML then apply `**bold**`, `[text](http(s)://…)` link, and newline→`<br>` formatting
- Todos with non-empty notes render a `<div class="notes">…</div>` beneath the title
- POST request now sends `notes` value; clears textarea after submit
- Title output is now HTML-escaped too

**`app/test.js`**
- Added 8 new tests covering API-01 (notes field on existing todos), API-02 (POST/PUT store and return notes), and API-03 (non-string and >1000-char notes → 400)

### Test runs

```
npm test   →  17 passed, 0 failed, 0 skipped
```

### Browser/manual checks
None performed (no browser available in sandbox).

### Errors, limitations, retries
None.

### Unclear requirements
None; interpreted "notes string" over 1000 chars as `notes.length > 1000`.

### Unexpected findings
Pre-existing XSS risk: `item.title` was interpolated into innerHTML without escaping. Fixed for title as a coupled concern (notes XSS protection required the same helper); the existing tests still pass.

### Session metadata
Model: `anthropic-direct/claude-sonnet-4-6` · Duration/tokens: not available from this interface.
