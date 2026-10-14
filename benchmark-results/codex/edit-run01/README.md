# Codex title-edit benchmark

Joseph B. ran GPT-6.1 Sol (`gpt-6.1-sol`) with light/`low` reasoning through headless Codex CLI `0.162.0-alpha.17.2` on October 14, 2026. The successful fresh attempt passed 13 local tests, 12 independent API tests, and 10 independent browser tests. All grader exit codes were zero. Only the three allowed files changed; all nine original tests were preserved and four API tests were added.

Baseline commit: `4e258a96855d98edd10247f68c0b8265e53a8921`. Team-agreed evaluator: `02996447e01bb284939d9b1a83c45ab033c22fb9`, confirmed by the operator. Joseph reported that grader hashes match other participants.

## Attempts and setup

`setup-history/` preserves the transcripts, stderr, and timing of two setup-blocked sessions. Both reported policy rejection before reading the task and made no changes. Their measured invocation times were 20.214 and 14.311 seconds. Independent grading of the unchanged blocked session 01 baseline passed 9/9 local, 5/12 API, and 0/10 browser tests. The second blocked session retained identical baseline source; it was not graded separately. Full unchanged-baseline grading logs are retained outside the repository.

A separate setup diagnostic only printed the working directory. Explicitly setting the Windows sandbox backend to elevated and ignoring execution rules allowed shell execution. The successful attempt used a new isolated baseline snapshot and fresh coding session; it received the exact initial prompt without grader feedback or implementation hints. It required no coding correction.

## Successful run conditions

Windows/PowerShell, Node v24.21.0, npm 11.19.0, Playwright 1.64.1. Approval policy `never`, sandbox `workspace-write`, Windows backend `elevated`. User configuration and local execution rules were ignored. Memory and external memory import were explicitly disabled, as were apps, plugins, hooks, multi-agent tools and host skill discovery. No previous conversation was passed to the session. The successful invocation inherited desktop CODEX environment variables; these were removed in blocked session 02 but retained for the successful diagnostic and the successful attempt. Automatically loaded instruction details beyond the recorded launch flags were not independently inventoried and remain unknown.

Memory was not explicitly disabled in blocked session 01, whose launch preceded the operator's no-memory instruction. It was explicitly disabled in blocked session 02, the diagnostic, and the successful attempt. The setup assistant had read the benchmark procedure and older delete-run reports. Operator prior knowledge of title-edit graders/reference was not answered and remains unknown. Setup assistance and blocked attempts must be disclosed when comparing results.

## Timing and usage

The successful attempt took 72.622 seconds, measured with a PowerShell Stopwatch immediately before piping the exact prompt into a new CLI invocation until process return. This includes CLI startup and final process shutdown; exact prompt-to-final-event time was not measured separately. Approval waiting was zero under policy `never`.

CLI-reported successful-turn usage: 138,660 input tokens, including 123,264 cached input tokens; 3,124 output tokens. Cached input is a subset of input. The JSON usage record also reports 76 reasoning output tokens. Monetary cost is unavailable. Setup attempts and diagnostic have separate usage events in their preserved transcripts; they are not included in the successful-turn counts above.

## Evidence

The repository package follows Antigravity's edit-run layout: original source snapshots, exact prompt and final report, one successful-session transcript, manifests, provenance, configuration, timing, usage, independent suite logs and exit codes, scope review, and the successful browser report/results. Minimal blocked-session transcripts and timing remain in setup-history/ so setup problems are disclosed. Duplicate baseline source/manifests, blocked-baseline browser reports/traces, the diagnostic transcript, and other redundant setup artifacts are retained outside the repository in ../codex-edit-publication-full-evidence and the original run evidence folders. Grader source and installed dependencies are excluded from the publication package.

The agent reported that it performed no browser checks; the operator subsequently ran the independent browser suite. Its local test count and allowed-file report were verified. Review the recorded limitations before comparisons: one task and attempt do not establish a general tool winner.

This evidence package is prepared on a separate results branch. No commit or push has been performed.


