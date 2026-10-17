# Task 004 evaluator validation

Recorded 2026-10-17 on Windows 11, Node v24.22.0, npm 11.19.1, and
Playwright 1.64.1 (Chromium headless shell v1248).

## Results

| App version | Local | API | Browser | Logs |
|---|---|---|---|---|
| Unchanged starting app (4e258a9) | 9 / 9 | 5 / 24 | 2 / 4 | [evidence/before/](evidence/before/) |
| Fixes only the `Boolean()` bug | not run | 15 / 24 | not run | [validation-checks.txt](evidence/validation-checks.txt) |
| Reference fix ([reference/](reference/)) | 14 / 14 | 24 / 24 | 4 / 4 | [evidence/after/](evidence/after/) |
| Reference fix, 3 repeat runs | — | 24 / 24 each time | 4 / 4 each time | [validation-checks.txt](evidence/validation-checks.txt) |

What this shows:

- **The graders detect every bug.** Each failing check on the unchanged app
  matches one of B1 to B4 in [ACCEPTANCE.md](ACCEPTANCE.md).
- **The guard checks pass on both versions.** They catch an agent that
  breaks working behaviour.
- **The reference fix passes everything,** so the requirements can be met
  within the allowed files.
- **Partial fixes get partial scores,** so the task separates agents.
- **No flaky tests** across 3 repeat runs.

## Limitations

- **The UI-03 "looks the same" check also passes on the unchanged app,**
  because that app re-renders the same state after a failed save. It guards
  against an agent that updates the row optimistically and never rolls it
  back. On the unchanged app, UI-02 (no alert) is what fails.
- **Rows are found by their title text,** and clicking that text must still
  toggle the todo. An agent that moves toggling to a separate control only
  (for example a checkbox, with the text no longer clickable) fails UI-01,
  as the task requires.
- **The add/delete check finds the first text box and buttons named
  "Add" and "Delete".** Renaming those controls would fail UI-04.
- **The browser tests make network failures happen by intercepting the
  request.** They don't test a real server outage.
- **The order of status codes is fixed only where the task states it.**
  A malformed id always returns 400. A bad body sent to a missing todo may
  return either 400 or 404, so it is not tested.
- **The evidence was recorded before this folder was committed.** Re-run
  the graders from the agreed evaluator commit and compare counts before
  measured runs.
- **The operator who wrote the graders and reference fix knows the task,**
  so runs by that operator are not blind.
