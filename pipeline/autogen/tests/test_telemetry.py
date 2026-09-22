"""Phase 4 tests for telemetry capture and serialization. Fully offline."""

from __future__ import annotations

import json

import pytest

from harness.telemetry import SCHEMA_VERSION, RunTelemetry


def _telemetry(**overrides) -> RunTelemetry:
    defaults = dict(
        task_id="001-add-delete-endpoint",
        model_label="azure/gpt-4.1-mini",
        model_profile="azure-dev",
        benchmark_valid=False,
    )
    defaults.update(overrides)
    return RunTelemetry(**defaults)


# --- accumulation ------------------------------------------------------------


def test_starts_empty():
    t = _telemetry()
    assert t.call_count == 0
    assert t.total_tokens == 0


def test_records_calls_and_sums_tokens():
    t = _telemetry()
    t.record_call(prompt_tokens=100, completion_tokens=40, latency_seconds=1.2)
    t.record_call(prompt_tokens=250, completion_tokens=60, latency_seconds=0.8)

    assert t.call_count == 2
    assert t.total_prompt_tokens == 350
    assert t.total_completion_tokens == 100
    assert t.total_tokens == 450


def test_run_id_is_unique_per_instance():
    """Two runs of the same task must not overwrite each other's artifact."""
    assert _telemetry().run_id != _telemetry().run_id


# --- T (token efficiency) ----------------------------------------------------


def test_token_efficiency_is_100_when_unused():
    assert _telemetry().token_efficiency(15000) == 100.0


def test_token_efficiency_half_budget():
    t = _telemetry()
    t.record_call(prompt_tokens=7000, completion_tokens=500, latency_seconds=0.0)
    # 1 - 7500/15000 = 0.5
    assert t.token_efficiency(15000) == 50.0


def test_token_efficiency_exact_budget_is_zero():
    t = _telemetry()
    t.record_call(prompt_tokens=15000, completion_tokens=0, latency_seconds=0.0)
    assert t.token_efficiency(15000) == 0.0


def test_token_efficiency_is_floored_at_zero_when_over_budget():
    """Exceeding the cap must not produce a negative T."""
    t = _telemetry()
    t.record_call(prompt_tokens=30000, completion_tokens=5000, latency_seconds=0.0)
    assert t.token_efficiency(15000) == 0.0


def test_token_efficiency_with_zero_budget_is_zero():
    """Guard against division by zero rather than raising mid-run."""
    assert _telemetry().token_efficiency(0) == 0.0


# --- ingesting an AutoGen TaskResult ----------------------------------------


class _Usage:
    def __init__(self, prompt_tokens, completion_tokens):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class _Message:
    def __init__(self, source, usage):
        self.source = source
        self.models_usage = usage


class _Result:
    def __init__(self, messages, stop_reason):
        self.messages = messages
        self.stop_reason = stop_reason


def test_ingest_records_stop_reason():
    t = _telemetry()
    t.ingest_task_result(
        _Result(
            messages=[_Message("coder", _Usage(120, 30))],
            stop_reason="Maximum number of messages 4 reached",
        )
    )
    assert t.stop_reason == "Maximum number of messages 4 reached"


def test_ingest_does_not_record_usage_from_messages():
    """Usage must come from the instrumented client, not TaskResult.

    Reading `models_usage` off messages yields real token counts but no
    timing, so every call would serialize latency_seconds: 0.0 -- which is
    indistinguishable from a measured zero. This asserts we do not
    silently regress to that path.
    """
    t = _telemetry()
    t.ingest_task_result(
        _Result(
            messages=[
                _Message("user", None),
                _Message("coder", _Usage(120, 30)),
                _Message("coder", _Usage(200, 45)),
            ],
            stop_reason="done",
        )
    )

    assert t.call_count == 0, "usage must not be harvested from messages"
    assert t.total_tokens == 0


# --- serialization -----------------------------------------------------------


def test_write_produces_expected_filename(tmp_path):
    t = _telemetry()
    path = t.write(logs_dir=tmp_path)
    assert path.name == f"001-add-delete-endpoint_{t.run_id}.json"


def test_artifact_is_valid_json_with_stable_schema(tmp_path):
    t = _telemetry()
    t.record_call(prompt_tokens=100, completion_tokens=50, latency_seconds=1.5)
    t.network_isolated = True
    t.finalize()

    payload = json.loads(t.write(logs_dir=tmp_path, max_tokens=15000).read_text())

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["task_id"] == "001-add-delete-endpoint"
    assert payload["usage"]["total_tokens"] == 150
    assert payload["usage"]["max_tokens"] == 15000
    assert payload["usage"]["token_efficiency"] == 99.0
    assert payload["run"]["network_isolated"] is True
    assert payload["timing"]["wall_seconds"] is not None


def test_artifact_stamps_benchmark_validity(tmp_path):
    """A dev-model run must be distinguishable from a scored benchmark."""
    payload = json.loads(_telemetry().write(logs_dir=tmp_path).read_text())

    assert payload["model"]["profile"] == "azure-dev"
    assert payload["model"]["label"] == "azure/gpt-4.1-mini"
    assert payload["model"]["benchmark_valid"] is False


def test_token_efficiency_omitted_when_no_budget_given(tmp_path):
    payload = json.loads(_telemetry().write(logs_dir=tmp_path).read_text())
    assert "token_efficiency" not in payload["usage"]


def test_logs_dir_is_created_if_absent(tmp_path):
    target = tmp_path / "nested" / "logs"
    path = _telemetry().write(logs_dir=target)
    assert path.exists()
