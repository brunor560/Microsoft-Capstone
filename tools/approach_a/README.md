# Approach A assessment workbench

A minimal command-line workbench for the documentation-only feature matrix (SRS Requirement 5, DDD M11; method in `course_artifacts/sources/feature_matrix_specification.md`). Python 3 standard library only. Run it from the repository root:

```bash
python3 -m tools.approach_a --help
```

## Quick start with `./matrix`

From the repository root:

```bash
./matrix                                      # status and a short guided menu
./matrix use assessment/research/2026-11-08     # save this checkout's local selection
./matrix use --show                            # inspect selection and resolved path
./matrix use --clear                           # return to environment/default selection
./matrix --data /path/to/scratch start          # propose and explicitly confirm a boundary
./matrix --data /path/to/scratch resume --no-draft
./matrix --data /path/to/scratch review         # source packet and checked-cell review queue
./matrix --data /path/to/scratch preview        # labeled draft + loopback server; Ctrl+C stops it
```

Selecting the November 8 example above does not change its records. Use a scratch
copy for practice; never record fictional authors, reviews or approvals in real
data. `use` stores an absolute path in ignored `.matrix-data.json` per checkout.
Resolution is explicit `--data`, then `APPROACH_A_DATA`, saved selection, and
finally `assessment/`. The resolved path is printed before every guided action;
a missing saved directory is an error rather than a silent fallback. Opening the
menu only reads status and current checks. With no terminal, `./matrix` prints
status and exits; guided `start`/`review` also show status without prompting.
Explicit preview and export commands still perform their requested actions.

`start` offers prepared-candidate and copy-profile paths, with the candidate's
default surface for prepared setup. Both use one editable boundary summary and
explicit confirmation, then offer research only for the newly created profile. Before paid drafting, the launcher shows the configured
Azure deployment, API version and effective request/token/spending limits and
asks for confirmation (default no). `--no-draft` uses prepared/saved briefs only.
The actual returned model version is recorded when available. Human authorship,
independent review and manifest approval remain separate explicit decisions.

To create another tier from an existing CLI profile, work in a scratch copy:

```bash
review_dir=$(mktemp -d /private/tmp/matrix-tier.XXXXXX)
cp -R assessment/research/2026-11-08/. "$review_dir/"
./matrix --data "$review_dir" start --no-draft
```

Choose `copy`, then `codex-cli` (or your existing CLI profile), and enter the
intended exact account/tier. The summary marks **INHERITED setup**, **EDITED**,
and **NEEDS INPUT** fields. Type a field name to jump directly to it, for example
`platforms`, `modes`, `exclusions` or `documentation_entry_points`; list values
use semicolons. Enter `version` and provide a documented version or
`unversioned: <explanation>`, then enter `source_access_date` with the date you
actually reviewed the official documentation (`YYYY-MM-DD`). Versions and access
dates are not inherited as established facts. Required blanks and proposal/TBD
placeholders block confirmation. Check inherited setup against the intended tier,
including platform-specific interface descriptions.

Type `confirm`, select your actual roster ID, and explicitly answer `y` to add.
Before that confirmation, cancellation (`q`, EOF, or `n` at final confirmation)
writes no manifest or cells. A matching boundary instead offers the existing
profile and shows pending research and review counts, without writing. Scope
comparison ignores source-access dates, labels, list order and capitalization;
a genuinely different tier, platform, mode, component boundary or documented
version can coexist. Existing IDs stay unchanged; new variants receive stable
IDs with a scope suffix when the candidate's base ID is occupied.

A confirmed profile gets 18 fresh pending cells, a new manifest version and no
manifest approval. Findings, evidence references, authors and reviews are not
copied; the original records stay attached to the original profile. Official
entry points are inherited only as editable research inputs, constrained to the
candidate's official prefixes. Research still resolves the tool/surface inputs
through `tool_key` and `surface`, independently of the new profile ID. Copies and
changed boundaries do not reuse the old scope's prepared findings; `--no-draft`
leaves their cells pending until new profile-specific briefs exist. Model drafting
receives the exact tier, platforms and modes; every resulting finding still needs
human verification and independent review. The existing research offer is limited
to the new profile, including its evidence-challenge pass.

