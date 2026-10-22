# Approach A assessment workbench

A minimal command-line workbench for the documentation-only feature matrix (SRS Requirement 5, DDD M11; method in `course_artifacts/sources/feature_matrix_specification.md`). Python 3 standard library only. Run it from the repository root:

```bash
python3 -m tools.approach_a --help
```

## Boundaries

- It reads public official documentation only (HTTP GET). It never installs or runs an assessed developer tool and makes no model or benchmark calls (SRS Spec 5.4).
- The JSON in `assessment/` is the authoritative dataset. Markdown in `assessment/out/` is generated from it; do not edit it by hand. Those files are review artifacts, not a publication: nothing is published, scored or ranked (Spec 5.5 is out of scope).
- Research agents draft findings and the evidence-challenge pass flags problems. Neither is the independent team-member review that Spec 5.3 requires.

## Dataset (`assessment/`)

| File | Contents |
| --- | --- |
| `catalog.json` | 18 features, 7 categories, 5 statuses, generated from the matrix specification tables |
| `people.json` | Team roster and roles; only roster IDs are accepted as authors, reviewers or approvers |
| `candidates/<tool>/` | Prepared, unapproved profile proposals and research briefs (one JSON per feature, with page, section and quote) |
| `manifest.json` | Versioned profile manifest: P profiles, boundary confirmation, approval with the manifest hash |
| `cells.json` | Exactly one cell per feature and profile (18 x P) |
| `sources.json` | Shared official-source index: pages (title, access date, SHA-256, surfaces) and evidence entries `MATRIX:E01`... |
| `reviews.json` | Reviewer, decision, disposition and the hash of the cell as reviewed |
| `worklog.jsonl` | Append-only work log |
| `validation_report.json` | Latest validation result |
| `.cache/` | Cached page copies (gitignored) |

## Cell states

Each cell has one of the five method statuses plus an `assessment_state`:

| State | Meaning |
| --- | --- |
| `pending` | Research not done. The status shown is a placeholder, not a finding; it never passes validation |
| `drafted` | A research agent wrote it from a brief whose quotes were all re-verified in the cited sections |
| `challenged` | The automated evidence-challenge pass has run |
| `reviewed` | A roster member other than the author agreed with the cell as it stands now |

"Not established from documentation" is a completed finding only with a specific gap or conflict reason. It is never scored as zero, and "Assessment pending" is rejected as a gap reason.

## Commands

| Command | Purpose |
| --- | --- |
| `start` | Guided: select the tool, review the proposed surface, modes, platforms, tier and exclusions, adjust tier or exclusions, confirm the boundary. `--research` continues straight into research |
| `research` | Real progress through source discovery, research agents (one per profile), challenge pass, artifact generation and validation |
| `show F07` | One feature: finding, supported/unsupported/unestablished scope, sources (section, URL, access date), challenge flags, author and review state |
| `status` | Progress by profile and the last validation result |
| `validate` | Coverage, fields, evidence, approval and review checks; writes the report |
| `render` | Regenerate `assessment/out/` from the JSON |
| `approve --approver ross` | Record manifest approval (approver role only); any later manifest change makes it stale |
| `author --author <id> [--feature Fxx]` | Record the team member responsible for agent drafts |
| `review --reviewer <id> --decision agree\|disagree --note "..." [--disposition ...]` | Record an independent review; self-review is refused |
| `resume` | Continue an interrupted or partial run; completed steps are saved |
| `new --tool-name ... --docs-url https://.../` | Candidate for a tool with no prepared research; its cells stay pending (honest partial result) |
| `init [--force]` | Empty dataset (keeps catalog, roster and candidates) |

Options: `--offline` (cached pages only), `--refresh` (re-fetch), `--data DIR` (scratch dataset), `--rehearsal` (practice run on an unconfirmed, labeled boundary; validation blocks it). `APPROACH_A_STEP_DELAY=0.2` slows the progress display for an audience without changing results.

## What `validate` blocks on

Empty manifest (P = 0); duplicate or unnamed profiles; missing profile fields; proposed (unconfirmed) boundary; no approval or approval made stale by a manifest change; missing, extra or mismatched cells against 18 x P; unknown status; score or rank fields; pending cells; missing or dangling evidence or an unverified quote; Not established without a gap or conflict reason; challenge pass not run or a blocking flag (for example a claim transferred from another product surface); no named author; no review, a stale review, self-review or a reviewer off the roster; a disagreement without a resolved disposition. `validate` exits 1 until all are cleared.

A pass shows the dataset is structurally complete. It does not prove that each source supports its claim and is not by itself H-9 completion.

## Demo sequence

```bash
python3 -m tools.approach_a init --force
APPROACH_A_STEP_DELAY=0.15 python3 -m tools.approach_a start --research
                                   # choose the tool (default Antigravity, CLI surface), review and
                                   # confirm the boundary, then watch discovery, agents and checks
python3 -m tools.approach_a show F08   # one finding in detail
python3 -m tools.approach_a show F09   # a completed "Not established" finding and its gap reason
python3 -m tools.approach_a show F03   # pending research, not a finding
python3 -m tools.approach_a validate   # NOT ACCEPTED: approval, authors, reviews, pending F03
```

A tool with no prepared research (cells stay pending; discovery crawls the documentation):

```bash
python3 -m tools.approach_a new --tool-name "<Tool>" --docs-url https://<official docs>/ --surface cli
python3 -m tools.approach_a start --tool <tool-key> --research
```

## Tests

```bash
python3 -m unittest discover -s tools/approach_a/tests -t .
```

Synthetic datasets in temporary directories; no network.

## Known limits

- Briefs are drafted by an AI assistant from official pages. The workbench confirms each quote appears in its cited section; it cannot judge whether the quote supports the status. The author and reviewer do.
- People are not authenticated; the commit that adds a review or approval is its provenance.
- Section matching depends on the documentation's headings. A site change can make quotes fail; those cells stay pending rather than being guessed.

