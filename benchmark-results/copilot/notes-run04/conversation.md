## Task prompt

Read pipeline/tasks/010-todo-notes.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture. Let me implement all the changes:

Now update the HTML:

Now update the JavaScript in index.html:

Now add tests for API-01 to API-03 in test.js:

All 17 tests pass. Here's a summary:

---

## Summary

### Files changed

**`app/server.js`**
- Added `notes: ''` to seed todos
- `POST /api/todos`: accepts optional `notes`, validates (string, ≤1000 chars), stores it (default `""`)
- `PUT /api/todos/:id`: accepts optional `notes`, validates same rules, updates if valid

**`app/public/index.html`**
- Added `<textarea id="notes-input">` with accessible `<label>Notes</label>` to the add form
- Notes submitted on form submit; cleared after
- `escapeHtml()` prevents XSS in titles and notes
- `formatNotes()` renders `**bold**` → `<strong>`, `[text](url)` → `<a>`, `\n` → `<br>`
- Notes shown in `<div class="notes">` under title when non-empty

**`app/test.js`**
- Added 8 new tests covering API-01 (default `""` notes), API-02 (store/return notes via POST & PUT), API-03 (reject non-string and >1000 char notes)

### Commands run
1. `npm test` — **17 passed, 0 failed, 0 skipped**

### Browser/manual checks
None performed (automated tests only).

### Errors/retries/limitations
None.

### Unclear requirements
None; all requirements interpreted as written.

### Security notes
HTML escaping via `escapeHtml()` is applied before formatting in the UI, preventing XSS from malicious todo titles or notes.

### Model/session info
Model: `anthropic-direct/claude-sonnet-4-6`. Token/duration data: not available.
