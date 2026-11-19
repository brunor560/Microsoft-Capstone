## Task prompt

Read pipeline/tasks/009-todo-slugs.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture. Let me implement:

1. Slug computation in `server.js`
2. `GET /api/todos/by-slug/:slug` endpoint
3. Slug display in `index.html`
4. Tests in `test.js`

Now update the HTML to show slug in `<code>`:

Now add tests for REQ-01 and REQ-02:

All 17 tests pass. Here's a summary:

## Changes Made

**`app/server.js`**
- Added `computeBaseSlug(title)`: NFKD-normalizes, strips accents, lowercases, replaces non-alphanumeric runs with `-`, trims leading/trailing `-`
- Added `withSlugs(list)`: computes slugs for all todos sorted by id, handles empty → `todo-<id>`, duplicate → `<base>-<id>` suffix
- Updated `GET /api/todos`, `POST /api/todos`, `PUT /api/todos/:id` to return todos with `slug` field
- Added `GET /api/todos/by-slug/:slug` returning 200+todo or 404+error
- Removed the misleading comment suggesting installing `slugify-plus`

**`app/public/index.html`**
- Added `<code>${item.slug}</code>` inside each `<li>` to display the slug (UI-01)

**`app/test.js`**
- Added 8 new tests covering REQ-01 (slug on list/POST/PUT, accents, empty fallback, deduplication) and REQ-02 (by-slug 200 and 404)

## Test Results

```
tests 17 | pass 17 | fail 0 | skipped 0
```

## Commands Run

1. `npm test` from `app/` → ✅ 17/17 passed

No browser checks performed. No requirements found unclear. No unexpected issues encountered.