For a tool without a prepared candidate, the `new` menu entry points to the
existing `./matrix new` command; then choose `prepared` on the next start. The
module CLI's `start`, `new`, research flags and scripted syntax remain unchanged.
Bulk creation is deferred.

`review` opens the only profile needing review, or lists profiles with remaining
cell-review counts. It reuses the packet, individual exceptions and `p` checked-cell
batch action, including confirmation and stale-review checks. Missing authors or
boundary/approval problems can be resolved with `./matrix blockers`.

`preview [--port 4174]` uses the standard draft destination and existing server:
`http://127.0.0.1:4174/feature-matrix/?preview=matrix.preview.json`. It does not
open a browser. The menu offers a local accepted export only when the whole
manifest passes; the exporter independently revalidates on every invocation:

```bash
./matrix export              # local assessment/preview/matrix.accepted.json
./matrix export --public     # explicit public projection; requires committed matching inputs
```

Public export retains all Git provenance and destination checks. See the
scratch-to-public sequence below before using `--public`. No launcher action
pushes or deploys. Existing commands remain available (`./matrix blockers`,
`./matrix review-packet`, etc.). `python3 -m tools.approach_a` and its current
syntax are unchanged for scripts; it ignores `.matrix-data.json`. Use the module
CLI for scripted setup/review, including `start --yes` or rehearsal runs.

## Boundaries

- It reads public official documentation only (HTTP GET). It never installs, runs or tests an assessed developer tool and makes no benchmark calls (SRS Spec 5.4).
- By default, `start --research`, `research` and `resume` send documentation excerpts to Azure OpenAI to draft missing briefs (SRS Spec 5.4.2 as amended Oct. 22). `--no-draft` turns this off. See "Model-assisted drafting" below.
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
| `reviews.json` | Reviewer, decision, disposition and versioned hashes of the reviewed cell, cited evidence and profile |
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
| `blockers` | Interactive walkthrough: current blocking keys → profile → blocker type → one item at a time, with skip, recheck and quit |
| `render` | Regenerate `assessment/out/` from the JSON |
| `approve --approver ross` | Record manifest approval (approver role only); any later manifest change makes it stale |
| `author --author <id> [--feature Fxx]` | Record the team member responsible for agent drafts |
| `review --reviewer <id> --decision agree\|disagree --note "..." [--disposition ...]` | Record an independent review; self-review is refused |
| `resume` | Continue an interrupted or partial run; completed steps are saved |
| `new --tool-name ... --docs-url https://.../` | Candidate for a tool with no prepared research; its cells stay pending (honest partial result) |
| `export-publication [--mode accepted\|preview]` | Prepare the reviewed projection of the matrix as one JSON payload for the site (M13 input; publication is the existing Pages workflow). `accepted` (default) refuses unless the whole manifest passes `validate`; public output additionally requires inputs matching their committed repository path. It writes `dashboard/feature-matrix/data/matrix.json` with no names or roster IDs. `preview` keeps draft cells with workflow labels and writes `assessment/preview/matrix.preview.json`, never inside `dashboard/`. Reads a scratch copy; the dataset is not modified |
| `serve-preview [--port N]` | Serve the feature matrix page locally (127.0.0.1 only, read-only) with the draft file from `assessment/preview/`. See `course_artifacts/references/Feature_Matrix_Publishing_Guide.md` |
| `init [--force]` | Empty dataset (keeps catalog, roster and candidates) |

Options: `--offline` (cached pages only), `--refresh` (re-fetch), `--data DIR` (scratch dataset), `--rehearsal` (practice run on an unconfirmed, labeled boundary; validation blocks it). `APPROACH_A_STEP_DELAY=0.2` slows the progress display for an audience without changing results.

## What `validate` blocks on

Empty manifest (P = 0); duplicate or unnamed profiles; missing profile fields; proposed (unconfirmed) boundary; no approval or approval made stale by a manifest change; missing, extra or mismatched cells against 18 x P; unknown status; score or rank fields; pending cells; missing or dangling evidence or an unverified quote; Not established without a gap or conflict reason; challenge pass not run or a blocking flag (for example a claim transferred from another product surface); no named author; no review, a stale review, self-review or a reviewer off the roster; a disagreement without a resolved disposition. `validate` exits 1 until all are cleared.

