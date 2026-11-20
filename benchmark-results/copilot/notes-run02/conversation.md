## Task prompt

Read pipeline/tasks/010-todo-notes.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture. Let me implement the changes:

Now update the HTML:

Now add the API tests to test.js:

All 17 tests pass. Here's a summary:

---

## Summary

### Files changed

**`app/server.js`**
- Added `notes: ''` to both initial seed todos
- Added `validateNotes()` helper (returns error string or null) to avoid code duplication
- `POST /api/todos`: accepts optional `notes`, validates via helper, stores it (defaults to `""`)
- `PUT /api/todos/:id`: validates and updates `notes` if provided; returns 400 if invalid

**`app/public/index.html`**
- Restructured form layout (flex-column) to accommodate the textarea
- Added `<label for="notes-input">Notes</label>` + `<textarea id="notes-input">` with `aria-label="Notes"`
- Added `escapeHtml()` and `formatNotes()` functions: HTML-escapes content first (XSS-safe), then applies `**bold**` → `<strong>`, `[text](https://…)` → `<a href>`, and `\n` → `<br>`
- Renders non-empty `notes` in a `<div class="notes">` beneath each todo title
- Form submission now sends `notes` to the API and clears the textarea after submit

**`app/test.js`**
- Added 8 new tests covering API-01 (notes field on all todos), API-02 (POST and PUT store/return notes, default empty string), and API-03 (non-string rejected with 400, >1000 chars rejected with 400, changes not applied on error)

### Commands run

| Command | Outcome |
|---|---|
| `npm test` (from `app/`) | ✅ 17 passed, 0 failed, 0 skipped |

### Browser/manual checks
None performed (no browser available in this environment).

### Requirements unclear / interpretations
- UI-02 says "each line break … starts a new line" — interpreted as `\n` → `<br>` in HTML output.
- The `[text](url)` link regex only allows `http://` and `https://` URLs to prevent `javascript:` injection.

### Security notes
- Notes are HTML-escaped before formatting to prevent XSS via crafted notes content. The link URL regex only matches `https?://` origins, blocking `javascript:` protocol injection.

### Model / session info
- Model: anthropic-direct/claude-sonnet-4-6
- Session timing and token counts: not available
