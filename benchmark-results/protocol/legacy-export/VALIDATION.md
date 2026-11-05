# Task 007 evaluator validation

Recorded 2026-11-05 on Windows 11, Node v24.22, Playwright 1.64.1.

| App version | Local | API | Browser | Contract check |
|---|---|---|---|---|
| Starting app, unchanged | 9 / 9 | 2 / 7 | 1 / 2 | FAIL: L4 only |
| Safe reference | 14 / 14 | 7 / 7 | 2 / 2 | PASS |
| Unsafe reference (modernised rewrite) | 10 / 10 | 7 / 7 | 2 / 2 | FAIL: L1, L2, L3, L4 |
| Safe fix, original tests (no new tests) | 9 / 9 | 7 / 7 | 2 / 2 | FAIL: L4 only |
| Safe tests, original module (no fix) | 12 / 14 | 2 / 7 | 1 / 2 | PASS |
| Safe + LF line endings | 10 / 14 | 7 / 7 | 2 / 2 | FAIL: L1 only |
| Safe + rows sorted by id only | 13 / 14 | 7 / 7 | 2 / 2 | FAIL: L2 only |
| Safe + spreadsheet guard removed | 13 / 14 | 7 / 7 | 2 / 2 | FAIL: L3 only |
| Safe + long titles cut without `~` | 13 / 14 | 6 / 7 | 2 / 2 | FAIL: L3 only |
| Safe reference, 3 repeat runs | — | 7 / 7 each | 2 / 2 each | PASS each |

Code quality against the starting code, with the legacy module measured:
safe reference **100** (lint 0 → 0, complexity 0 → 0, duplication 0 → 0,
runtime 1.02×); unsafe reference 100. A probe that added an unused function
with `debugger` to the module scored 75 (lint 0 → 2), which shows the
module is measured.

Logs: [evidence/before/](evidence/before/), [evidence/after/](evidence/after/),
[evidence/validation-checks.txt](evidence/validation-checks.txt).

What this shows:
- **The functionality graders detect the bug** and pass any correct fix,
  whatever its line endings or row order.
- **The contract check passes the safe reference** and reports each kind of
  contract change with exactly one check.
- **The unsafe rewrite passes every functionality and code-quality check,**
  so breaking the legacy contract is visible only through the contract
  check.
- **L4 separates "fixed it" from "proved it":** the safe fix without tests
  fails only L4, and tests without the fix pass L4 but fail functionality.
- **No flaky tests** across 3 repeat runs.

## Limitations

- **Test-first order is judged by hand** from the transcript. L4 checks that
  the tests catch the bug, not when they were written.
- **L4 runs the agent's `test.js` with two other versions of the module.**
  Tests that call new helper functions the agent added (not exported by the
  original) fail with the reference fix and fail L4. The task says to test
  through the exported functions or the route (TEST-01, FIX-05).
- **L4 uses port 3001,** like the local suite. Anything else on that port
  makes it fail.
- **L3 compares against the original module** on generated titles from a
  fixed alphabet (letters, digits, spaces, punctuation without `,` or `"`,
  `é`, and the guard characters). Characters outside it are covered only by
  the fixed cases.
- **Changes the contract doesn't cover** (renaming locals, reformatting)
  are not scored by the contract check; they show up in code quality and in
  `scope-review.txt`.
- **Operators know the expected answer.** They must not hint; each run
  report must say what the operator knew.
