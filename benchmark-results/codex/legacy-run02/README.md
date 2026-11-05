# codex-legacy-run02

Independent benchmark evidence; user confirmed frozen commit and first-set grader hashes on 2026-11-05.

## Configuration
run_id=codex-legacy-run02
participant=Joseph B.
date=2026-11-05
timezone=America/New_York
tool=codex-cli 0.166.0-alpha.6
interface=headless CLI
model=gpt-6-luna
reasoning=low
approval=never
sandbox=workspace-write; windows.sandbox=elevated
node=v24.22.2
npm=11.19.1
os=Microsoft Windows NT 10.0.26200.0
playwright=Version 1.64.1
fresh_start=ephemeral, memories and external agent memory import disabled, ignore user config and rules, project_doc_max_bytes=0, CODEX_* removed
team_commit_agreement=user confirmed 2026-11-05
grader_hashes=first set for this task; nothing to compare yet

## Timing
start_utc=2026-11-05T20:04:12.1745479+00:00
end_utc=2026-11-05T20:05:03.0223781+00:00
elapsed_seconds=50.8471095
method=Stopwatch immediately before prompt submission through CLI process exit; exact final delivery time unavailable
approval_wait_seconds=0
cli_exit=0

## Usage
input=180313, cached input=131072 (included in input), output=1973, reasoning output=73; cost unavailable.

## Results
local: ℹ tests 11; ℹ pass 11; ℹ fail 0
API: ℹ tests 7; ℹ pass 7; ℹ fail 0
browser:   ok 2 legacy-export.browser.spec.cjs:52:1 › UI-02: add, toggle and delete still work (340ms)    2 passed (1.5s)
L1=PASS  header, CRLF line endings, empty and missing list
L2=PASS  row order, id padding and DONE column
L3=PASS  cutting, spreadsheet guard, and unchanged output for titles that need no quoting
L4=PASS  tests catch the bug (with original module: 1 failed, 10 passed; with reference fix: 0 failed, 11 passed)
security=PASS

## Limitations
No H score until an independent teammate reviews interventions.json. Exact final-report delivery time is not known; timing ends at CLI process exit. No commits or pushes were made for this run.
See scope-review.txt, operator.json, interventions.json and original test logs for details.

## Code quality
lint         PASS  baseline 0 candidate 0
complexity   PASS  baseline 0 candidate 0
duplication  PASS  baseline 0 candidate 0
runtime      PASS  baseline 292 candidate 291.5 ratio 0.998
score 100 (100/100)

Token-efficiency and independent-review limitations: see scoring-notes.txt.