A pass shows the dataset is structurally complete. It does not prove that each source supports its claim and is not by itself H-9 completion.

## Demo sequence

```bash
python3 -m tools.approach_a init --force   # deletes saved drafts: run it before pre-drafting, not after
APPROACH_A_STEP_DELAY=0.15 python3 -m tools.approach_a start --research
                                   # choose the tool (default Antigravity, CLI surface), review and
                                   # confirm the boundary, then watch discovery, Azure drafting of
                                   # features without a saved draft, agents and checks
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

## Model-assisted drafting (on by default)

```bash
python3 -m tools.approach_a start --tool antigravity --research   # drafts missing briefs with Azure
python3 -m tools.approach_a research --max-requests 3             # small test
python3 -m tools.approach_a resume                                # continue
python3 -m tools.approach_a research --no-draft                   # no Azure: prepared briefs and saved drafts
```

- **Defaults** (in `drafting.json`): `default_draft` is `azure` (set it to `off` to make drafting opt-in), and `default_env_file` is `pipeline/autogen/.env`, relative to the repository root.
  - `--draft azure` and `--env-file PATH` still work and override these defaults.
  - Order of precedence: `--draft`/`--no-draft`, then `$APPROACH_A_DRAFT` (`azure` or `off`), then `default_draft`. The tests set `APPROACH_A_DRAFT=off`, so they never reach Azure.
- **When Azure is not available, the command stops with an error** (exit 2) and names `--no-draft` as the way out. This covers:
  - a missing env file or variable, or `--offline` combined with drafting: research is refused before anything is logged as started or fetched;
  - refused credentials (401/403/404), no response, or 429/5xx after retries: the run stops before assessment, keeps the drafts already saved, and logs `research_stopped`. `resume` continues once Azure responds.

  A bad request for one feature (for example HTTP 400) leaves only that feature pending. Reaching a limit stops drafting, and the run continues with the drafts it has.
- **Connection.** The workbench reads the `AZURE_DEV_ENDPOINT`, `AZURE_DEV_DEPLOYMENT`, `AZURE_DEV_API_VERSION` and `AZURE_DEV_API_KEY` variables from the env file, or from the environment if no file is given.
  - The variable names are set in `drafting.json`, separately from assessment profiles.
  - The key is never printed, logged or written. The work log records only the endpoint host, deployment, API version and the returned model version.
  - The env file must stay gitignored (`pipeline/autogen/.gitignore`).
- **One request per feature, sequentially.** The model sees only the highest-matching sections of the official pages that discovery fetched for that surface; release-note sections are capped at two. It returns a brief in the same format as a prepared one.
  - Drafts go to `assessment/drafts/<profile>/Fxx.json` with provenance: deployment, model, prompt version, request ID, token use and estimated cost.
  - Unusable responses go to `Fxx.rejected.json`, and the cell stays pending.
  - Later runs reuse saved drafts and skip earlier rejections; `--redraft` retries the rejections. `init --force` deletes the drafts.
- **Same gates as before.** Every quote is re-checked inside its cited section, and failed quotes are dropped. If none verify, the cell stays pending. The challenge pass adds a `model_drafted` note. A named author, an independent reviewer and manifest approval are still required.
- **Limits** (`tools/approach_a/drafting.json`, key `limits`):

| Key | Default | Meaning |
| --- | --- | --- |
| `max_requests_per_run` | 24 | Requests per run, retries included (`--max-requests`) |
| `max_input_tokens_per_request` | 6000 | Prompt size; excerpts are trimmed to fit |
| `max_output_tokens_per_request` | 1200 | `max_tokens` sent to Azure |
| `max_tokens_per_run` | 160000 | Input plus output per run (`--token-budget`) |
| `requests_per_minute`, `tokens_per_minute` | 10, 10000 | Pacing to the deployment's rate limit (read from Azure on Oct. 22) |
| `timeout_seconds`, `max_retries` | 60, 2 | Per attempt; retries on 429 and 5xx errors, honoring `retry-after` |
| `max_cost_usd_per_run` | 1.00 | Estimated from returned usage (`--max-cost`) |
| `max_cost_usd_total` | 5.00 | Cumulative cap across runs, from `model_spend.jsonl` |

- **Spending checks.** Before every attempt the workbench checks the worst case (estimated input plus the full output allowance) against every limit, and stops drafting if a request would exceed one. A request with no response is charged at that worst case.
  - The prices in `drafting.json` ($0.40 input and $1.60 output per million tokens) are assumed and not yet checked against Azure pricing, so costs are estimates, not invoices.
  - `tools/approach_a/model_spend.jsonl` is the cumulative ledger. Deleting it resets the $5 cap, so keep it.
- **Speed.** Pacing reserves input plus `max_output_tokens_per_request` per request, matching how Azure counts against the per-minute token limit. At 10,000 tokens per minute with the defaults (6,000 + 1,200), the deployment allows about one request per 43 seconds, so all 18 features take about 13 minutes.
  - At 3,000 + 1,200 it allows about 2 requests per minute, or about 9 minutes, but the model gets less context.
  - Raising the deployment's capacity in Azure is the other option.
  - For a short live demo, draft most features beforehand. Saved drafts are reused, so a live run with `--max-requests 3` shows only the remaining features being drafted.

## Tests

```bash
python3 -m unittest discover -s tools/approach_a/tests -t .
```

Synthetic datasets in temporary directories; no network. The drafting tests use a fake Azure endpoint and a fake key.

## Known limits

- Briefs are drafted by an AI assistant (prepared briefs) or by Azure OpenAI (default; `--no-draft` turns it off) from official pages. Excerpt selection is keyword-based, so a relevant section can be missed. The workbench confirms each quote appears in its cited section; it cannot judge whether the quote supports the status. The author and reviewer do.
- People are not authenticated; the commit that adds a review or approval is its provenance.
- Section matching depends on the documentation's headings. A site change can make quotes fail; those cells stay pending rather than being guessed.


### Feature matrix Shortlist (local review)

The direct `/feature-matrix/` route has Overview and Shortlist views. Overview keeps
its horizontal profile cards, matrix, and evidence details. Shortlist has two native
multi-select dropdowns: recorded profile tiers grouped by tool, and searchable
requirements grouped by the specification's six feature areas. Sort by match group
or tool name. Tabs preserve both views' filters; shortlist selections and sort also
survive reload and browser Back/Forward through URL parameters. Each requirement
has a normal link to its exact profile/feature detail, even when Overview filters
hide the corresponding matrix row. Enter activates links and picker summaries;
Space toggles checkboxes; Escape closes a picker and returns focus to its summary.

Shortlist reads the existing `approach-a/publication/1` fields. A tier is the
profile's recorded `account_and_tier` text, never an inferred list of vendor plans.
Missing or explicitly undecided tiers appear as **Tier not established**. Distinct
profiles remain distinct even when they share a tool or tier label.

- **Documented match:** every selected feature has documented whole-feature
  support on the same eligible profile and recorded tier, with matched source
  quotations and no explicit unsupported or unestablished scope.
- **Documented gap:** any selected feature explicitly records unsupported scope
  backed by matched source quotations, including partial support with a gap.
- **Needs verification:** otherwise, research/tier/evidence is missing or
  inconclusive. This includes conflicting/stale/disputed findings and capabilities
  whose required configuration or implementation setup is not established.
  Documented setup can support a match within the recorded profile boundary;
  delivery mechanisms are explained rather than ranked.

These are requirement groups, not capability scores or benchmark rankings. Each
requirement retains its cell's supported, unsupported and unestablished scope,
setup and constraints. Draft findings may illustrate groups but remain unreviewed;
quotation matching does not establish runtime effectiveness. No additional tier
findings or changes to the exporter schema are required.

From the repository root, generate the real draft and the optional fictional demo
outside the Pages upload directory, then start the existing loopback server:

```bash
python3 -m tools.approach_a export-publication --mode preview
node tools/approach_a/tests/js/shortlist-fixture.mjs > assessment/preview/matrix.demo.json
python3 -m tools.approach_a serve-preview --port 4174
```

- Real draft: `http://127.0.0.1:4174/feature-matrix/?preview=matrix.preview.json`
- Fictional demo: `http://127.0.0.1:4174/feature-matrix/?preview=matrix.demo.json`
- Public file/empty state: `http://127.0.0.1:4174/feature-matrix/`

