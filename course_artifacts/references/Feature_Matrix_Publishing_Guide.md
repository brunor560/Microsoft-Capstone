# Feature matrix: how it reaches the microsite (guide)

Written November 5, 2026 for team members who have not worked on the microsite. It covers what the pieces are, how to preview draft work, how to publish an accepted matrix, and what to check when something looks wrong. Background and design reasoning are in `Feature_Matrix_Microsite_Integration_Review_2026-11-04.md`.

## 1. The microsite in five facts

1. The public site is a **static website on GitHub Pages**. There is no server, database or login.
2. The deployed folder is **`dashboard/`**. Everything in it is public once deployed. The root `index.html` and `demo.html` are older and are not deployed.
3. The workflow `.github/workflows/static.yml` deploys it. It runs on every push to `master`, about every 15 minutes on a schedule, and when started by hand from the Actions tab. It rebuilds the benchmark data, then uploads all of `dashboard/`.
4. The benchmark dashboard (`dashboard/index.html`, `build-data.mjs`, `data.js`, `serve.mjs`) belongs to another team member. **Do not edit those files.** Everything for the feature matrix lives in **`dashboard/feature-matrix/`**.
5. The site address is the repository's GitHub Pages address, with `/feature-matrix/` added for this page. Confirm the base address in the repository's Settings, Pages.

## 2. What exists for the feature matrix

| Piece | Where | What it does |
| --- | --- | --- |
| Research data | `assessment/*.json` | The authoritative Approach A dataset. Written by the `tools.approach_a` commands. Contains names and drafts, so it is not published |
| Exporter | `tools/approach_a/publish.py`, `pubcheck.py` | `export-publication` turns an accepted dataset into one public JSON file, with no names and no roster IDs |
| Public data file | `dashboard/feature-matrix/data/matrix.json` | What the page reads. Either an accepted export or the "nothing published yet" marker |
| The page | `dashboard/feature-matrix/index.html` plus `app.mjs`, `grid.mjs`, `controls.mjs`, `views.mjs`, `matrix-logic.mjs`, `dom.mjs`, `style.css` | Plain HTML and JavaScript, no framework and no build step |
| Draft preview | `assessment/preview/matrix.preview.json` (gitignored) and `serve-preview` | Lets you see unreviewed work locally. Never inside `dashboard/` |
| Tests | `tools/approach_a/tests/` | Python tests for the exporter and the data file, Node tests for the page |

## 3. The life of a finding

1. **Research.** The workbench drafts cells (`start`, `research`, `resume`). See `tools/approach_a/README.md`.
2. **Authors and reviews.** A team member takes responsibility for each cell (`author`), and a different team member reviews it (`review`).
3. **Approval.** The approver records the manifest approval (`approve`).
4. **Validate.** `python3 -m tools.approach_a validate` must say ACCEPTED.
5. **Export.** `export-publication` writes the public file. It refuses unless the whole manifest is accepted.
6. **Commit and merge to `master`.** The Pages workflow deploys it.

Nothing in steps 2 to 4 happens on the website. The site only displays the result.

## 4. Preview draft work locally

Use this to see what the page will look like. It needs Python 3 only, and runs from the repository root.

```bash
python3 -m tools.approach_a export-publication --mode preview
python3 -m tools.approach_a serve-preview
```

Open the first address it prints. It ends in `?preview=matrix.preview.json`. You will see a yellow "Draft — not accepted" banner, and each cell carries its workflow state (for example "Draft: awaiting independent review"). Pending cells show "Research pending", never "Not established".

Things to know:

- The preview file is written to `assessment/preview/`, which is gitignored, and served by a small Python server that listens on this computer only. The exporter refuses to write a preview inside `dashboard/`.
- The preview address is honoured only on `localhost`. On the real site the page always reads `data/matrix.json` and rejects any preview file.
- The second address the command prints, without `?preview=`, shows what the public page shows right now.
- Re-run `export-publication --mode preview` after the dataset changes, then reload.
- `dashboard/serve.mjs` is not used. Press Ctrl+C to stop the server.

## 5. Publish an accepted matrix

Only do this once `validate` reports ACCEPTED for the profiles you intend to show.

```bash
python3 -m tools.approach_a validate          # must end ACCEPTED
python3 -m tools.approach_a export-publication
python3 -m unittest discover -s tools/approach_a/tests -t .
node --test tools/approach_a/tests/js/*.test.mjs
git status                                    # expect only dashboard/feature-matrix/data/matrix.json changed
```

