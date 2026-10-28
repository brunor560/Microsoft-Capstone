# App brief verification — October 28, 2026

AI-assisted candidate research; documentation only. These checks are not human authorship, independent review, manifest approval, runtime testing, or H-9 acceptance.

## Result

All 18 App briefs were exercised in an isolated rehearsal dataset using the existing workbench: 18 drafted, zero pending, zero rejected citations, and zero blocking evidence-challenge flags. All 31 short citations were matched inside their named sections. Two warnings remain: the Plans page lacks a machine-readable surface badge for F17/F18. Its App breadcrumb was inspected, but applicability still needs human review. Shared-page notes are informational; App-specific sections were preferred.

The live HTML was fetched from official documentation on October 28 and converted with `tools.approach_a.pages.to_text`. The rehearsal reused that snapshot offline, disabled Azure drafting, and recorded no human identity. No assessed-tool execution, benchmark runs or Azure model calls were made. The active dataset and generated outputs were not modified.

The final rehearsal validation is intentionally **NOT ACCEPTED**: 18 missing authors, 18 missing independent reviews, one missing manifest approval, and one unconfirmed boundary. This is the expected state of a candidate-only contribution.

| Feature | Proposed status | Verified citations |
| --- | --- | ---: |
| F01 | Built in | 2 |
| F02 | Built in | 1 |
| F03 | Not established from documentation | 2 |
| F04 | Built in | 2 |
| F05 | Built in | 2 |
| F06 | Built in | 2 |
| F07 | Built in | 2 |
| F08 | Not established from documentation | 2 |
| F09 | Not established from documentation | 2 |
| F10 | Built in | 1 |
| F11 | Built in | 2 |
| F12 | Built in | 1 |
| F13 | Built in | 3 |
| F14 | Built in | 2 |
| F15 | Built in | 1 |
| F16 | Not established from documentation | 2 |
| F17 | Not established from documentation | 1 |
| F18 | Not established from documentation | 1 |

## Existing-brief corrections

- F02: replaced a quote absent from the current plan page; removed the unsupported explicit invocation claim from that brief.
- F08: replaced the removed business/enterprise sentence. The updated sandbox table still names only Linux/macOS mechanisms; Windows conditions remain under previous settings. Kept the Windows/account mapping unresolved rather than assuming unavailability.
- F01, F07 and F10: existing citations still match the fetched sections.

## Review focus

- Confirm that the proposed standalone App surface represents the product being assessed; do not transfer IDE or CLI observations.
- Confirm free-tier versus the operator's Pro/student benchmark subscription. No tier was silently changed.
- F03, F08, F09, F16, F17 and F18 are documentation gaps, never zero scores or claims of unsupported capability.
- F04 establishes file inspection, not a particular indexing implementation; F05 does not guarantee atomic edits.
- F06 establishes execution, not successful automated repair. F11 does not establish cancellation semantics.
- F12 covers unstaged file discard only. F15 establishes partial Git integration, not PR/CI/deployment completeness.
- F13/F14 assess native mechanisms without adding skills or servers. Review the scope of shared documentation.

## Reproduce

The existing offline suite passed: 44 tests, zero failures. `git diff --check` also passed.

Run the offline unit suite from the repository root:

```powershell
python -m unittest discover -s tools/approach_a/tests -t .
```

For a fresh live-source rehearsal, choose a new scratch dataset path. Do not reset the active assessment:

```powershell
python -m tools.approach_a --data ../antigravity-app-rehearsal init
python -m tools.approach_a --data ../antigravity-app-rehearsal start --tool antigravity --surface app --rehearsal --yes --research --no-draft
```

The second command should draft all 18 if the cited sections remain available. It exits 1 because candidate approval/review is absent. Quote matches and cell counts may change with live documentation. `--no-draft` prevents Azure requests.

## Source snapshot hashes

SHA-256 values below identify workbench-converted page text, not raw HTML. Full vendor pages are not committed. Access date: 2026-10-28; pages are rolling documentation, not proof of a pinned release.

| Official page | Converted-text SHA-256 |
| --- | --- |
| https://antigravity.google/docs/agent-settings/ | `b6e1f70f6aeb8a7b345c013f7d49b75524e285a90b76252ea87ce74a0be00dbd` |
| https://antigravity.google/docs/artifact-review/ | `b9bceaf84c38f8df98996270f315fe1b1b8b064a957070cc6868ca74e5ec9dc3` |
| https://antigravity.google/docs/artifacts/ | `ad76dff7d9925e56e9a7f75ec842808fda3aa73ecf617a4d85a08200347c6e7d` |
| https://antigravity.google/docs/features/ | `e7155d68fc6dc390e396f80d3370617011a5ea8ee562e3cbbbd0e8340fa966d7` |
| https://antigravity.google/docs/implementation-plan/ | `052541eda38446c25e02af5638521caffb4c5bd8a07e8720beba292ed703b413` |
| https://antigravity.google/docs/mcp/ | `d45079ff4755487c4647d90ce5e12b21e26969947ce8ebe65f8299b398b206ec` |
| https://antigravity.google/docs/permissions/ | `fecc592dae5aa974614b25ff4dad453cf25750412c8bc154b74baee734ca800c` |
| https://antigravity.google/docs/plans/ | `5f6ba31056b09d516e10b6b57ff24444de3774d941e6e1bfd7e81c2458baead5` |
| https://antigravity.google/docs/projects/ | `e2910f7f2c2de61403a82b554ebb956b3a6322e4f11b55c42d7c233f3fb40ac4` |
| https://antigravity.google/docs/rules/ | `cd02d138b191489512d45773a9c74afc06a625f1edcf637636db4eea8e1d03e2` |
| https://antigravity.google/docs/sandbox/ | `fd2c2af2fda9cc857cb17457a3b0187058b11d03e727d6f67dadd4531bd01ca5` |
| https://antigravity.google/docs/settings/ | `bb458429d8059523484e147c7d0587fcf9705789f0ba6ce53770728664a42edd` |
| https://antigravity.google/docs/skills/ | `cf27331586fe563eba0a10df057d581b58269a3c8e8268ab12ffc6bf027d0141` |
| https://antigravity.google/docs/walkthrough/ | `3b81afe09823aa66c32e1b278f2c9496396d93606d0b7e4707a2d3ea572f54a8` |
