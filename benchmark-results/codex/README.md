# Codex CLI benchmark results

This results collection preserves Joseph's two successful DELETE-endpoint attempts, their generated code, independent test outputs, and token records. Both runs used a fresh snapshot of commit `be98d692807da26dac3c3a720d4d5cf157e9717d` from `benchmark-start-v1` and the same initial task prompt.

| Run | Model / reasoning | Local tests | Acceptance tests | Supplemental test | Total session time | Input tokens, including cached | Cached input tokens | Output tokens |
|---|---|---|---|---|---:|---:|---:|---:|
| [run01](run01/README.md) | GPT-6.1 Sol / low | 7/7 | 9/9 | 1/1 | 129.1 seconds | 112,815 | 100,864 | 1,527 |
| [run02](run02/README.md) | GPT-6 Luna / low | 7/7 | 9/9 | 1/1 | 47.397 seconds | 160,381 | 143,616 | 1,945 |

The Sol interface separately displayed 49 seconds of work. Total session time includes startup and operator time before exit; Sol used manual prompt entry, while Luna's runner submitted it automatically. The two total times should not be treated as a controlled comparison of coding speed.

Cached input is a subset of the input column, not an additional amount to add to it. Including cached input, total usage was 114,342 tokens for Sol and 162,326 for Luna. Dollar cost was not captured under ChatGPT authentication and remains unavailable. Each report links its machine-readable token counters.

## Evidence and scope

Each run folder contains the original generated server and test files, all three verification outputs, a report, and token usage. Luna also includes its submitted prompt and run metadata. Neither run required corrective coding feedback. Approval counts were not recorded. Before/after hash checks identified only the permitted `app/server.js` and `app/test.js` changes in the temporary run workspaces.

Saved JavaScript files are evidence copies, not replacements for the repository's application files. No reference implementation was put into the agent workspaces. The participant knew the task and supplemental leading-zero check before the runs, so they are not blind trials. Full conditions and limitations are recorded in the individual reports.

## Relationship to the master specifications

The [feature matrix specification](../../agentic_developer_feature_matrix_specification.md) defines a documentation-only assessment and explicitly separates live benchmarks from that deliverable. These results belong to the separate execution pilot and do not validate documentation-based feature claims or establish a general tool ranking.

The [task matrix](../../pipeline/tasks/README.md) defines shared benchmark tasks. These attempts used the preserved `benchmark-start-v1` version of task `001-add-delete-endpoint`, identified by the starting commit above, rather than silently substituting the current master task.

The [AutoGen telemetry contract](../../pipeline/autogen/docs/telemetry-schema.md) defines artifacts for its scoring pipeline. These CLI attempts were not AutoGen runs: no weighted score, token-efficiency ceiling, or `model.benchmark_valid` value has been invented for them. Their evidence remains under `benchmark-results/codex/` rather than being presented as scored AutoGen telemetry.