Then open a pull request. In review, look at three things:

1. `data/matrix.json` has `"publication_mode": "accepted"` and no names (the tests check this too).
2. The **Feature matrix checks** run on the pull request (`.github/workflows/feature-matrix-checks.yml`) and pass. They run the Python and Node tests, including `test_publish_files.py`. That workflow only reports a result. It does not stop a merge unless it is made a required check in the repository's branch protection settings (see section 8), and it does not run on direct pushes to `master`.
3. The cell count is 18 for each profile.

After the merge, the next Pages run publishes it. Open `/feature-matrix/` on the site and look at one cell's evidence links.

**Return to the empty state** (if an accepted file has to be withdrawn): replace the contents of `data/matrix.json` with the empty marker, exactly as in `tools/approach_a/publish.py`, function `empty_marker`:

```json
{ "schema": "approach-a/publication-empty/1", "message": "No reviewed assessment published yet." }
```

## 6. Page states

| You see | Meaning |
| --- | --- |
| "No reviewed assessment published yet." | The data file is the deliberate empty marker. Nothing is wrong |
| Red "could not be shown" message | The file is missing, not valid JSON, an unknown version, incomplete, or a draft. This is a fault. Check the browser's network tab and the file in the deployed folder |
| Yellow "Draft — not accepted" banner | A local preview. It never appears on the real site |
| Grey dashed "Research pending" | A cell the research has not completed. It is a placeholder, not a finding |
| "Not established from documentation" | A completed finding: the sources are silent, ambiguous or conflicting. The cell explains why |

The page reads only the matrix file. A broken benchmark dashboard does not affect it, and the other way round.

## 7. Changing the page

Edit files under `dashboard/feature-matrix/` only. Rules that the tests enforce:

- Text from the data is shown as text, never as HTML. Use `h()` from `dom.mjs`. Do not use `innerHTML`.
- Only `https:` links are made clickable (`safeHref`).
- Statuses are never summed, scored or used to sort products.
- The page can be opened locally with `serve-preview`. There is no build step, and `node --test` runs the page tests without a browser.

## 8. What is not done yet

These need the microsite owner, so they are left for the coordinated change:

| Item | Why it matters now |
| --- | --- |
| Link from the benchmark dashboard to `/feature-matrix/` | Decided: share the page by its address for now. Once the view is approved, one of us adds a single relative link in the dashboard header, `<a class="btn" href="feature-matrix/">Documented capabilities ↗</a>`, in agreement with the microsite owner. Use a relative path with no leading slash, because Pages serves from a repository subpath. The page already links back with `../` |
| Make the checks a merge requirement | The checks workflow is a pull-request check only. To enforce it, a repository admin marks "Feature matrix checks" as required in branch protection. Its path filters mean it does not run for unrelated changes, and GitHub treats a required check that never ran as pending, so confirm the setting with the admin before turning it on |
| Gate inside the deploy workflow | `static.yml` is unchanged, so a push to `master` that skips a pull request is deployed without these tests |
| Staged release, previous-release pointer, release folder layout | The design document's full release process. The export already carries a release ID and input hashes for it |
| Local server support for JSON in `dashboard/serve.mjs` | `serve-preview` covers local use in the meantime |

Open question for the team: the real `antigravity-cli` data has no approval, 17 cells without a named author and no independent reviews (36 blocking findings at last check), so no real matrix can be published yet.

## 9. Troubleshooting

| Problem | Likely cause and fix |
| --- | --- |
| `export-publication` says "dataset is not accepted" | Working as intended. Run `validate` to see the codes. `AUTHOR_MISSING`, `REVIEW_MISSING` and `APPROVAL_MISSING` need people, not code |
| "preview output must stay outside dashboard/" | You passed `--out` inside `dashboard/`. Leave `--out` off |
| `serve-preview` page shows "HTTP 404" | The preview file does not exist yet. Run `export-publication --mode preview` |
| Page works locally but is blank when deployed | Run it from a subfolder: all paths in the page are relative. Check the Actions run and that `matrix.json` was merged to `master` |
| The Feature matrix checks workflow does not appear on a pull request | It runs only when files under `dashboard/feature-matrix/`, `assessment/` or `tools/approach_a/` change, or the workflow itself changes. It can also be started by hand from the Actions tab |
| A test fails with "missing .../matrix.json" | The data file was deleted. Restore the empty marker or an accepted export |
| `git status` shows `assessment/preview/` | It should be gitignored. Check `.gitignore` was not changed |

