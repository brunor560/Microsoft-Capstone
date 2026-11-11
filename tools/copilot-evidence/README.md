# Copilot publication packets

These tools format and validate preserved evidence. They never launch Copilot,
execute a submitted solution, run graders, or change benchmark requirements.
Use the selected task's committed procedure, RUN-RECORD.md and OPERATOR-GUIDE.md
for collection; the unchanged dashboard importer defines publication fields.

## Prepare one attempt

Keep original events, workspace and logs private and immutable. Work on a
publication derivative with recorded redactions. Record verified runtime identity
in `runtime-observation.json` (`source: "owned assistant.message events"`,
`models`, `session_id`), raw `copilot-usage.json`, raw `timing.json`, actual
`original-test-exits.raw.json`, and the prescribed evidence files. Record full
`snapshot_commit`, `evaluator_commit` and `quality_commit` in both configuration
and source-commits.txt. Keep the requested selector and provider separate from
observed identity. Missing/mixed observations are blockers, not permission to
substitute the requested model.

Provide `publication-notes.json` using
[the notes example](templates/publication-notes.example.json), replacing its
instructions with this attempt's actual scope findings and observed effort or
reason it is unavailable. Notes are operator presentation, never human approval.
Preserve `review-status.json`, `operator.json`, `interventions.json`, approval and
setup notes; never create h-review.json for a human. One folder/README per attempt;
the batch summary belongs in the PR description, outside individual packets.

```sh
node tools/copilot-evidence/publication-records.mjs /absolute/publication/packet
```

The formatter derives its [README template](templates/run-readme.md), summary,
compatible model/timing/exit records, internal format validation and publication
hashes from this packet. It stages and validates proposed files in temporary
storage before writing. Contradictory existing model/timing/exit records block;
original logs, code and measurements are never rewritten. Repeating it is
idempotent. Existing README presentation can be refreshed with `--readme-only`;
this mode requires existing compatible model, timer and exit records.

If token-usage.json is absent, first verify that this installed Copilot export's
inputTokens includes cacheReadTokens/cacheWriteTokens and outputTokens includes
reasoningTokens, then explicitly use `--copilot-inclusive-tokens`. This generates
token-usage.json from one modelMetrics aggregate: input + output, without adding
cache/reasoning subsets or provider/agent duplicate summaries. An existing record
is validated against raw usage and never replaced. Unknown schema/coverage needs
operator investigation; do not guess. Missing optional subset fields remain
unavailable, while measured zero stays zero. Premium requests and AI credits are
not USD; unavailable provider cost stays null with a reason.

| Raw exit name | Publication key | Evidence filename |
|---|---|---|
| local-tests | local_exit | original-local-tests.txt |
| api-tests | api_exit | original-api-tests.txt |
| browser-tests | browser_exit | original-browser-tests.txt |
| acceptance | acceptance_exit | original-acceptance.txt |
| supplemental | supplemental_exit | original-supplemental.txt |
| security-runtime | security_runtime_exit | original-security-runtime.txt |
| security-scan | security_scan_exit | original-security-scan.txt |

Only performed suites have logs and exits. Put absent-suite reasons in
suite-applicability.json (`{"security_runtime":{"applicable":false,"reason":"..."}}`
for Task 006). Never write a "Not applicable" suite log or fabricated exit.
Mark required suites with `applicable:true` to block missing grading. Unknown
extra suite keys are rejected. Local/API subtests use the log's counting
convention; browser skipped counts are unavailable unless reported; static checks
have no skipped counter. Avoidance checks are listed individually.

Timing retains raw boundaries/process lifetime in timing.json and writes
`start_utc`, `end_utc`, `elapsed_seconds`, `method`, `approval_wait_seconds` to
timing.txt. UTC final-message comparison uses JavaScript millisecond precision;
raw submillisecond boundaries remain intact. A launch-to-final-report proxy
includes startup; a process-lifetime proxy also includes shutdown/export.
Neither is exact prompt acceptance latency. Setup/grading are excluded. Approval
waiting is unavailable unless independently measured in timing.json; never infer
zero from no interventions. The importer rounds elapsed seconds to one decimal.

## Required publication gate

Commit only the intended packet directories on an isolated results branch based
on fresh origin/results/all-runs. Then validate the committed tree:

```sh
node /absolute/tooling/tools/copilot-evidence/validate-publication.mjs \
  --repo /absolute/results-checkout --ref HEAD --base origin/results/all-runs \
  --importer-ref origin/master --run copilot/avoid-runNN \
  --report /absolute/private/first-attempt-validation.json --write-records
```

Use a unique external report path; reports are never overwritten. For multiple
packets repeat `--run` for each intended directory. The gate rejects changes
outside those directories, stale source/packet hashes, contradictory README,
wrong model/session/pins/tokens/suite fields, missing required artifacts, malformed
Markdown in the generated subset, broken evidence links, and placeholder suite
logs. It copies the exact importer bytes from the selected Git commit into
temporary storage, runs them against the committed results tree, and compares
model, timing method/rounding, suite counts/exits, tokens/cost, changed files and
human-review presence. Generated data stays temporary and is removed afterward.
Genuine failing suites/nonzero exits pass publication validation when faithfully
reported; this gate does not award benchmark success or human review.

`--write-records` first verifies the worktree still matches the checked inputs,
then writes a per-run publication-validation.json and refreshes publication hashes.
Commit these records; rerun without `--write-records` and with a new report path
against final HEAD before pushing. Validation records bind file hashes excluding
themselves and publication-files.sha256 to avoid a self-hash cycle. Old validation
reports remain historical evidence for their named commit; do not relabel them as
validating changed files. A changed packet requires a new gate/record.

Check the first completed attempt before launching any remaining batch attempts.
Validate every packet again before publication, including the intended-directory
allowlist. Inspect secrets, redactions, screenshots and pending review separately;
passing structural checks is not a privacy or human-approval substitute. Do not
commit generated dashboard data, modify the importer, merge, or deploy.

Offline regression checks (requires Node, Git, and the locally fetched
origin/master importer object; no network/model/grader execution):

```sh
node --test tools/copilot-evidence/publication-records.test.mjs
```

## Comparison findings (2026-11-11)

Inspected fresh origin/results/all-runs at 61ccc1a, PR #27 head 035e808,
protocol Task 006 at 6a01a4f, shared RUN-RECORD/OPERATOR-GUIDE, and unchanged
origin/master importer at d85c23b. No root/ancestor AGENTS.md exists in these
checkouts; course_artifacts/AGENTS.md does not govern these tool paths.

- PR #27 used Python dictionary/list representations in the README's result
  table, omitted separate pass/fail/skip/exit columns, and summarized total tokens
  without the input/output/cache/reasoning breakdown or linked evidence list.
  Its verified scalar model, timing.txt and exact suite-exit keys import correctly;
  retain their raw values and review state. Correct only presentation/derived
  metadata, not logs or candidate code.
- Codex avoid-run01/02 READMEs clearly label timing boundaries, cache inclusion,
  individual avoidance checks and pending second-rater review. They omit a full
  pinned-input list in the README and use legacy score prose. Follow protocol
  capture requirements and current scoring restrictions instead of copying those
  omissions/claims.
- Claude edit-run03 has a readable suite table and scope/approval limitations,
  but no skipped column; token wording combines Claude-specific additive cache
  fields with ambiguous "part of input" prose. Copilot inclusive aggregates must
  follow their own verified schema.
- Antigravity bugfix-run02's heading calls itself interactive run01, reflecting
  copied lineage. Its cache accounting/scoring is explicitly provisional and
  its post-run H score conflicts with the separately stated missing second rater.
  Preserve honest limitations; do not copy the run label, assumptions or score.
- Copilot bugfix-run01 imports correctly and distinguishes requested Sonnet from
  actual Auto-routed model, subset accounting, unavailable cost, approval waiting,
  scope findings and pending human review. It lacks the proposed uniform results
  columns; presentation alone does not define importer requirements.
- Protocol legacy score/deployment instructions differ from the current native
  measurement policy and this user's publication scope. This tool changes no
  requirements and computes no native composite score. PR #27 was already merged
  when inspected; presentation corrections require a separate results-only PR,
  not modification of historical records for other runs.

Limits: text summary parsing supports the inspected Node/TAP, Playwright and
check-per-line/verdict formats; new/ambiguous formats block for inspection. The
Markdown validator covers the generated template subset, not arbitrary Markdown.
Verified model observations still depend on truthful upstream event extraction;
formatting cannot prove OS isolation, fill missing data, approve humans, or
re-establish cohort eligibility. Importer moving baseline refs remain external
limitations; the gate does not rewrite them or benchmark requirements.
