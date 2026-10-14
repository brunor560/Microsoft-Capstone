# Antigravity title-edit benchmark — edit-run01

The original implementation passed all 16 local tests, 12 independent
API tests, and 10 independent browser tests. No corrective coding
prompt was needed. Application correctness and workspace compliance
are reported separately below.

## Configuration

- Participant: Kapil Srikanth
- Date: October 14, 2026
- Run ID: antigravity-edit-run01
- Harness: Antigravity desktop app 2.22.0
- Interface: Fresh interactive conversation, Local execution
- Displayed model: Gemini 3.8 Flash Medium
- Environment: Windows / PowerShell; Node v24.21.0; npm 11.19.0
- Independent browser evaluator: Playwright 1.64.1 / managed Chromium
- Baseline commit: 4e258a96855d98edd10247f68c0b8265e53a8921
- Protocol commit: 02996447e01bb284939d9b1a83c45ab033c22fb9
- Task: pipeline/tasks/003-edit-todo-title.md
- Agent workspace: ZIP export containing only app/ and the task file,
  without Git metadata.
- Security preset: Default, inherited globally.
- Plan review policy: Always Ask, inherited globally.
- No custom rules were listed in the inspected global file, terminal,
  and MCP permission screens.
- Connected MCP servers, additional loaded instructions, and detailed
  sandbox enforcement were not independently verified.
- The operator helped prepare the task, evaluators, reference, and
  mutation checks beforehand. This attempt was not blind.

## Original results

| Suite | Passed | Failed | Exit code |
|---|---:|---:|---:|
| Baseline local tests before coding | 9 | 0 | 0 |
| Agent-executed local tests after coding | 16 | 0 | 0 |
| Independently rerun local tests | 16 | 0 | 0 |
| Independent API evaluator | 12 | 0 | 0 |
| Independent browser evaluator | 10 | 0 | 0 |

These suites overlap in coverage. Their counts are not a count of
distinct requirements.

The independent evaluators checked title updates, trimming, invalid
payloads, rejection without state changes, completion preservation,
existing endpoint behavior, inline editing, cancellation, reloads,
keyboard operation, save failures, retained drafts, literal title
rendering, and existing Add/toggle/Delete interactions.

The agent also created and ran its own Edge/CDP browser verification
script. Those checks are separate from the independent Playwright suite.

The operator subsequently checked the live app and reported that it
worked as intended. That manual check occurred after measured coding.

## Timing and human involvement

- Recorded elapsed time: 533.3346616 seconds, approximately 8 minutes
  53 seconds.
- Method: Manual PowerShell stopwatch started before prompt submission
  and stopped after the final report.
- The measurement includes window switching and approval waiting.
  It is not an exact automated prompt-to-final measurement.
- Ten permission requests were documented in supplied screenshots.
  The operator confirms approving each using "allow this time."
- Approval waiting was not separately measured.
- The transcript contains one initial user task prompt and no
  corrective coding prompt.
- No correction stage was performed.

## Implementation and scope review

- The project manifest records changes only to app/server.js,
  app/test.js, and app/public/index.html.
- Package files and the task file were unchanged in that manifest.
- Source review against the baseline content in the transcript
  confirmed preservation of all 179 original test-file lines after
  line-ending normalization. Seven tests were appended.
- PUT validates supplied titles before changing title or completion.
- The frontend renders titles through textContent and displays
  meaningful validation/save errors in the affected row's role="alert".
- Uploaded source hashes matched the recorded post-run manifest.

## Security, restrictions, and reporting accuracy

Application checks passed, but the agent created and executed
browser_test.js in Antigravity's internal scratch folder outside the
specified project workspace. Its script also configured a temporary
Edge profile outside the workspace.

This activity is disclosed as a deviation from the task's workspace
restriction. The project manifest cannot capture external files.
A human command approval does not establish benchmark scope compliance.

No external grader/reference access, commit, push, or MCP call appears
in the recorded tool actions. This observation is limited to the
preserved transcript and is not a complete filesystem or network audit.

The final report accurately stated 16 passing local tests. Its blanket
claim that all constraints were followed needs qualification because
of the external scratch activity.

Browser-discovery commands returned a failure before Edge was located
at its installed path. git status failed because the isolated snapshot
had no Git metadata. These did not prevent successful evaluation.

Before the measured attempt, git fetch encountered a directory-deletion
prompt. Both fixed commits were verified locally and exported directly.
This setup issue is separate from coding time.

## Recorded token usage

The full transcript contains 22 model-response records with token
fields. Their values were summed once using transcript_full.jsonl.
The other transcript repeats the same counters and was not added.

| Recorded field | Sum |
|---|---:|
| input_tokens | 137,848 |
| cache_read_tokens | 1,071,565 |
| output_tokens | 52,730 |

These are raw recorded field totals. Whether input_tokens includes
cached input and how reasoning tokens are categorized were not
independently verified. No combined billing total is claimed.
Dollar cost is unavailable, not zero.

See token-usage.json and the preserved transcripts for provenance.

## Evidence and limitations

- original/: preserved server.js, test.js, and index.html.
- conversation/: initial prompt, copied final report, approval notes,
  and preserved session transcripts; supporting screenshots where saved.
- before-files.csv and original-after-files.csv: project manifests,
  excluding installed node_modules.
- original-scope-diff.txt: recorded project changes.
- original-*-tests.txt and original-test-exits.txt: independent results.
- original-browser-report/ and original-browser-test-results/:
  browser evaluation artifacts.
- source-commits.txt and grader-hashes.csv: evaluator provenance.
- run-configuration.txt, original-start-time.txt, and
  original-timing.txt: configuration and timing evidence.

The saved source files are evidence copies. To run them, restore server.js
and test.js to app/ and index.html to app/public/ in a fresh baseline copy.

Passing these checks does not prove exhaustive correctness or complete
security. This is one attempt on one task with a particular model,
environment, permission policy, and informed operator. It does not
establish a general tool winner.

This results summary was AI-assisted and reviewed against the supplied
source files, transcripts, and operator-reported evaluation outputs.
