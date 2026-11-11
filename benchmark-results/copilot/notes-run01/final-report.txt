All 18 tests pass. Here's a summary:

---

## Summary

### Files changed

**`app/server.js`**
- Added `notes: ""` to seeded todos
- Added `validateNotes()` helper (string check, max 1000 chars)
- `POST /api/todos`: accepts optional `notes`, validates it, stores it (defaults to `""`)
- `PUT /api/todos/:id`: accepts optional `notes`, validates and updates it

**`app/public/index.html`**
- Updated form layout to flex-column; added `<label for="notes-input">Notes</label>` and a `<textarea id="notes-input">` to the add form
- Added `formatNotes()` function that safely escapes HTML, renders `**text**` as `<strong>`, `[text](https://…)` as `<a>`, and `\n` as `<br>`
- Updated todo rendering to include a `<div class="notes">` with formatted notes (when non-empty)
- Form submission now sends `notes` and clears the textarea

**`app/test.js`**
- Added 9 new tests covering API-01 (notes field on all todos), API-02 (POST/PUT store notes), API-03 (non-string notes → 400, >1000 chars → 400, boundary at 1000 accepted)

### Test results
**Command:** `npm test` from `app/`  
**Outcome:** ✅ 18 passed, 0 failed, 0 skipped

### Browser/manual checks
None performed (automated tests only).

### Errors, retries, limitations
None.

### Unclear requirements / interpretations
- UI-02 says "each line break in the notes starts a new line" — interpreted as `\n` → `<br>`.
- Security: `formatNotes()` HTML-escapes all plain text before inserting HTML, so notes cannot inject script/HTML.

### Unexpected findings
- The existing `fetchTodos` rendered `item.title` directly into `innerHTML` (pre-existing XSS risk in title); left unchanged per instructions (unrelated pre-existing issue), but notes rendering is fully escaped.

### Model / session info
- Model: anthropic-direct/claude-sonnet-4-6
- Session time / tokens: not available
