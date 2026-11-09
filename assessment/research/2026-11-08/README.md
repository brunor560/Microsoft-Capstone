# CLI and Windows app research — November 8, 2026

**Proposed research, not accepted findings.** Eight documentary profiles, 144
feature cells, all drafted and mechanically challenged. No profile confirmation,
human authorship, independent review or manifest approval has been recorded.
The existing active dataset at `assessment/` remains byte-for-byte unchanged.
This is a separate candidate dataset for the team's adoption decision.

| Tool | CLI profile and platform | Windows app profile | Proposed account baseline |
| --- | --- | --- | --- |
| Google Antigravity | `antigravity-cli`: original multi-platform CLI scope, with Windows restrictions recorded per feature | `antigravity-app-windows`: native App; current and previous permission settings distinguished | Individual personal Google account, no Pro/Ultra |
| Claude Code | `claude-cli`: Ubuntu 24.04 | `claude-app-windows`: local Code tab in Claude Desktop, Windows 11 | Claude Pro, Anthropic sign-in |
| Codex | `codex-cli`: native Windows 11, PowerShell | `codex-app-windows`: Codex in the ChatGPT desktop app, Windows native agent | ChatGPT Plus, ChatGPT sign-in |
| GitHub Copilot | `copilot-cli`: macOS Apple silicon | `copilot-app-windows`: native GitHub Copilot app, Windows 11 | Copilot Free, GitHub sign-in |

These are concrete proposals for confirmation, not claims about a person's paid
subscription or approved team choices. Eligibility documentation is in
[profile-boundary-evidence.json](profile-boundary-evidence.json). The two surfaces
remain separate even when documentation explicitly shares configuration. Desktop
chat, cloud, SSH, WSL, IDE extensions, added skills/plugins/MCP servers and enterprise
administration are excluded from desktop profiles. No Cursor profile was added.

All eight use **rolling official documentation**, not an installed binary version.
In particular, newer Antigravity CLI documentation is not attributed to the
existing active version-1.4.0 profile. The historical manifest and human-owned cell
were not modified. No benchmark results are used as feature evidence.

## Read the findings

- [Manifest and boundaries](out/manifest.md)
- [Matrix](out/matrix.md) and [per-cell records](out/cells/)
- [Source index with sections and quotations](out/sources.md)
- [Structural validation report](out/validation_report.md)
- [Work log](out/worklog.md)
- [Machine-readable research summary](research-summary.json)
- [Source retrieval and hash audit](source-audit.json)
- [Expected publication refusal](publication-check.txt)
- [Fresh citation recheck](citation-verification.json) and [input hashes](input-hashes.json)

The retained 178 cell citations all match their named sections, with **zero
rejected citations**. The source index contains 166 evidence entries: 164 are referenced by current
cells or boundary notes, and two superseded passages are retained for audit.
Identical quotations can be shared across cells.
The automated challenge pass checked all 144 cells: **zero blocking flags**,
73 `surface_unconfirmed` warnings, 15 informational shared-page notes, and one
informational release-note source flag. Source warnings mean the page or heading
lacks the workbench's machine-readable product-surface label; humans must check
applicability. Neither quotation matching nor the automated pass is independent
review or proof of a capability.

93 official pages were retrieved successfully. 72 pages supply retained feature
or boundary citations. The source audit also retains 13 failed/stale discovery
URLs and official redirects. Failed URLs are not used to infer unsupported
capabilities. Raw HTML and converted text stay in the locally ignored `.cache/`;
only short quotations, source URLs, access dates and hashes enter this packet.
The audit distinguishes raw-HTML hashes from converted-text hashes and identifies
the parser source used for conversion.

There are 110 proposed Built in statuses (often partial scope) and 34 completed
Not established findings with specific gap explanations. These are workflow
counts, not capability totals or rankings. Supported, explicitly unsupported and
unestablished subcapabilities remain separate in every cell. Read scope and setup
before treating any broad feature as covered.

