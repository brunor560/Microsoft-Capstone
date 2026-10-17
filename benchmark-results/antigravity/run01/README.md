# Antigravity DELETE benchmark — run01

- Participant: Kapil Srikanth
- Original run date: October 7, 2026
- Tool: Antigravity
- Model: Gemini 3.8 Flash Medium, as recorded by the participant
- Starting commit: be98d692807da26dac3c3a720d4d5cf157e9717d
- Task: pipeline/tasks/001-add-delete-endpoint.md
- Environment: Windows; Node v24.21.0; npm 11.19.0

## Original attempt

- Agent-reported local tests: 8 passed, 0 failed.
- Independent acceptance suite: 9 passed, 0 failed.
- Direct DELETE /api/todos/01 check: expected 204, received 400.
- Code review found that the implementation rejected leading-zero IDs
  and its generated tests incorrectly classified 01 as invalid.
- Antigravity displayed approximately 6 minutes. This was a rounded UI
  duration, not a verified stopwatch measurement.

## Correction after human feedback

- One corrective feedback prompt identified the leading-zero mismatch.
- Three command approval prompts were observed during correction.
- Agent-reported local tests: 9 passed, 0 failed.
- Independent acceptance suite: 9 passed, 0 failed.
- Direct DELETE /api/todos/01 check: expected 204, received 204.
- Antigravity displayed approximately 4 minutes. This was a rounded UI
  duration, not a verified stopwatch measurement.

## Review and limitations

- Manual comparisons found no differences in package files, the task
  prompt or frontend compared with the starting repository.
- Original and corrected server/test files are preserved separately.
- The original independent suite omitted leading-zero IDs.
- A separate supplemental evaluator was added after discovering that gap.
- The supplemental evaluator passed against the reference implementation
  and failed against the preserved original implementation.
- Saved JavaScript files are evidence copies. Their original filenames
  were server.js and test.js; they are not standalone runnable apps.
- Exact original prompt-to-final timing, original approval count and token
  usage are not established by the evidence summarized here.
- Model/version details should be checked against historical session
  evidence where available.
- This is one pilot task and does not establish a general tool winner.

## Verification of preserved outputs — October 14, 2026

The saved original and corrected implementations were reconstructed
separately using baseline commit
be98d692807da26dac3c3a720d4d5cf157e9717d.

These were verification runs of existing outputs, not new Antigravity
coding attempts. Neither preserved implementation was modified.

| Implementation | Local tests | Main evaluator | Supplemental evaluator |
|---|---|---|---|
| Original | 8 passed, 0 failed | 9 passed, 0 failed | 0 passed, 1 failed |
| Corrected | 9 passed, 0 failed | 9 passed, 0 failed | 1 passed, 0 failed |

The original implementation returned HTTP 400 where HTTP 204 was required
for leading-zero deletion. The corrected implementation passed the
supplemental evaluator.

### Evidence

Verification files are in `verification-20261014-112703/`:

- Original and corrected installation and test transcripts.
- Test exit codes.
- Baseline and verification source commits.
- Verification environment: Windows, Node v24.21.0, npm 11.19.0.
- Raw grader hashes and hashes after CRLF-to-LF normalization.

Original exit codes: local 0, acceptance 0, supplemental 1.
Corrected exit codes: local 0, acceptance 0, supplemental 0.

### Grader hash reconciliation

After normalizing Windows CRLF line endings to LF in memory,
both grader hashes exactly matched the hashes recorded for the
Copilot run. Neither grader file was modified.

Normalized SHA-256 hashes:

- Acceptance: `6e366e23e7aef27c687448c1e758dd9b990fb7bf989fd41a388029dd70dec6cb`
- Supplemental: `3c36a27c48a6e7f485280570bc8fae9394cbc63d8283997447c56e2d0da5e7d0`

This resolves the observed grader-hash discrepancy as a line-ending
difference.

The October 14 verification does not reconstruct historical timing,
token usage, approval counts or a complete original file-scope audit.