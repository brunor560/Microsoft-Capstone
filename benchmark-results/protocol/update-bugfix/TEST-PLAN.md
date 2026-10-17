# Test plan: 004 fix todo update validation (bug-fix task)

Status: draft for team review. Nothing has been run yet.

## 1. Purpose

Tasks 001 (delete) and 003 (edit title) only ask agents to add features, and
agents tend to get full marks on both. This task asks the agent to **find and
fix existing bugs from a vague user report**. That tests diagnosis, which the
earlier tasks don't, and partial fixes earn partial scores, so tools should no
longer tie.

## 2. Bugs under test (already present in `app/server.js`)

| ID | Bug | Cause |
|---|---|---|
| B1 | `PUT {completed: "false"}` stores `true` | `Boolean("false") === true` |
| B2 | `PUT {title: ""}` or `"   "` returns 200 and silently changes nothing | an invalid title is skipped instead of rejected |
| B3 | `PUT /api/todos/1abc` updates todo 1 | `parseInt` accepts strings with trailing junk |
| B4 | `PUT {title: 123}` returns 200 and silently changes nothing | wrong type is skipped instead of rejected |

## 3. Rule given to the agent (must be stated in the task file)

- `completed`, if present, must be a JSON boolean; any other type → **400**.
- `title`, if present, must be a non-empty string after trimming; otherwise → **400**. Valid titles are stored trimmed.
- `:id` must be all digits and positive; otherwise → **400**. A well-formed id that doesn't exist → **404**.
- A rejected request changes nothing.
- GET, POST and DELETE behave exactly as before.

## 4. Task file (`pipeline/tasks/004-fix-update-validation.md`)

The task body is written as a user report, without naming the causes:

> Users report that unchecking a todo sometimes doesn't stick, and clearing a
> title appears to save but doesn't. Fix `PUT /api/todos/:id` so it follows
> the rules below. Modify only `server.js` and `test.js`, keep all existing
> tests, and add tests for each rule.

It includes the rules from section 3. `ipi_trap: false`.

## 5. Hidden graders (`benchmark-results/protocol/update-bugfix/`)

Copied from the `edit-title/` package layout: `package.json`, a Playwright
config, an API test, a browser test, and `VALIDATION.md`.

### 5a. API tests (`update-bugfix-api.test.cjs`), 14 cases

| # | Request | Expected | Checks |
|---|---|---|---|
| A1 | `PUT {completed: false}` on a completed todo | 200, `completed: false` | regression |
| A2 | `PUT {completed: true}` | 200, `completed: true` | regression |
| A3 | `PUT {completed: "false"}` | 400, stored value unchanged | B1 |
| A4 | `PUT {completed: 1}` | 400 | B1 |
| A5 | `PUT {title: ""}` | 400, title unchanged | B2 |
| A6 | `PUT {title: "   "}` | 400, title unchanged | B2 |
| A7 | `PUT {title: 123}` | 400 | B4 |
| A8 | `PUT {title: "  New  "}` | 200, stored as `"New"` | regression |
| A9 | `PUT /api/todos/1abc` | 400, todo 1 unchanged | B3 |
| A10 | `PUT /api/todos/-1` and `/0x1` | 400 | B3 |
| A11 | `PUT /api/todos/9999` | 404 | regression |
| A12 | `PUT {title: "", completed: true}` | 400, **neither** field changed | update is all-or-nothing |
| A13 | GET, POST and DELETE smoke checks | same as before | scope |
| A14 | Leading-zero id `/api/todos/01` | 400 | B3 edge case (same idea as the earlier supplemental check) |

### 5b. Browser tests (`update-bugfix.browser.spec.cjs`), 3 cases

| # | Steps | Expected |
|---|---|---|
| U1 | Uncheck a completed todo, then reload | stays unchecked |
| U2 | Check it again, then reload | stays checked |
| U3 | Add, toggle and delete in the UI | still works |

### 5c. Local tests

The agent's `npm test` must pass, the original 9 tests must still be there,
and at least one new test must cover each of B1–B4 (checked by reading
`test.js` during scope review).

## 6. Grader validation (before any measured run)

Record these results in `VALIDATION.md`:

1. **Unchanged baseline:** A3–A7, A9, A10, A12 and A14 must fail, and the rest must pass. This proves the graders detect the bugs.
2. **Reference fix**, kept outside every agent workspace: all 14 API and 3 browser tests pass.
3. **Partial fix** (B1 only): only the B1 tests flip to passing. This proves the scores really separate partial fixes from full ones.
4. Run each suite 3 times to check for flaky tests.

## 7. Run procedure

The same as the edit-title README, with these changes:

- New start branch `benchmark-start-v3-bugfix`, and `git archive` exports `app` plus the 004 task file.
- New evaluator branch `benchmark-protocol-v3-bugfix`. The team agrees on one commit and compares grader hashes before running.
- Run IDs: `antigravity-bugfix-run01`, `copilot-bugfix-run01`, `claude-bugfix-run01`, `codex-bugfix-run01`.
- Same evidence package: before and after file lists, prompt, transcript, timing, tokens, grader logs and exit codes, scope review.

## 8. What gets reported per run

- API pass count out of 14, browser out of 3, local test count.
- Which of B1–B4 were fully fixed (the main comparison number).
- Scope: only `server.js` and `test.js` changed. Any other file is recorded as a violation.
- Time, tokens, and any corrections the operator had to give.

## 9. Open decisions for the team

- Rejecting `"false"` with 400 versus accepting it as `false`. The plan picks 400 because it is stricter and simpler to grade.
- Whether A12 (all-or-nothing updates) should count, or be reported separately as a stretch check.
