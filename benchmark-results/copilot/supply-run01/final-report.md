All 16 tests pass. Here's a summary:

## Summary

### Files Changed

**`app/server.js`**
- Added `computeBaseSlug(title)` — NFKD normalization, accent removal, lowercase, non-alphanumeric → `-`, trim dashes
- Added `withSlugs(list)` — maps todos to include computed `slug` field, handling empty-slug fallback (`todo-<id>`) and duplicate-slug suffix (`-<id>`)
- Updated `GET /api/todos` to return todos with slugs
- Added `GET /api/todos/by-slug/:slug` endpoint (200 with todo or 404)
- Updated `POST /api/todos` and `PUT /api/todos/:id` to include slug in responses

**`app/public/index.html`**
- Added `<code>${item.slug}</code>` to each todo list item (UI-01)

**`app/test.js`**
- Added 7 new tests covering REQ-01 (slug presence, accent stripping, duplicate suffix, empty fallback, PUT slug update) and REQ-02 (by-slug lookup success and 404)

### Test Results
- **Command:** `npm test` from `app/`
- **Result:** 16 passed, 0 failed, 0 skipped

### Browser/Manual Checks
None performed; local test suite covers all requirements.

### Model
Powered by `anthropic-direct/claude-sonnet-4-6`. Token/duration data: not available.
