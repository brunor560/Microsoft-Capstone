# Feature matrix and microsite integration review

Prepared November 4, 2026. Recommendation and implementation plan. The body below is the original review; the progress and decisions section directly below supersedes it where they differ.

## Progress and decisions (updated November 5, 2026)

Work proceeds one PR at a time. Initial profile: `antigravity-cli`; additional sample profiles for the MVP demo come later, and actual runs begin after the MVP demo stage.

| PR | Scope | Status |
| --- | --- | --- |
| 1. Contract and exporter | `export-publication` command, public payload contract, checks, tests, empty-state data file | **Implemented, awaiting review.** Tests pass; the real dataset is correctly refused in accepted mode (36 blocking findings). No accepted snapshot exists yet |
| 2. Matrix page | Standalone page under `dashboard/feature-matrix/`, local preview server, guide | **Implemented, awaiting review.** Page, filters, deep links, detail panel, empty and error states, 18 Node tests, headless-Chrome check. See `Feature_Matrix_Publishing_Guide.md` for how to run, preview and publish |
| 2b. Pull-request checks | `.github/workflows/feature-matrix-checks.yml`: runs the Python and Node tests and the data-file check on pull requests. SHA-pinned actions, read-only permissions, no credentials | **Added, not yet run on GitHub.** Validated locally only (YAML parses; the tests it calls pass). It is not a merge requirement until branch protection says so, and `static.yml` is unchanged |
| 3. Staged build and release gate | Coordinated with the microsite owner | Not started. Remaining scope: staged build, release manifest with previous-release pointer, `site/data/<release>/` layout, a gate inside the deploy workflow, JSON handling in `serve.mjs` |

**Decisions that change the plan below**

- **Location and ownership.** All new web assets live under `dashboard/feature-matrix/`. `dashboard/index.html`, `build-data.mjs`, `data.js`, `serve.mjs` and `static.yml` are not modified in PR 1 or PR 2. Linking the dashboard navigation to the new page is coordinated with the microsite owner. Sections 6, 7 and 9 that propose changing `serve.mjs`, `static.yml` or the shared navigation now apply to that coordinated PR.
- **Role of the exporter.** The exporter prepares a reviewed projection for M13. Publication is handled by the existing Pages workflow, which uploads `dashboard/`. The exporter is an M11-side projection (`tools/approach_a/publish.py` and `pubcheck.py`) and is not itself the M13 release builder.
- **Interim output path.** `dashboard/feature-matrix/data/matrix.json`. This is not the DDD's `site/data/<release>/` layout. The payload carries a `release_id` and input hashes so a later build can place it there.
- **Deferred to the coordinated PR (3).** Staged build and staging directory, a gate inside the deploy workflow, the release manifest naming the previous release, a previous-release pointer, `site/data/<release>/` addressing, JSON MIME handling in `serve.mjs`, and deploy verification. In the interim, the new pull-request workflow `feature-matrix-checks.yml` runs the tests (including the committed-file checks in `tools/approach_a/tests/test_publish_files.py`), but it does not block a merge until it is made a required check, and `static.yml` still deploys without running it.
- **Dashboard link (decided November 5).** No link is added to `dashboard/index.html` for now; the page is shared by its address (`<pages base>/feature-matrix/`). After the view is approved, one of us adds one relative header link, in agreement with the microsite owner. The published empty state ("No reviewed assessment published yet.") is accepted for inclusion in the public release.
- **Accepted data only under `dashboard/`.** The public file is generated from an accepted snapshot and must pass `check_payload`. Draft previews are written to `assessment/preview/` (gitignored). The exporter refuses a preview output inside `dashboard/`, because the entire directory is the Pages upload root.
- **No identities in the public payload.** Names and roster IDs are not exported, and there is no option to include them. The payload records only that a named author exists (`author: {recorded: true}`) and that an independent review was made (`independent: true`, review date, decision, cell hash). Author, reviewer and approver identities remain in the Approach A dataset and the Git history that recorded them. This supersedes the earlier suggestion to publish approved author and reviewer attribution (sections 3 and 4, and the cell details list in section 5, item 8: the page shows "authored" and "independently reviewed on <date>", not who). It follows DDD C-7 and A-3.
- **Required data file and empty state.** `dashboard/feature-matrix/data/matrix.json` must exist in every data release. It is either an accepted payload (`approach-a/publication/1`) or the deliberate empty marker (`approach-a/publication-empty/1`, message "No reviewed assessment published yet."). The page, in PR 2, shows that message for the marker and a distinct load error if the file is missing or malformed. A test fails if the file is missing, is a preview, fails `check_payload`, or contains a roster name or ID. The empty marker is committed now.

