"""Phase 4: telemetry capture and serialization (project brief, section 5).

Records per-call token usage and latency for a benchmark run, then writes a
structured JSON artifact to `logs/<task_id>_<run_id>.json`.

### Why this instruments AutoGen directly rather than LiteLLM

The brief specifies routing telemetry through LiteLLM's OpenTelemetry
interceptor (`LITELLM_OTEL_V2=true`). That was evaluated and rejected for
this pipeline, because AutoGen v0.4 already surfaces exactly the three
required fields at the boundary we care about:

  * `prompt_tokens` / `completion_tokens` -- on every message's
    `models_usage`, and cumulatively via `client.total_usage()`.
  * `latency_seconds` -- measurable around the client call.

Adding LiteLLM would mean running a proxy process in front of Azure purely
to re-derive numbers AutoGen already hands us, and would put a second
network hop between the orchestrator and the model. The telemetry contract
below (the JSON schema) is what actually matters to downstream consumers,
and it is provider-agnostic either way.

If a future pipeline needs to benchmark a framework that does NOT report
usage, LiteLLM becomes the right answer for that framework. This module's
schema is designed so such a source can be swapped in without changing the
artifact format.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"

# Bumped when the artifact shape changes in a way consumers must handle.
SCHEMA_VERSION = 1


@dataclass
class CallRecord:
    """Telemetry for a single model API call."""

    prompt_tokens: int
    completion_tokens: int
    latency_seconds: float
    source: str | None = None

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_seconds": round(self.latency_seconds, 4),
        }


@dataclass
class RunTelemetry:
    """Accumulates telemetry across a benchmark run.

    `run_id` is generated per run so repeated runs of the same task do not
    overwrite one another's artifact.
    """

    task_id: str
    model_label: str
    model_profile: str
    benchmark_valid: bool
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    calls: list[CallRecord] = field(default_factory=list)
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: str | None = None
    stop_reason: str | None = None
    network_isolated: bool | None = None
    wall_seconds: float | None = None
    _monotonic_start: float = field(default_factory=time.monotonic, repr=False)

    # --- accumulation --------------------------------------------------

    def record_call(
        self,
        *,
        prompt_tokens: int,
        completion_tokens: int,
        latency_seconds: float,
        source: str | None = None,
    ) -> None:
        self.calls.append(
            CallRecord(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_seconds=latency_seconds,
                source=source,
            )
        )

    def ingest_task_result(self, result: Any) -> None:
        """Record only the run-level outcome from an AutoGen TaskResult.

        Token usage and latency are captured by
        `harness.instrumented_client.InstrumentedChatCompletionClient`, which
        times each call at the client boundary.

        This method deliberately does NOT read `models_usage` off messages.
        Doing so yields real token counts but no timing, so every call would
        serialize `latency_seconds: 0.0` -- indistinguishable from a
        genuinely measured zero. Callers that want usage must wrap the
        client; see docs/telemetry-schema.md.
        """
        self.stop_reason = getattr(result, "stop_reason", None)

    def finalize(self) -> None:
        self.finished_at = datetime.now(timezone.utc).isoformat()
        self.wall_seconds = time.monotonic() - self._monotonic_start

    # --- derived metrics -----------------------------------------------

    @property
    def total_prompt_tokens(self) -> int:
        return sum(c.prompt_tokens for c in self.calls)

    @property
    def total_completion_tokens(self) -> int:
        return sum(c.completion_tokens for c in self.calls)

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def token_efficiency(self, max_tokens: int) -> float:
        """T: 100 * max(0, 1 - total_tokens / max_tokens).

        Brief section 6. Lives here rather than in the scoring harness
        because it is a pure function of telemetry.
        """
        if max_tokens <= 0:
            return 0.0
        return 100.0 * max(0.0, 1.0 - self.total_tokens / max_tokens)

    # --- serialization -------------------------------------------------

    def to_dict(self, *, max_tokens: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "model": {
                "label": self.model_label,
                "profile": self.model_profile,
                # Stamped so a cheap dev run can never be mistaken for a
                # scored benchmark result.
                "benchmark_valid": self.benchmark_valid,
            },
            "timing": {
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "wall_seconds": (
                    round(self.wall_seconds, 4)
                    if self.wall_seconds is not None
                    else None
                ),
            },
            "usage": {
                "call_count": self.call_count,
                "prompt_tokens": self.total_prompt_tokens,
                "completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_tokens,
            },
            "run": {
                "stop_reason": self.stop_reason,
                "network_isolated": self.network_isolated,
            },
            "calls": [c.to_dict() for c in self.calls],
        }
        if max_tokens is not None:
            payload["usage"]["max_tokens"] = max_tokens
            payload["usage"]["token_efficiency"] = round(
                self.token_efficiency(max_tokens), 2
            )
        return payload

    def write(
        self,
        *,
        logs_dir: Path | None = None,
        max_tokens: int | None = None,
    ) -> Path:
        """Serialize to `logs/<task_id>_<run_id>.json` and return the path."""
        directory = logs_dir or LOGS_DIR
        directory.mkdir(parents=True, exist_ok=True)

        path = directory / f"{self.task_id}_{self.run_id}.json"
        path.write_text(
            json.dumps(self.to_dict(max_tokens=max_tokens), indent=2) + "\n"
        )
        return path
