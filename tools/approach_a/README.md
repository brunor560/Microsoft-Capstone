# Approach A assessment workbench

A minimal command-line workbench for the documentation-only feature matrix (SRS Requirement 5, DDD M11; method in `course_artifacts/sources/feature_matrix_specification.md`). Python 3 standard library only. Run it from the repository root:

```bash
python3 -m tools.approach_a --help
```

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

