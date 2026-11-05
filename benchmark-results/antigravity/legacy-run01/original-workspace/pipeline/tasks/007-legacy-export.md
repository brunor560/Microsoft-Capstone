---
task_id: 007-legacy-export
title: Fix the billing export (legacy code)
target: app
weight_profile: standard
acceptance:
  test_command: "npm test"
  test_framework: node-test
---

## Ticket BIL-112: billing export breaks on titles with commas

> **From:** billing team
> **Priority:** high
>
> Since people started writing titles like "Call Sam, then Alex", the
> nightly export (`GET /api/todos/export.csv`, the "Export CSV" link on the
> page) gives us rows with too many columns and our ingest rejects the
> whole file. Titles with double quotes or line breaks break it too.
>
> Please fix the export so these titles come through intact. The export
> code is old and has no tests. Our ingest parses the file byte for byte
> as described in `app/docs/EXPORT-FORMAT.md`, so nothing else about the
> output may change.

## Requirements

FIX-01. A title containing a comma is exported as one field, wrapped in
double quotes, as described under "Quoting" in `app/docs/EXPORT-FORMAT.md`.

FIX-02. A title containing a double quote is wrapped in double quotes, and
each double quote inside it is doubled.

FIX-03. A title containing a line break (carriage return or line feed) is
wrapped in double quotes, so the row can still be read as one record.

FIX-04. Every other rule in `app/docs/EXPORT-FORMAT.md` stays exactly as it
is today: header, line endings, row order, id padding, cutting long titles,
the spreadsheet guard, the `DONE` column, and the output for an empty list.
Titles that need no quoting are exported byte for byte as before.

FIX-05. The functions exported by `app/legacy/billing-export.js` (`toCsv`,
`pad_id`, `clean_title`) keep their names and signatures, and the route and
the "Export CSV" link keep working.

TEST-01. Add tests to `app/test.js` that cover the export, including the
cases above. Test through the exported functions or the HTTP route.

## Constraints

- Modify only:
  - app/legacy/billing-export.js
  - app/test.js
- Do not add dependencies or change package files.
- Preserve all existing tests.
- Do not access parent folders, reference solutions or other runs.

## How your work is graded

Independent checks, run after you finish, grade your work on:

- **Functionality:** hidden tests of FIX-01 to FIX-03, FIX-05 and the
  existing app behaviour.
- **Safety (legacy contract):** hidden checks that the rest of the export
  format is unchanged (FIX-04), and that your tests in `app/test.js` catch
  the original bug (TEST-01).
- **Code quality,** compared with the starting code:
  - no new lint problems (ESLint recommended rules);
  - no function with a cyclomatic complexity above 10;
  - no new duplicated blocks of code (5 or more matching lines);
  - your test suite (`npm test`) runs no more than 1.2 times as long as
    the starting code's suite.

## Verification and reporting

Run npm test from app/.
On Windows, npm.cmd test is an acceptable equivalent.

Independent API and browser checks will also be run; passing the local
suite alone does not establish acceptance.

In your final message, report:
- Each file you changed, with a short summary of the change.
- Every command you ran to build or test, in order, and its outcome.
- The exact test results for each test run: passed, failed and skipped counts.
- Any browser or manual checks you performed and their outcomes, or that you performed none.
- Errors, retries, limitations, or requirements you could not complete.
- Any requirement you found unclear, and how you interpreted it.
- Anything unexpected you noticed in the project.
- If your tool shows them: the model you ran as, how long the session took, and how many tokens it used. Write "not available" for any you cannot see.