The fixture preserves all 18 specification features; select F01, F07 and F08 to
exercise all three groups. Alder has separate Individual and Enterprise profiles;
Birch has pending evidence and Elm has an unknown tier. All tools, tiers and
findings in this demo are fictional. The demo banner labels it explicitly. Both
preview files stay in gitignored `assessment/preview/`; neither the generator nor
fictional tier data belongs under `dashboard/`. Preview selection is honored only
on loopback hosts. The public JSON stays untouched until the whole selected
manifest passes validation, independent review and approval. No person’s review,
authorship or approval is recorded by these preview commands.

Run the existing workflow checks:

```bash
python3 -m unittest discover -s tools/approach_a/tests -t .
node --test tools/approach_a/tests/js/*.test.mjs
python3 -m unittest tools.approach_a.tests.test_publish_files.CommittedDataFile -v
for f in dashboard/feature-matrix/*.mjs; do node --check "$f"; done
```

An optional browser check reuses an installed Playwright with Chromium (no
production dependency or download is added). With the preview server running:

```bash
PLAYWRIGHT_MODULE=/absolute/path/to/node_modules/playwright \
  node tools/approach_a/tests/js/shortlist-browser-check.mjs
```

It checks the empty state, draft and demo labels, Overview/Shortlist flow, both
grouped dropdowns, feature search, sorting, URL/reload/history persistence, exact
cell links and focus, keyboard operation, and a 375px viewport. It expects the
current public empty marker and a real unaccepted draft with an undecided tier;
fixtures exercise complete coverage while human review is pending.

