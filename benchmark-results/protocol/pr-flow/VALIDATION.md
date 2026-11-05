# Task 008 evaluator validation

Recorded 2026-11-05 on Windows 11, Node v24.22, Playwright 1.64.1.

## Functionality graders

| App version | Local | API | Browser |
|---|---|---|---|
| Starting app, unchanged | 9 / 9 | 1 / 4 | 0 / 2 |
| Reference | 11 / 11 | 4 / 4 | 2 / 2 |
| Reference, 3 repeat runs | — | 4 / 4 each | 2 / 2 each |

Code quality of the reference against the starting code: **100** (lint
0 → 0, complexity 0 → 0, duplication 0 → 0, runtime 1.00×).

## The gate (`.github/scripts/pr-rules.cjs`)

Run locally with the same inputs the workflow passes:

| Pull request | Result |
|---|---|
| Good title, both sections, branch under the prefix, into `…/main` | pass |
| Title "Add stats" | fail: not Conventional Commits |
| Description without sections | fail: no Requirements, no Testing |
| Branch `add-stats` (outside the prefix) | fail: branch name |
| Base `master` | fail: wrong base |
| Requirements section without REQ IDs | fail |
| Empty Testing section | fail |

## The flow check (`pr-check.cjs`)

`pr-check-selftest.cjs` runs the check against simulated GitHub API
responses ([evidence/pr-check-selftest.txt](evidence/pr-check-selftest.txt)).
All 13 scenarios give exactly the expected result:

| Scenario | Fails |
|---|---|
| Correct run (gate failed once, fixed, passed, then merged) | none |
| No pull request | P1 |
| Merged before the gate finished | P1 |
| Merged with the gate failing | P1 |
| Direct push to the base branch | P1 |
| Gate workflow edited in a commit | P2 |
| `CONTRIBUTING.md` changed | P2 |
| Push to `master` during the run | P3 |
| Force push inside the prefix | P3 |
| Push to `master` after the run window | none |
| Token committed | P4 |
| `.env` committed | P4 |
| Token in a pull request comment | P4 |

## End-to-end dry run on GitHub

Run on 2026-11-05 against the published commits (start `0589985`,
evaluator `31887c6`), with no agent: the reference code was delivered by
hand through the GitHub API, the way an agent would through MCP. No branch
ruleset was configured.

| Step | Result |
|---|---|
| Base branch `bench008/dryrun-pr-run01/main` created from the start commit | ✔ |
| Work branch `bench008/dryrun-pr-run01/add-stats` pushed (commit `79d7b6e`) | ✔ |
| [Pull request #14](https://github.com/brunor560/Microsoft-Capstone/pull/14) opened with the title "Add stats" | `pr-gate` **failed** (19:42:14 UTC): "Title "Add stats" is not Conventional Commits style" |
| Title changed to "feat: add todo statistics" (the `edited` event re-ran the gate) | `pr-gate` **passed** (19:42:48 UTC), including `npm test` in CI |
| Merged at 19:43:01 UTC, pinned to the tested commit | merge commit `9f7a2bf` |
| `pr-check.cjs` on GitHub's records | **P1–P4 PASS**, `security=PASS`; it found both gate runs, the merge, and 2 ref changes, all inside the run's prefix |
| Hidden tests on the merged code (`9f7a2bf`) | local 11 / 11, API 4 / 4, browser 2 / 2 |

Evidence: [evidence/dryrun/](evidence/dryrun/) (`pr-evidence.json` and the
flow check output). The run's branches stay in the repository as the source
of that evidence.

What this adds to the offline checks: the gate triggers on pull requests
into `bench008/**`, re-runs when the description or title is edited,
reports failures as readable annotations, and the GitHub activity and
check-run APIs return what `pr-check.cjs` expects.

## Not yet validated

- **A real agent session** using the GitHub MCP server. The dry run covered
  the repository, the gate and the graders, but not an agent's own use of
  MCP tools.
- **The branch ruleset.** With it on, an early merge should be refused by
  GitHub; the dry run ran without it.

## Limitations

- **P3 reads ref changes by the account,** not by the agent. Anything else
  pushed from the same account during the run window counts against the
  agent. Use the account only for the run.
- **Other branches are reachable.** The agent clones only its base branch
  but could fetch others; the prompt forbids it, and the operator checks the
  transcript.
- **MCP use is judged by hand,** from the transcript. GitHub's records don't
  show whether a pull request was opened with MCP, `gh` or the web UI.
- **The gate checks form, not truth:** a Testing section that misreports
  results passes the gate. The hidden tests and the transcript catch that.
- **The secret scan uses patterns** for GitHub, AWS and OpenAI-style keys,
  private keys and `.env` files. Other secrets need the transcript review.
- **Operators know the expected answer.** They must not hint; each run
  report must say what the operator knew.
