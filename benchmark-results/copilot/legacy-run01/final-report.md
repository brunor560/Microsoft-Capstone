All 22 tests pass. Here's the summary:

## Changes Made

**`app/legacy/billing-export.js`** — Added `quote_field()` function that wraps a field in double quotes if it contains a comma, double quote, CR, or LF (RFC 4180), doubling any embedded quotes. Applied it in `build_row()` after `clean_title()`.

**`app/test.js`** — Added 13 new tests covering: `pad_id`, `clean_title` (truncation, spreadsheet guard), `toCsv` (empty list, CRLF endings, comma quoting, double-quote doubling, LF/CR quoting, plain titles, sort order), and HTTP route tests for the CSV export.

## Test Results

Command: `npm test` from `app/`  
**22 passed, 0 failed, 0 skipped**

## Notes
- No browser/manual checks performed.
- No unclear requirements.
- The fix is minimal: one new helper function + one call site change, preserving all existing behavior per FIX-04.
- Model: `anthropic-direct/claude-sonnet-4-6`; token/timing data: not available.
