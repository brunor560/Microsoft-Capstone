# Antigravity CLI — Task 001 — run01

## Configuration
- Operator: Kapil Srikanth.
- Date: 2026-10-29.
- Antigravity CLI 1.4.10, interactive.
- Model: Claude Sonnet 4.6 (Thinking).
- Conversation: 353df327-ead0-45df-841e-8e74ae44bbd4.
- Baseline: 4fa0659150b42fc9b01b1e68e51f07a8535c57e0.
- Evaluator commit: see source-commits.txt.
- Manual approvals; terminal sandbox disabled according to CLI snapshots.

## Original results
| Check | Result |
|---|---|
| Baseline local tests | 4 passed, 0 failed |
| Baseline main evaluator | 2 passed, 7 failed |
| Baseline supplemental evaluator | 0 passed, 1 failed |
| Candidate local tests | 15 passed, 0 failed |
| Candidate main evaluator | 9 passed, 0 failed |
| Candidate supplemental evaluator | 1 passed, 0 failed |
| Candidate exit codes | All 0 |
| Elapsed time | 77.080 seconds |
| Permission approvals | 6 |
| Corrective prompts observed | 0 |

No correction round was needed. Timing includes approval waiting and
window switching; approval waiting was not measured separately.

## Scope
Workspace manifests show changes only to app/server.js and app/test.js.
The full source snapshot, excluding installed dependencies, is under
original/. Application files are under original/app/.

The external evaluators were exported unchanged from the recorded
protocol commit and kept outside the coding workspace.

## Tokens
Nine distinct status usage updates were reconstructed:
- Input fields: 15,354.
- Output fields: 5,057.
- Input plus output: 20,411.
- Cache-read fields: 101,417.
- Total if cache reads are additional: 121,828.

Output sum matches the final cumulative output counter.
Final cumulative input is 17,941 and differs from summed input fields.
Cache accounting remains unverified. No verified billing total,
dollar cost or token-efficiency score claimed.

## Report accuracy
The reported 15 passing local tests match the independent rerun.
The agent reports preserving four baseline tests and adding eleven.
The external graders confirm the tested DELETE behaviors, including
leading-zero IDs and preservation of existing endpoint behavior.
The final report discloses the editing retry but omits the failed first
test-command execution visible in the conversation and recording.

## Evidence and limitations
- Conversation is a manual copy with collapsed tool details.
- Recording supports approval and execution review.
- Workspace manifests do not establish activity outside that workspace.
- Memory, global instructions and integrations were not independently verified.
- No browser checks were performed for this API task.
- Code-quality grading and independent teammate H review remain outstanding.
- No H score or overall score claimed.
- Dashboard and shared-results integration remain outstanding.


## Published in results/all-runs (added 2026-10-29)

- **Interface:** Antigravity **CLI** 1.4.10, interactive. It is filed under
  `antigravity/` with the Antigravity IDE runs for simplicity, so on the
  dashboard it is grouped with Antigravity runs that used the same model.
- **Original location:** `benchmark-results/antigravity-cli/run01/` on
  `results/antigravity-cli-sonnet` (Kapil Srikanth). That branch holds the full
  evidence: screen recording, conversation, telemetry snapshots, browser
  reports and the full original workspace.
- **This copy** keeps only the files needed for analysis. The agent's files are
  flattened from `original/app/` to `original/`, and UTF-16 text files were
  converted to UTF-8.
- **Token totals are provisional:** reconstructed from interactive status
  snapshots, with input and cache-read counts reported separately.
- **Human collaboration** has no second-rater `h-review.json` yet.
