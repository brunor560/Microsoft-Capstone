"""Per-call latency instrumentation (project brief, section 5).

AutoGen v0.4 reports token usage on each message (`models_usage`) but does
**not** expose per-call latency. Deriving telemetry from a `TaskResult` alone
therefore yields real token counts and no timing data.

Rather than serialize `latency_seconds: 0.0` -- which looks like a measured
zero rather than a missing measurement -- this wrapper times every
`create()` call at the client boundary and records it alongside usage.

The wrapper delegates by composition, so it works identically for the
Azure and OpenAI-compatible clients and adds no provider-specific code.
"""

from __future__ import annotations

import time
from typing import Any, Sequence

from autogen_core.models import ChatCompletionClient


class InstrumentedChatCompletionClient(ChatCompletionClient):
    """Wraps a ChatCompletionClient to record usage and latency per call.

    Every completed `create()` is appended to the supplied RunTelemetry.
    Streaming calls (`create_stream`) are delegated untimed; the agent loop
    used by this pipeline does not stream.
    """

    def __init__(self, inner: ChatCompletionClient, telemetry) -> None:
        self._inner = inner
        self._telemetry = telemetry

    # --- the instrumented path -----------------------------------------

    async def create(self, messages, **kwargs) -> Any:
        started = time.monotonic()
        try:
            result = await self._inner.create(messages, **kwargs)
        except Exception:
            # A failed call still consumed wall time; record nothing rather
            # than attribute phantom tokens to it.
            raise
        latency = time.monotonic() - started

        usage = getattr(result, "usage", None)
        self._telemetry.record_call(
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            latency_seconds=latency,
            source="model_client",
        )
        return result

    # --- delegation ----------------------------------------------------

    def create_stream(self, messages, **kwargs):
        return self._inner.create_stream(messages, **kwargs)

    async def close(self) -> None:
        await self._inner.close()

    def actual_usage(self):
        return self._inner.actual_usage()

    def total_usage(self):
        return self._inner.total_usage()

    def count_tokens(self, messages: Sequence[Any], **kwargs) -> int:
        return self._inner.count_tokens(messages, **kwargs)

    def remaining_tokens(self, messages: Sequence[Any], **kwargs) -> int:
        return self._inner.remaining_tokens(messages, **kwargs)

    @property
    def capabilities(self):
        return self._inner.capabilities

    @property
    def model_info(self):
        return self._inner.model_info
