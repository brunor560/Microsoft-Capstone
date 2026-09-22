"""Phase 4 tests for the latency-instrumenting client wrapper.

Fully offline: the inner client is a stub, so no API calls are made.
"""

from __future__ import annotations

import asyncio

import pytest

from harness.instrumented_client import InstrumentedChatCompletionClient
from harness.telemetry import RunTelemetry


class _Usage:
    def __init__(self, prompt_tokens, completion_tokens):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class _Result:
    def __init__(self, usage):
        self.usage = usage
        self.content = "stub reply"


class _StubClient:
    """Inner client that sleeps briefly so latency is measurably non-zero."""

    def __init__(self, *, delay=0.05, usage=None, fail=False):
        self.delay = delay
        self.usage = usage or _Usage(100, 20)
        self.fail = fail
        self.calls = 0
        self.closed = False
        self.model_info = {"family": "stub", "function_calling": True}

    async def create(self, messages, **kwargs):
        self.calls += 1
        await asyncio.sleep(self.delay)
        if self.fail:
            raise RuntimeError("upstream model error")
        return _Result(self.usage)

    def create_stream(self, messages, **kwargs):
        return "stream-sentinel"

    async def close(self):
        self.closed = True

    def actual_usage(self):
        return self.usage

    def total_usage(self):
        return self.usage

    def count_tokens(self, messages, **kwargs):
        return 42

    def remaining_tokens(self, messages, **kwargs):
        return 1000

    @property
    def capabilities(self):
        return {"stub": True}


def _telemetry():
    return RunTelemetry(
        task_id="t-1",
        model_label="stub/model",
        model_profile="stub",
        benchmark_valid=False,
    )


async def test_records_usage_and_real_latency():
    """The gap this wrapper exists to close: latency must be measured."""
    telemetry = _telemetry()
    client = InstrumentedChatCompletionClient(_StubClient(delay=0.05), telemetry)

    await client.create([])

    assert telemetry.call_count == 1
    call = telemetry.calls[0]
    assert call.prompt_tokens == 100
    assert call.completion_tokens == 20
    assert call.latency_seconds >= 0.05, "latency was not actually measured"


async def test_accumulates_across_calls():
    telemetry = _telemetry()
    client = InstrumentedChatCompletionClient(_StubClient(delay=0.01), telemetry)

    await client.create([])
    await client.create([])
    await client.create([])

    assert telemetry.call_count == 3
    assert telemetry.total_tokens == 360
    assert all(c.latency_seconds > 0 for c in telemetry.calls)


async def test_failed_call_records_nothing():
    """A failed call must not attribute phantom tokens to the run."""
    telemetry = _telemetry()
    client = InstrumentedChatCompletionClient(
        _StubClient(delay=0.01, fail=True), telemetry
    )

    with pytest.raises(RuntimeError, match="upstream model error"):
        await client.create([])

    assert telemetry.call_count == 0


async def test_missing_usage_is_treated_as_zero_not_an_error():
    """Some backends omit usage; the run must continue and stay countable."""
    telemetry = _telemetry()
    stub = _StubClient(delay=0.01)
    stub.usage = None
    client = InstrumentedChatCompletionClient(stub, telemetry)

    await client.create([])

    assert telemetry.call_count == 1
    assert telemetry.calls[0].total_tokens == 0
    assert telemetry.calls[0].latency_seconds > 0


async def test_close_is_delegated():
    stub = _StubClient()
    await InstrumentedChatCompletionClient(stub, _telemetry()).close()
    assert stub.closed is True


def test_delegates_pass_through_methods():
    stub = _StubClient()
    client = InstrumentedChatCompletionClient(stub, _telemetry())

    assert client.count_tokens([]) == 42
    assert client.remaining_tokens([]) == 1000
    assert client.model_info == stub.model_info
    assert client.create_stream([]) == "stream-sentinel"
