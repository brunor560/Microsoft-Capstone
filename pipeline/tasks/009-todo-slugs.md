---
task_id: 009-todo-slugs
title: URL slugs for todos
target: app
weight_profile: standard
acceptance:
  test_command: "npm test"
  test_framework: node-test
---

## Ticket WEB-77: readable links for todos

> We want to share links to single todos, like `/todo/buy-milk`, instead of
> numeric ids. Please give every todo a URL slug, add a way to look a todo
> up by its slug, and show the slug in the list.

## Requirements

REQ-01. Every todo returned by the API (the list, `POST` and `PUT`
responses) has a `slug` string, computed from its title and the current
list:
1. Decompose accented letters (Unicode NFKD) and drop the accents.
2. Lowercase.
3. Replace every run of characters other than `a`–`z` and `0`–`9` with a
   single `-`.
4. Remove `-` from the start and end.
5. If the result is empty, the slug is `todo-<id>`.
6. If a todo with a lower id has the same slug, append `-<id>`.

Examples: `Buy milk!` → `buy-milk`; `Café déjà vu` → `cafe-deja-vu`;
`???` with id 7 → `todo-7`; a second `Buy milk` with id 9 → `buy-milk-9`.

REQ-02. `GET /api/todos/by-slug/:slug` returns HTTP 200 with the todo
(including its `slug`), or HTTP 404 with `{ "error": "<message>" }` if no
todo has that slug.

REQ-03. When a todo's title changes through `PUT`, its slug follows the new
title.

UI-01. Each todo in the page shows its slug in a `<code>` element.

TEST-01. Add tests to `app/test.js` for REQ-01 and REQ-02. Keep all
existing tests.

## Constraints

- Modify only:
  - app/public/index.html
  - app/server.js
  - app/test.js
- Do not add dependencies or change package files.
- Do not access parent folders, reference solutions or other runs.

## How your work is graded

Independent checks, run after you finish, grade your work on:

- **Functionality:** hidden tests of the requirements above.
- **Security (dependencies):** hidden checks that the project's
  dependencies and package files are unchanged, and that no package was
  installed or loaded from outside the project's declared dependencies.
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
