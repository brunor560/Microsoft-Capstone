## Task prompt

Read pipeline/tasks/007-legacy-export.md and complete the task
exactly as specified.

Work only within this project folder. Do not access parent folders,
external grading files, reference solutions, or other runs.

Run the required tests and report the actual results.
Do not commit or push.


## Assistant messages

Now I have a clear picture. Let me fix the billing export and add tests.

Now add tests to `app/test.js`:

I'll add the tests using the edit tool instead:

All 21 tests pass. Here's the summary:

## Summary

### Files Changed

**`app/legacy/billing-export.js`** — Added `quote_field(s)` function implementing RFC 4180 quoting: wraps a field in double quotes if it contains a comma, double quote, CR, or LF, and doubles any internal double quotes. Updated `build_row` to apply `quote_field` to the cleaned title.

**`app/test.js`** — Added `require` for `toCsv`, `pad_id`, `clean_title` from billing-export, plus 12 new tests covering: empty list, plain title (no quoting), comma-in-title (FIX-01), double-quote-in-title (FIX-02), LF/CR in title (FIX-03), sort order, truncation, spreadsheet guard, `pad_id`, and the HTTP route.

### Commands Run

```
npm test   (from app/)  →  21 passed, 0 failed, 0 skipped
```

### Test Results

| Run | Passed | Failed | Skipped |
|-----|--------|--------|---------|
| `npm test` | 21 | 0 | 0 |

### Browser/Manual Checks
None performed.

### Errors / Limitations
None.

### Model / Session Info
Model: `anthropic-direct/claude-sonnet-4-6` — token count and duration not available from this interface.
