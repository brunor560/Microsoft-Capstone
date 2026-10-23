# Task 004 and 005 procedures

The procedures, graders, references and validation evidence for the later
tasks are kept on their own branches, not copied here:

| Task | Branch | Folder on that branch | Commit used by earlier runs | Commit for new runs |
|---|---|---|---|---|
| 004 Fix update validation | `benchmark-protocol-v3-bugfix` | `benchmark-results/protocol/update-bugfix/` | `1e690f91a11dd1b37c796345a511d6791476efbc` | `eb848b67ad0fcbdcb35c5058d13773de9cfaa6cd` |
| 005 Todo priority (hidden prompt-injection traps) | `benchmark-protocol-v4-injection` | `benchmark-results/protocol/injection-priority/` | `cef49cca7a3298cda4dc18660b434c60d871e2e7` | `27492d43654bd802b3749e12df1c1be6742f6d92` |

The newer commits have the same app and graders. They add a fuller "What to
report" section to the task file and the [RUN-RECORD.md](../RUN-RECORD.md)
checklist. The team must confirm them before new runs.

Each folder has a README (the full run procedure), ACCEPTANCE.md (criteria
with before and after evidence), VALIDATION.md and RUN-RECORD.md.

The task 005 branch contains the trapped app and must never be merged into
`master`.
