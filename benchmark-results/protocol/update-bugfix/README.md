# Task 004 and 005 procedures

The procedures, graders, references and validation evidence for the later
tasks are kept on their own branches, not copied here:

| Task | Branch | Folder on that branch | Commit used by the runs |
|---|---|---|---|
| 004 Fix update validation | `benchmark-protocol-v3-bugfix` | `benchmark-results/protocol/update-bugfix/` | `1e690f91a11dd1b37c796345a511d6791476efbc` |
| 005 Todo priority (hidden prompt-injection traps) | `benchmark-protocol-v4-injection` | `benchmark-results/protocol/injection-priority/` | `cef49cca7a3298cda4dc18660b434c60d871e2e7` |

Each folder has a README (the full run procedure), ACCEPTANCE.md (criteria
with before and after evidence) and VALIDATION.md.

The task 005 branch contains the trapped app and must never be merged into
`master`.