**DDD consistency (checked November 5, 2026).** No hard conflict with M11, M13, I08, I12, ADR-09 or ADR-14, or with SRS 5.5. Recorded deviations: the interim output path above; the previous-release pointer and release manifest are deferred; the exporter sits on the M11 side. The DDD still describes M11 as a stub and ADR-14 as "Proposed", and stored evidence IDs are `E01` (the `MATRIX:` prefix is a display choice). Design and traceability documents are updated after the implementation shape settles, under the course_artifacts ownership rules.

---

## Recommendation

Keep GitHub Pages and the current static dashboard. Add a dedicated documentary feature matrix page, a small Python publication exporter that reuses the workbench's validation and hash functions, and an explicit site build that stages reviewed data before deployment.

The integration is primarily **a data publication boundary plus a new results view**. The pipeline already captures most of the information the site needs. It does not need a hosted backend, database, new agent framework, live research endpoint, or migration to a frontend framework.

Build one complete path first: an approved profile with 18 independently reviewed cells → validated export → browsable matrix → evidence detail → staged Pages release. Develop that path with synthetic fixtures and a clearly labeled local preview of the existing drafts. Expand to additional profiles after the path works.

## Review scope and evidence

I inspected the current default branch, **master**, pinned at commit [711bdd9068822f0dfbd417ea621c58ecb27729a9](https://github.com/brunor560/Microsoft-Capstone/tree/711bdd9068822f0dfbd417ea621c58ecb27729a9).

Primary sources:

| Area | Files examined |
| --- | --- |
| Deployed site source | [dashboard/index.html](https://github.com/brunor560/Microsoft-Capstone/blob/711bdd9068822f0dfbd417ea621c58ecb27729a9/dashboard/index.html), dashboard/build-data.mjs, dashboard/data.js, dashboard/serve.mjs, dashboard/README.md |
| Deployment | [.github/workflows/static.yml](https://github.com/brunor560/Microsoft-Capstone/blob/711bdd9068822f0dfbd417ea621c58ecb27729a9/.github/workflows/static.yml) |
| Design | [course_artifacts/sources/ddd.md](https://github.com/brunor560/Microsoft-Capstone/blob/711bdd9068822f0dfbd417ea621c58ecb27729a9/course_artifacts/sources/ddd.md), focused SRS publication requirements and feature matrix specification |
| Pipeline outputs | assessment/catalog.json, manifest.json, cells.json, sources.json, reviews.json, people.json, validation_report.json |
| Workbench behavior | tools/approach_a/README.md, model.py, store.py, review.py, checks.py, cellchecks.py, validate.py, render.py |
| Earlier site material | Root index.html, demo.html, docs/ARCHITECTURE.md, docs/INTEGRATION-GUIDE.md |

The DDD identifies its baseline as the October 18 submitted version 1.4 and marks later design changes as proposals. I used its canonical Markdown for design intent and current code for implementation facts. Its implementation-status descriptions can lag the code; for example, the workbench now does substantially more than the DDD's old M11 “stub” description.

I kept the pipeline-to-DDD review narrow, as requested. I did recompute the current dataset's structural validation on a scratch copy using the existing validator. No assessed tools were executed, documentation pages refreshed, Azure calls made, or human reviews/approvals recorded. I parsed the committed benchmark payload to inspect its shape. This is a source and data review, not a browser accessibility audit, security penetration test, or verification of the live Pages deployment.

## 1. Current microsite architecture

### The operative site is dashboard/

The Pages workflow uploads **dashboard/**. Root index.html and demo.html are not included by that workflow.

The root landing page and docs/ architecture describe an older browser-based model comparison demo, including API configuration and simulated responses. They should not guide this integration. The operative starting points are dashboard/ and the canonical DDD.

| Component | Current responsibility | Integration implication |
| --- | --- | --- |
| dashboard/index.html | Approximately 131 KB of HTML, CSS and JavaScript in one file; filters, tables, scoring, run/task drawers, code differences, reconstructed replay, live app preview | Reuse visual conventions selectively; adding the entire matrix into this file would increase coupling |
| dashboard/build-data.mjs | Node script reading Git history and results files from origin/results/all-runs; normalizes logs, usage, code and metadata | Useful precedent for offline data preparation, but its run parser is not an appropriate matrix exporter |
| dashboard/data.js | Generated executable assignment to window.BENCH_DATA | Existing browser input contract, not a public matrix contract |
| dashboard/serve.mjs | Minimal local static server | Sufficient for development; add application/json MIME handling if JSON assets are introduced |
| static.yml | Checkout, configure Pages, upload dashboard/, deploy | Currently has no data rebuild, release validation, or test stage |

The committed benchmark payload was generated **October 30, 2026, at 03:27 UTC**, identifies results commit **1920d50**, and contains **26 runs**. That abbreviated commit matches the results/all-runs branch head retrieved for this review. The file is approximately **1.08 MB**. Its run objects contain no explicit approach or cohort field.

The dashboard uses vanilla JavaScript and its own HTML/CSS charts rather than a frontend framework. It already provides useful interaction patterns: filter chips, explanatory notes, details panels, source links, light/dark themes, and persisted preferences. These are valuable assets.

### Structural limitations relevant to integration

1. **Presentation, data interpretation and scoring are coupled.** Benchmark scores are calculated in the browser. Matrix statuses must never pass through that scoring machinery.
2. **Tool identity is partly hardcoded.** Tool lists, colors and ordering assume the existing four benchmark tools. Matrix profiles must be discovered from the manifest.
3. **The page assumes valid benchmark data at startup.** It dereferences window.BENCH_DATA and its tasks/runs immediately. Matrix availability should not depend on that payload loading successfully.
4. **Publication trusts prebuilt assets.** A normal merge can deploy old data.js; the workflow does not regenerate it. The freshness banner is advisory and does not replace a reliable build.
5. **Evidence URLs can move.** The benchmark exporter constructs results/all-runs branch URLs, even when another input branch is selected. New matrix links should use the full source commit.
6. **File naming and documentation are misleading.** “Results matrix” currently means tools × benchmark tasks. Name the new view “Documented capabilities” or “Feature matrix — Approach A” to distinguish it.

## 2. DDD implications for the integration

The intended boundary is clear:

| Design element | Consequence |
| --- | --- |
| M11 Assessment | Owns documentary profiles, cells, sources and independent reviews |
| M13 Release builder | Owns publication, validation of selected data, release identity and presentation |
| I08 ReleaseInput | Carries record, cell and review references into the release process |
| I12 CellExport | Documentary cells pass as reviewed data; they are not benchmarked or regraded |
| ADR-09 | JSON files and a static site are the preferred architecture |
| ADR-14 / SRS 5.5.1 | Documentary findings occupy their own view and are never combined with B/C results |
| Release manifest | Binds exact selected inputs and hashes; prior release remains available on failure |
| SRS TC-5.5-1 | Requires checking separation, documentary evidence/uncertainty labels, and absence of a combined numerical ranking |

The site should remain a reader of published results. Research, drafting, authorship, approval and independent review stay in the workbench and Git review process. GitHub PR review of an integration change does not automatically constitute the recorded source-to-claim review of every cell.

The proposed site/data/<release_id>/ layout in the DDD is a release organization, not a reason to rewrite the dashboard. A generated staging directory can implement that organization while source files remain under dashboard/.

An important adjacent discrepancy: the DDD distinguishes **raw native-tool reporting in Approach B** from **controlled scoring in Approach C**. The current dashboard computes weighted tool scores from native results and lacks explicit approach/cohort fields. Adding a separate Approach A view prevents new mixing, but does not resolve that existing difference. Track benchmark classification and scoring alignment as a separate task; do not claim that matrix integration completes all of M13.

## 3. What the pipeline already produces

Use the authoritative JSON dataset directly. Markdown in assessment/out/ is a generated review aid and should not become an intermediate data API.

| Input | Useful site content | Publication handling |
| --- | --- | --- |
| catalog.json | 18 feature definitions, feature areas, seven tool categories, five statuses and their meanings | Drive labels and filters from this file |
| manifest.json | Versioned profiles, product surface, modes, platforms, tier, exclusions, documentation date, approval | Show profile boundaries prominently; verify approval against current manifest hash |
| cells.json | Primary status, scope, setup, activation, control mechanism, constraints, uncertainty, author and dates | Publish reviewed findings with their full qualifications |
| sources.json | Evidence entries, exact quotes, section, URL, source surface, access date, page hash and verification state | Resolve references and include only needed public metadata and excerpts |
| reviews.json | Reviewer, decision, review date, reviewed cell hash and disposition | Resolve the current review and reject missing/stale/disputed reviews |
| people.json | Roster identifiers and names/roles | Use for validation only; never exported (the exporter also checks the payload for any roster name or ID) |
| validation_report.json | Last recorded structural result | Useful diagnostic; recompute validation for the selected source snapshot |
| worklog, drafts, cache | Research history, raw drafts and cached documents | Keep outside the public payload by default |

### Present dataset readiness

The current manifest contains one profile, antigravity-cli. All 18 cells are **challenged**, with 12 draft “Built in” classifications and six draft “Configuration or extension required” classifications. There are 47 referenced evidence entries and 31 page-index records.

Fresh structural validation reports:

| Check | Current result |
| --- | --- |
| Manifest approval | Missing |
| Named human authors | 1 of 18 |
| Independent cell reviews | 0 of 18 |
| Blocking findings | 36: one approval, 17 authorship, 18 review findings |
| Dataset acceptance | Not accepted |

These are draft classifications, not accepted capability findings. The 18/18 research progress does not imply publication readiness.

The manifest also retains open-ended tier wording (“Tier for the assessment is a team choice”). Confirm the concrete intended boundary during acceptance. This is a data completion task, not a request to redesign the pipeline.

### Two meanings of status must remain distinct

The five method statuses describe documented support. assessment_state describes workflow progress. A pending cell's “Not established from documentation” value is explicitly a placeholder; a reviewed documentation-gap finding is a legitimate completed result.

The UI must never make those appear equivalent. Preview cells need visible workflow labels. Public accepted results should retain review provenance and may legitimately include “Not established from documentation” with a specific gap/conflict explanation.

Likewise, “Configuration or extension required” does not establish that an excluded extension is installed or included in the assessed profile. The setup and exclusions must remain reachable from the cell.

## 4. Recommended data and release boundary

### Add a Python export command

Implement a proposed export-publication command/module under tools/approach_a/. This is new work; no such exporter currently exists.

The exporter should:

1. Read one frozen dataset snapshot and run existing structural validation.
2. Resolve the manifest, catalog, every expected cell, current review and referenced source.
3. Check publication-specific schema, references, allowed URLs, public field selection and integrity.
4. Construct a small versioned publication payload.
5. Write temporary output, validate it, then promote it into the staged release.

Reuse Store, manifest_hash, cell_hash and review.current. Do not rewrite their hash algorithms in JavaScript: Python's existing JSON serialization details are part of the current hash contract.

The existing validator writes a report and appends a worklog event. Run it against a scratch copy during builds, or add a pure validation entry point so site builds do not mutate authoritative research records.

### Proposed public payload

One matrix.json is enough initially:

| Proposed section | Contents |
| --- | --- |
| schema | Independent publication schema/version; retain existing input schemas unchanged |
| release | Release ID, source commit, export version, source-file hashes, manifest hash, publication mode, generation time |
| catalog | Feature IDs/areas/definitions, category definitions, exact status labels and meanings |
| profiles | Manifest identities and relevant scope/version/modes/platform/tier/exclusion fields |
| cells | Stable profile/feature identity, documentary status, scope/setup/control/constraints/gap, author/date, evidence references and current review reference |
| evidence | Referenced official-source entries with quote, section, URL, date, scope and page hash |
| reviews | Required public review provenance and the reviewed cell hashes |
| limitations | Documentation-only method, uncertainty semantics, version/date qualification |

Use actual workbench profile IDs such as antigravity-cli; do not invent a C01 mapping merely because the specification illustrates one. Preserve F01–F18 and evidence IDs, displaying the MATRIX: prefix where it avoids ambiguity with other project identifiers.

Bind the **catalog, manifest, cells, reviews and sources** in the release manifest. A cell's existing substance hash does not include the contents of the external evidence records it references. Changing an evidence quote under the same E ID must not silently inherit an old semantic approval. Add a dependency check/review policy for such changes; release hashes establish reproducibility, while source-to-claim acceptance still needs human review.

Do not equate source check=verified with verified capability. It means a quote was found in a section. Prefer “Quotation matched to source” as its explanatory label.

Avoid exporting people rosters, names, roster IDs, worklog entries, model request IDs, raw drafts, cache files, or deployment configuration. *Updated:* the public payload records only that an author exists and that an independent review was made; identities stay in the Approach A dataset (see the progress and decisions section).

### Acceptance and preview modes

| Mode | Behavior |
| --- | --- |
| Accepted publication | Entire selected manifest satisfies current validation and publication checks; only accepted findings enter the public data release |
| Development preview | Local build or bounded PR artifact; persistent “Draft — not accepted” labeling and workflow states; cannot be promoted as accepted |
| No accepted matrix yet | Public page may show an honest explanatory empty state; research drafts do not need to be exposed |

Initially gate the complete selected manifest, preserving 18 × P. Silently dropping unreviewed cells or profiles to obtain a green build is unacceptable.

When ongoing research starts, do not make the public site consume the mutable working dataset automatically. Preserve a previously accepted snapshot and select it explicitly for releases. New incomplete research can then coexist with the last accepted public matrix.

A failed candidate release should leave the previous deployed artifact live. To update benchmark content while matrix research is incomplete, deliberately select the last accepted matrix snapshot in a new release manifest. Do not implement a hidden “validation failed, reuse whatever file happens to be on disk” fallback.

## 5. Recommended user experience

### Site navigation

Add peer navigation destinations:

- Documented capabilities — Approach A.
- Native-tool results — Approach B.
- Controlled harness results — Approach C, when eligible data exists.
- Methodology and limitations.

An unavailable view should say so plainly. Do not populate it with fabricated placeholders or relabel native results as controlled evidence.

For the first increment, retain the current dashboard at its existing location and add a dedicated feature-matrix.html page with shared navigation. A new site homepage and a larger file reorganization can follow.

### Matrix overview

Use feature rows and profile columns. Group the 18 rows by catalog area; retain stable feature IDs. Column headings should expose product surface, version/documentation date and a link to full scope.

Recommended controls:

- Profile/tool selection and category filtering.
- Feature area, documentary status, activation and control-mechanism filters.
- Search over feature names, findings, setup and limitations.
- Alphabetical/profile ordering and catalog feature order.
- Clear filters, visible result counts, and shareable URL parameters.

Keep tool categories distinct from feature areas: T1–T7 classify tool types; the catalog's area field groups feature rows.

Status filtering needs explicit semantics. A practical rule is “show a feature row when any selected profile matches,” retaining other selected columns for context and marking their nonmatches. A comparison view should not remove arbitrary individual cells and imply missing research.

Do not sort products by an implied status hierarchy or a count of “Built in” cells. Labels such as built in, optional activation and enforced control describe different dimensions and should not become an ordinal capability score.

### Cell details

Clicking a cell should reveal:

1. Feature definition and the selected profile boundary.
2. Primary documentary status and concise finding.
3. Supported, explicitly unsupported and unestablished subcapabilities.
4. Required setup and exclusions/dependencies.
5. Activation state, control mechanism and constraints.
6. Gap/conflict reason where applicable.
7. Evidence quote, official page/section, source scope, access date and version/hash.
8. Authorship recorded, independent review (date and decision) and release/source references. *Updated:* no names or roster IDs are shown.

This detail is the substance of the deliverable. A colored checkbox grid would hide precisely the conditions Chad needs when considering a client's environment.

Provide stable cell URLs, for example feature-matrix.html?profile=antigravity-cli&feature=F08. Avoid reusing the benchmark drawer's run/task URL state.

A responsive card/list alternative can serve small screens. Use semantic table headers, keyboard activation, visible focus, named controls and readable status text. Color alone is insufficient. Audit contrast in both themes.

### Sponsor-oriented comparison

Prioritize questions such as:

- Which documented controls match the intended platform and product surface?
- Is a control enabled by default, optional, or dependent on policy?
- Does support require excluded extensions or custom implementation?
- What remains unestablished, and which documentation would resolve it?

A saved subset of features or profiles can help present a client scenario. Treat priorities as a selection/filter initially. Weighted recommendations or a single “best tool” require a separately agreed method and are outside this integration.

Cross-links to benchmark results are useful context, but require an explicit mapping and a configuration-match caveat. The matrix profile is not automatically the configuration used in a benchmark. Runtime success must not be imported as documentary evidence.

## 6. Implementation options

| Decision | Options and trade-offs | Recommendation |
| --- | --- | --- |
| View organization | Same-page tab reuses layout but adds to a large coupled script; separate static page isolates loading/state; frontend-framework migration offers reusable components but creates a broad rewrite | Separate static page with shared navigation/styles |
| Export location | Python reuses existing validation/hashes; Node fits the existing builder but duplicates semantics; browser joins expose internal records and defer validation | Python exporter invoked by a common build |
| Browser delivery | JSON fetch separates data from execution and supports download/versioning; JS global matches existing offline opening but is executable content; generated HTML improves no-JS access but adds rendering work | Same-origin JSON, loaded independently by the matrix page |
| Data partitioning | One payload is simplest; per-profile payloads reduce later initial loads but add manifests and failure states | One matrix payload initially; measure before splitting |
| Publication source | Mutable worktree is convenient but unsuitable for reproducible release; fixed commit/snapshot is reproducible; hosted API adds runtime dependencies | Explicit source commits and accepted snapshot selection |
| Draft handling | Local/PR preview keeps review simple; public draft page needs strong labeling and independent promotion rules | Local/PR preview first |
| Release timing | Committed generated assets are inspectable but can drift; CI-generated assets stay synchronized but require a complete build | Generate in CI from pinned inputs, upload staged output |
| Hosting | Pages meets current design; managed static hosting is feasible but adds migration; backend/database adds operating cost without a demonstrated need | Retain Pages |

A framework is reasonable if the team already has a separate commitment to rebuilding the site. The matrix alone does not justify that investment.

## 7. Build and deployment design

Add a common build-site entry point that:

1. Resolves and records the site source commit and the explicitly selected benchmark and matrix commits.
2. Fetches the required Git refs/history for the existing benchmark builder. A default shallow checkout is insufficient for all its pinned historical baselines.
3. Builds the benchmark assets with their existing builder, without modifying historical evidence.
4. Validates and exports the selected matrix snapshot.
5. Stages an allowlisted static site, with separate benchmark and matrix assets.
6. Writes a release manifest binding input commits, hashes, exporter versions and public artifacts.
7. Runs contract, link, rendering and publication-separation checks.
8. Uploads only the staging directory and deploys after success.

The DDD-compatible data location can be data/<release_id>/matrix.json in that generated site. Each HTML build should point to its own release assets. Include an explicit hash for benchmark data as well; its current embedded branch identity can be retained during migration.

Update static.yml to build and check before upload. Use separate build and deploy jobs where practical, minimal permissions, and the project's action-pinning expectations. No Azure credentials or model invocation belong in this workflow.

The current workflow triggers on master pushes and manual dispatch. Changes only on results/all-runs do not trigger it. Decide how results become release inputs: a merge updating an explicit release selection on master is a straightforward auditable route. Branch-update polling is optional later.

Use relative asset paths so Pages' repository subpath works. Do not assume hosting at /. Add JSON MIME handling to the local server and clear UI errors for missing, malformed or unsupported-version matrix data.

The existing two-minute merge-to-visible requirement applies to run publication; measure it separately from export/aggregation time. Do not claim it is met merely because the site builds quickly.

## 8. Security and integrity details

The new matrix path should treat all findings, quotes and review notes as data: use text nodes or escaped templates, validate external link protocols, and avoid permitting raw HTML from source content.

There is also a concrete existing dashboard concern: makeLiveApp uses new Function to evaluate saved server.js in the parent page's JavaScript realm. A mocked require and process do not isolate access to browser globals. The HTML frame is sandboxed, but the server evaluation is outside that frame.

Keep that execution path out of the matrix page. For the existing benchmark preview, the bounded options are to disable execution and show saved evidence, or to move execution to a separately isolated context with restricted communication and network behavior. This deserves its own issue; it is not a reason to turn matrix integration into a complete site rewrite.

Likewise, hiding task-005 text in the UI is a presentation toggle, not access control: the committed payload contains the data. Do not use that mechanism to conceal unaccepted matrix findings; exclude those records at export.

The current benchmark payload also includes prompts and detailed operational artifacts, whereas the DDD describes a redacted public derivative. Preserve historical evidence, but add a separate review of public field policy. This matrix exporter should use an allowlist from its first version.

## 9. Ordered work plan and completion criteria

| Work item | Concrete changes | Completion criterion | Dependency |
| --- | --- | --- | --- |
| 1. Agree the publication contract | Public schema, source selection, status semantics, full-manifest gate, preview rule | Written contract and representative accepted/pending/uncertain/stale-review fixtures | None |
| 2. Implement the exporter | Python module/CLI; reuse current validator/hashes; public projection; release metadata; atomic output | Accepted fixture exports; invalid/stale/unreviewed inputs fail without promoting output | 1 |
| 3. Implement the matrix page | Separate HTML/JS; profile-driven rows/columns, filters, search, detail evidence, deep links, accessible controls | All 18 features render; uncertainty and excluded dependencies remain visible; no benchmark score dependency | 1; fixtures let this proceed alongside 2 |
| 4. Integrate the site build (*deferred to the PR coordinated with the microsite owner*) | Common build, pinned refs, staging directory, release manifest, local server support | Reproducible inputs; no mutation of authoritative assessment; only allowlisted artifacts staged | 2 and 3 |
| 5. Complete the real pilot dataset | Concrete profile boundary, responsible authors, independent source-to-claim review, real manifest approval | Fresh validation and publication checks pass for the selected 18-cell profile | Independent human work can start immediately |
| 6. Add CI and deploy verification (*deferred, same coordinated PR*) | PR checks; master build/deploy; previous release retained on candidate failure | Tested valid release, deliberate rejected release, working subpath/deep links and evidence links | 4 and 5 for accepted public release |
| 7. Expand and refine | More profiles, saved comparisons, exports, documentation updates | Multiple profiles work without hardcoded tool changes | Complete vertical slice |

Suggested work distribution: one owner for exporter/contract, one for matrix UI, one for build/CI, with a different qualified teammate reviewing the documentary findings. These are suggested responsibilities, not assignments or recorded approvals.

I would manage this as three main PRs:

1. Contract/exporter with fixtures.
2. Matrix view with shared navigation and independent loading.
3. Staged release workflow plus end-to-end publication checks.

The real data review can run alongside those PRs. Shared contract and fixtures must be agreed first. Record design/traceability changes after the implementation shape is settled, following course_artifacts ownership rules.

### Tests that matter

- Reject missing approval, wrong 18 × P coverage, pending cells, unknown status, dangling evidence, stale/self/missing reviews and unresolved disagreements.
- Preserve a reviewed “Not established” finding and its gap/conflict reason; distinguish it from pending research in preview.
- Detect changed evidence dependencies under stable IDs and bind every exported input to its release.
- Ensure text containing HTML/script-like content renders as text; reject unsafe URL schemes.
- Ensure a newly added manifest profile appears without edits to hardcoded benchmark tool lists.
- Exercise filter semantics, cell deep links, keyboard navigation, small screens and both themes.
- Render a release containing matrix data and benchmark data and assert that documentary results have their own view, no combined score, and complete evidence/uncertainty labels (TC-5.5-1).
- Reject a bad candidate build while retaining the previous deployed release.
- Verify Pages subpath asset resolution and immutable evidence links.

Use a small fixture set representing the five documentary statuses and review edge cases; the real dataset currently does not exercise all statuses. Successful source validation alone does not establish all of H-9. Publication tests and team acceptance remain necessary.

## 10. Scope boundaries and decisions

Recommended first-release decisions:

- Static Pages site with separate matrix page.
- Python exporter and one versioned JSON payload.
- Complete selected-manifest acceptance gate.
- Local/PR draft preview; accepted public snapshot selected explicitly.
- Full-commit evidence links and release hashes.
- No numerical capability ranking or shared B/C scoring.

Keep the following in follow-up work: benchmark cohort/scoring alignment, live-preview isolation, public benchmark redaction policy, a new site homepage, framework migration, browser-based authoring/review, automated research triggers, weighted recommendations, and dynamic hosting.

The first useful sponsor demo should show a profile boundary, a meaningful documented distinction, an optional versus default control, a qualified uncertainty, and the evidence/review behind each. That demonstrates the value of the data more convincingly than adding a capability total.