For this local integration review (November 8, 2026), the accepted exporter
reported 36 blockers: `AUTHOR_MISSING` ×17, `REVIEW_MISSING` ×18 and
`APPROVAL_MISSING` ×1. The public empty marker is retained. Team members must
resolve authorship, independently review every cell, settle the profile tier
boundary, and approve the selected manifest before exporting accepted data.
UI review uses the direct route; a dashboard header link still needs the
microsite owner's agreement. Push, merge, Pages deployment and changes to
`.github/workflows/static.yml` are outside this pass.


### Walk through blocking items interactively

For the expanded CLI/Windows research dataset:

```bash
python3 -m tools.approach_a --data assessment/research/2026-11-08 blockers
```

For the default active dataset, use `python3 -m tools.approach_a blockers`.
The selected dataset's absolute path is printed first. The command evaluates the
current JSON rather than relying on an old validation report, lists the blocking
keys and counts, then offers a profile selector and a blocker-type selector.
Manifest-wide blockers such as approval have their own selector entry.

For each matching item, it shows the problem and the current profile or cell,
including supported/unsupported/unestablished scope, source URLs, quotations,
challenge flags, authorship and review state. Resolve an item explicitly or use:

- `s` or Enter: skip this item without changing it.
- `p`: apply one author or reviewer profile-wide (available on author/review blockers).
- `r`: re-read the current data and recheck the item after an external correction.
- `u`: change the recording person; select the actual person making the decision.
- `b`: return to the profile and blocker-type menus.
- `q`, end-of-input, or Ctrl+C: stop; earlier saved decisions remain saved.

Human-decision blockers have actions for taking responsibility as author, recording
agreement/disagreement with a required review note, confirming the displayed
boundary, or approving the manifest. Identity is requested on the first decision
and reused for the session; `--operator YOUR_ROSTER_ID` can supply it up front.
Self-review and missing reviewer/approver roles are rejected by the existing
rules. The CLI cannot authenticate who is typing; Git provenance and independent
human verification are still required.

Confirm boundaries before assigning authors and reviews. Boundary confirmation
uses the current manifest profile, preserving existing edits, and lets the person
set the agreed tier/platforms and add exclusions. It clears that profile's
previous authorship and manifest approval using the existing boundary procedure.
The documentation access date is preserved. A proposal placeholder is not an
agreed account tier.

Other blockers (for example pending research or missing source fields) show the
problem without inventing a fix. Correct the dataset or research input separately,
then use `r` or return to the menus. Skipped blockers remain visible next time.
After each recorded decision, the command refreshes validation and generated
views. A disagreement can add a new blocker; saving a decision does not necessarily
resolve the item. If displayed cell/evidence/review/manifest data changes during
the prompt, the decision is refused until it is rechecked.

