All 22 tests pass. Here's a summary:

## Summary

### Files Changed

**`app/legacy/billing-export.js`** — Added `quote_field()` function implementing RFC 4180 quoting (wraps in `"` if field contains `,`, `"`, `\r`, or `\n`; doubles embedded `"`). Applied in `build_row()` after `clean_title()`.

**`app/test.js`** — Added 13 new tests covering: `pad_id`, `clean_title`, `toCsv` with comma/quote/LF/CR titles (FIX-01–03), plain unquoted titles (FIX-04), header, empty list, row order, DONE column, and the HTTP export route.

### Test Results

```
npm test (from app/)
tests: 22 | pass: 22 | fail: 0 | skipped: 0
```

### Manual/Browser Checks
None performed.

### Errors/Limitations
None.

### Unexpected Observations
None.

### Model/Session Info
Model: anthropic-direct/claude-sonnet-4-6. Token/duration info: not available.