## Material review questions

- Confirm all eight boundaries and exact account baselines. Product/plan eligibility
  documentation is not the team's choice of account or approval of a manifest.
- Check every affirmative claim against the cited passage, especially any shared
  CLI/desktop configuration and all surface-applicability warnings.
- Plans and issue context are not formal requirement-to-code-to-test traceability.
  F03 remains unestablished for all profiles.
- Provider sign-in, credential storage and sandbox credential restrictions do not
  establish the full application-secret lifecycle; F09 remains unestablished.
- Distinguish native Windows sandbox implementations and supported OS/update
  requirements from WSL/cloud isolation and from Git worktrees. Antigravity's
  updated and previous App settings still need version/account mapping review.
- Review F12 file-only recovery limits, F15 partial Git/PR/CI support, and F16
  transcript visibility versus a complete exportable audit record.
- F17 distinguishes tokens, context utilization, plan quotas, credits and dollars.
  F18 distinguishes CLI print/autopilot limits from desktop and subscription limits.
  Current Antigravity headless docs say no time limit by default and document an
  explicit print timeout; do not reuse the old five-minute default claim.

## Local preview and checks

From the repository root:

```bash
python3 -m tools.approach_a --data assessment/research/2026-11-08 export-publication --mode preview
python3 -m tools.approach_a serve-preview --port 4174
```

Open `http://127.0.0.1:4174/feature-matrix/?preview=matrix.preview.json`.
It is labeled **Draft — not accepted** and contains the eight profiles and 144
cells. Proposed tiers remain visibly unestablished in Shortlist until the team
confirms them. The previous integration preview is preserved locally at
`assessment/preview/matrix.before-expanded-research.json`; the fictional Shortlist
fixture is separate. Nothing from this packet is inside the Pages upload root.

The existing tools can inspect or regenerate this packet:

```bash
python3 -m tools.approach_a --data assessment/research/2026-11-08 status
python3 -m tools.approach_a --data assessment/research/2026-11-08 show F08 --profile codex-app-windows
python3 -m tools.approach_a --data assessment/research/2026-11-08 validate --brief
python3 -m tools.approach_a --data assessment/research/2026-11-08 render
```

Validation intentionally returns NOT ACCEPTED, with **297 blockers**:
`BOUNDARY_UNCONFIRMED` ×8, `AUTHOR_MISSING` ×144, `REVIEW_MISSING` ×144,
and `APPROVAL_MISSING` ×1. The accepted exporter was checked and refused before
writing. The public `dashboard/feature-matrix/data/matrix.json` remains unchanged.

69 offline Python tests and 27 Node page tests passed. The research uncovered a
nested-heading parser defect, fixed in `tools/approach_a/pages.py` with two targeted
regressions; section citations now retain headings containing vendor anchor/div
markup. Existing tests emitted their existing unclosed-file ResourceWarnings.
No assessed developer tool was installed or run. No additional Azure drafting
requests, remote repository changes, publishing or deployment occurred.

This packet was prepared by Codex with AI assistance. The session model identity
was not exposed and is recorded as unknown. The operator session also had repository
and UI integration context; it was not an isolated documentation-only model
session. Official documentation supplied feature evidence; no execution/benchmark
outputs support findings. The work log records that distinction and the purpose
of the research. Raw provider token accounting for this assistant session is not
available; no zero-cost claim is made for the assistant's work.

## Human adoption steps

1. Confirm the proposed platforms, surfaces, tiers and exclusions, and decide
   whether to adopt this separate dataset as the selected assessment.
2. A team member checks each claim, takes responsibility for its cell, and corrects
   any unsupported interpretation. A different member reviews each current cell
   hash and records agreement or resolved disagreement.
3. The authorized approver approves the selected manifest version. Revalidate the
   entire selected dataset before exporting accepted public JSON.
4. Coordinate UI review with the microsite owner. A dashboard header link, push,
   merge and deployment remain separate later actions; none were performed here.