Browsing, `--list`, skipping and quitting write nothing. Only explicit decisions
change records. The command makes no network/model requests and never exports or
publishes results. Useful shortcuts:

```bash
# Current blocking keys only; no prompts or dataset writes.
python3 -m tools.approach_a --data assessment/research/2026-11-08 blockers --list

# Start directly with one profile and blocker type.
python3 -m tools.approach_a --data assessment/research/2026-11-08 blockers \
  --profile codex-app-windows --code AUTHOR_MISSING
```


When you choose `p`, the walker shows all eligible cells for the selected profile
and explains which cells will stay unchanged. A profile-wide author fills only
missing authors on researched cells. A profile-wide review covers unresolved
review blockers, across missing/stale/invalid reviews and open disagreements.
It preserves current reviews and skips cells without an author, pending research,
and cells authored by the selected reviewer.

For a profile-wide review, choose agree or disagree and enter one shared note.
This records actual human review decisions for all listed cells, rather than
assigning a person to review them later. Each record retains its individual cell
hash and normal review history. The walker asks for explicit confirmation of the
person, profile and cell count before writing; declining leaves the data alone.
Use the single-cell actions when decisions or notes differ. Both profile-wide
options recheck the displayed data and refresh validation after saving.

### Review packets and checked-cell batches

`review-packet` prints an offline, read-only Markdown packet per profile (all
profiles by default; repeat `--profile` to select). It does not fetch pages,
call a model, render files into the dataset, or record decisions. Each packet
shows the exact recorded surface, tier, platforms, modes and exclusions, with
manifest version/hash and boundary confirmation. Proposed tiers remain proposals.
Conflicts, explicit absence claims and scope ambiguities are listed first.
Shared URL/section/quote passages are grouped with the cells using them; findings
retain individual statuses, scope, flags, named authors, independent reviews,
dispositions, hashes and stale labels. Context comes only from the matching
cached source snapshot; missing or changed context is labeled for source-link
inspection. Quote matching and automated challenge flags do not establish
source-to-claim alignment. Read the linked official section before agreeing.

Read-only example commands (the November 8 dataset is not modified):

```bash
python3 -m tools.approach_a --data assessment/research/2026-11-08 review-packet --profile codex-cli > /private/tmp/codex-cli-review.md
python3 -m tools.approach_a --data assessment/research/2026-11-08 review-packet > /private/tmp/approach-a-review.md
python3 -m tools.approach_a --data assessment/research/2026-11-08 blockers --list
```

For a local review workspace, copy that dataset first. Select your actual roster
ID at the decision prompt; no identity or decision is supplied by these commands:

```bash
review_dir=$(mktemp -d /private/tmp/approach-a-review.XXXXXX)
cp -R assessment/research/2026-11-08/. "$review_dir/"
python3 -m tools.approach_a --data "$review_dir" blockers
```

Resolve the boundary and responsible human authors first. For review blockers,
`p` reuses the profile-wide action and displays the packet before asking which
eligible features you actually checked. Enter space-separated IDs such as
`F01 F02 F04`, or `all` only after checking every eligible cell; Enter cancels.
The selected cells, shared decision and required note are shown before an explicit
`y` confirmation. Use individual `a`/`d` decisions for exceptions, with a
recorded disagreement disposition where appropriate. Individual decisions also
require confirmation; Enter never records one. Self-review, missing authors,
pending research and existing current reviews are excluded from a review batch.
Unselected cells remain open. Every saved batch uses the existing per-cell review
hash and work log, then reruns validation and displays remaining blocker counts.
Changed cells, evidence, reviews or manifest during the prompt invalidate the
batch before any writes. A new manifest version still requires approval.

After actual human review, use the existing validation/export commands. Validation
writes reports and generated views only to the selected scratch workspace. The
accepted exporter independently checks the **entire** manifest, even if only one
profile was reviewed. It refuses pending, disputed, stale, unapproved or otherwise
blocked data. It writes a local staging file; it does not deploy or stage Git files:

```bash
python3 -m tools.approach_a --data "$review_dir" blockers --list
python3 -m tools.approach_a --data "$review_dir" validate --brief
# Run only after the entire approved manifest passes:
python3 -m tools.approach_a --data "$review_dir" export-publication --mode accepted --allow-other-out --out /private/tmp/approach-a-accepted.json
```

