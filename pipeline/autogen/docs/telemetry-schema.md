# Telemetry Artifact Schema (v1)

**This is a stable contract.** The microsite dashboard consumes these files;
treat additive changes as safe and renames/removals as breaking (bump
`schema_version`).

Artifacts are written to `pipeline/autogen/logs/<task_id>_<run_id>.json`.

## Example

```json
{
  "schema_version": 1,
  "task_id": "001-add-delete-endpoint",
  "run_id": "d777d041a918",
  "model": {
    "label": "azure/gpt-4.1-mini",
    "profile": "azure-dev",
    "benchmark_valid": false
  },
  "timing": {
    "started_at": "2026-09-21T19:49:27.555132+00:00",
    "finished_at": "2026-09-21T19:49:34.013142+00:00",
    "wall_seconds": 5.31
  },
  "usage": {
    "call_count": 2,
    "prompt_tokens": 345,
    "completion_tokens": 25,
    "total_tokens": 370,
    "max_tokens": 15000,
    "token_efficiency": 97.53
  },
  "run": {
    "stop_reason": "Maximum number of messages 4 reached, current message count: 4",
    "network_isolated": true
  },
  "calls": [
    {
      "source": "model_client",
      "prompt_tokens": 160,
      "completion_tokens": 15,
      "total_tokens": 175,
      "latency_seconds": 1.182
    }
  ]
}
```

## Fields

| Path | Type | Notes |
|---|---|---|
| `schema_version` | int | Bumped on breaking changes. Currently `1`. |
| `task_id` | string | Matches a file in `pipeline/tasks/`. |
| `run_id` | string | Random 12-hex per run; two runs of one task never collide. |
| `model.label` | string | e.g. `azure/gpt-4.1-mini`. |
| `model.profile` | string | `local-dev`, `azure-dev`, or `azure-prod`. |
| **`model.benchmark_valid`** | bool | **Filter on this.** `false` means a cheap plumbing run, not a scored result. |
| `timing.started_at` / `finished_at` | ISO-8601 UTC | |
| `timing.wall_seconds` | float | End-to-end run duration. |
| `usage.call_count` | int | Number of model API calls. |
| `usage.prompt_tokens` | int | Summed across calls. |
| `usage.completion_tokens` | int | Summed across calls. |
| `usage.total_tokens` | int | `prompt + completion`. |
| `usage.max_tokens` | int? | The ceiling in force. Omitted if not supplied. |
| `usage.token_efficiency` | float? | **T** = `100 × max(0, 1 − total/max)`. Omitted with `max_tokens`. |
| `run.stop_reason` | string? | Which termination condition fired. |
| `run.network_isolated` | bool? | `true` when the sandbox had no outbound network. |
| `calls[].source` | string? | Origin of the call. |
| `calls[].latency_seconds` | float | Measured at the client boundary. |

## Consumer guidance

**Always filter on `model.benchmark_valid`.** The `logs/` directory will
contain plumbing-validation runs from `azure-dev` and `local-dev` alongside
real benchmark runs. Charting them together would compare a cheap dev model
against a production one and present it as a framework comparison.

`token_efficiency` is pre-computed so consumers need not reimplement the
formula. It may be absent on runs recorded without a ceiling.

## Implementation note: why not LiteLLM?

The project brief specifies LiteLLM's OpenTelemetry interceptor
(`LITELLM_OTEL_V2=true`). That was evaluated and **not** adopted, because
AutoGen v0.4 already exposes token usage directly, and LiteLLM would require
running a proxy process in front of Azure — a second network hop — purely to
re-derive numbers already in hand.

Per-call latency, however, is genuinely **not** available from AutoGen: a
`TaskResult` message carries `models_usage` but no timing. Rather than emit
`latency_seconds: 0.0` (indistinguishable from a measured zero),
`harness/instrumented_client.py` wraps the client and times each `create()`
call at the boundary.

If a future pipeline must benchmark a framework that does not report usage at
all, LiteLLM becomes the right tool **for that framework**. This schema is
deliberately source-agnostic so it can be populated either way without
changing the artifact format.