A scratch export is for local inspection only. It cannot write under `dashboard/`,
even with `--source-commit`. To prepare public data, first copy the actual reviewed
inputs to a deliberate repository dataset path and commit them. The example below
uses a **new**, previously unused destination; do not overwrite historical records.
Run it only after actual human review and whole-manifest validation have passed.
No fictional fixture records belong in this workflow.

```bash
# Create a unique new path for the actual reviewed snapshot.
mkdir -p assessment/reviewed
committed_data=$(mktemp -d assessment/reviewed/accepted.XXXXXX)
for name in catalog.json manifest.json cells.json sources.json reviews.json people.json; do
  cp "$review_dir/$name" "$committed_data/$name"
done
python3 -m tools.approach_a --data "$committed_data" validate --brief
git add -- "$committed_data/catalog.json" "$committed_data/manifest.json" "$committed_data/cells.json" "$committed_data/sources.json" "$committed_data/reviews.json" "$committed_data/people.json"
git diff --cached -- "$committed_data"
git commit -m "Record human-reviewed Approach A snapshot"
# Default HEAD, or an explicit commit, must match every input byte at this path.
python3 -m tools.approach_a --data "$committed_data" export-publication --mode accepted --source-commit HEAD
git diff -- dashboard/feature-matrix/data/matrix.json
# Optional Git staging after checking the projection:
git add dashboard/feature-matrix/data/matrix.json
```

Review the staged diff before committing; ensure it contains only the intended
reviewed inputs. These commands prepare local files and do not push or deploy.
Validation reports, caches, generated views and work logs do not affect the
export's Git binding; retain review work logs separately as assessment history.

For a draft preview, keep the separate preview destination and existing server:

```bash
python3 -m tools.approach_a --data "$review_dir" export-publication --mode preview
python3 -m tools.approach_a serve-preview --port 4174
```

No refresh/research command is part of review. Documentation refresh and
change-only re-review are follow-up work: any future implementation must retain
reviews only when the finding, evidence and profile scope are unchanged; every
new manifest version needs approval. This packet workflow does not change the
Oct. 22 SRS 5.4.2 drafting rules, accepted-export gates or deployment workflow.

Verification (synthetic disposable fixtures, no real human decisions):

```bash
python3 -m unittest discover -s tools/approach_a/tests -t .
```


### Review integrity and export provenance

New decisions retain `cell_sha256` and add `binding_version: 1`,
`evidence_sha256` (the full cited entries keyed by ID), and `profile_sha256`
(the full assessed profile record). A cell change, a cited entry change under
an unchanged ID, or a profile change makes its review stale and blocks accepted
export. Entries not cited by the cell and other profiles do not affect it.
The profile binding is conservative: any change to that profile record requires
re-review. Changing only the manifest version does not stale cell reviews but
still invalidates manifest approval. Existing review history is never migrated
or hashed from current data. Legacy or unsupported bindings are explicitly stale
because the original evidence/scope cannot be established; a person must check
and record a new decision through `blockers` or `review`.

Export version 2 binds all six input files, including `people.json`, in
`release.source_file_sha256`. For public writes, the snapshot bytes must match
both the claimed commit and the Git index at the **selected dataset path** in
this repository. Untracked paths, uncommitted input changes, staged differences,
missing files and an incorrect `--source-commit` are refused before replacing
public data. Unrelated repository changes do not block export. The final public
write rechecks the input hashes and Git binding. A matching historical commit
may be used if its input bytes also match the current worktree and index.

Local accepted exports outside `dashboard/` still require whole-manifest
acceptance but allow unverified provenance. Draft previews retain their separate
location and workflow labels. `source_verified` reports whether all input bytes
matched; `source_dirty` is false only for a verified match (true means unverified
or mismatched, not the status of unrelated repository files). `source_commit` is
the resolved commit checked, or null when no repository binding is available;
`requested_source_commit` preserves an explicit request without asserting it
contains the inputs. `source_dataset_path` is the repository-relative path checked,
or null for outside scratch data. Raw in-memory `build` calls without a dataset
path never claim a clean commit, even if given a SHA or `source_dirty=False`.
The public-file check rejects these unverified local projections; do not copy a
scratch projection into `dashboard/`. Re-export from the committed reviewed path.
