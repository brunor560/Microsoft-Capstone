"""Phase 4 gate: live telemetry capture and serialization.

Runs a real agent loop and proves the telemetry artifact is produced with
populated token counts -- the fields T (token efficiency) depends on.

Usage:
    ./.venv/bin/python -m harness.verify_telemetry --model-profile azure-dev
"""

from __future__ import annotations

import argparse
import asyncio
import json

from harness.executor import IsolatedDockerCodeExecutor, probe_network
from harness.instrumented_client import InstrumentedChatCompletionClient
from harness.model_profiles import Limits, ProfileError, build_client, load_profile
from harness.orchestrator import build_orchestration
from harness.staging import stage_workspace
from harness.tasks import load_all_tasks
from harness.telemetry import RunTelemetry

IMAGE = "agentic-eval-sandbox:latest"


async def run(profile_name: str | None) -> int:
    failures: list[str] = []

    try:
        profile = load_profile(profile_name)
    except ProfileError as exc:
        print(f"PHASE 4 GATE: FAILED\n  {exc}")
        return 1

    task = load_all_tasks()[0]
    print(f"profile : {profile.name}  ({profile.label})")
    print(f"task    : {task.task_id}\n")

    # Tight ceilings keep the gate cheap; real limits live in models.yaml.
    gate_limits = Limits(max_consecutive_auto_replies=2, max_total_tokens=4000)

    telemetry = RunTelemetry(
        task_id=task.task_id,
        model_label=profile.label,
        model_profile=profile.name,
        benchmark_valid=profile.benchmark_valid,
    )

    # Wrap the client so every call's latency is measured at the boundary.
    # AutoGen does not expose per-call timing on TaskResult messages.
    model_client = InstrumentedChatCompletionClient(build_client(profile), telemetry)

    with stage_workspace() as workspace:
        executor = IsolatedDockerCodeExecutor(
            image=IMAGE, work_dir=workspace.path, timeout=120
        )
        await executor.start()
        try:
            telemetry.network_isolated = not await probe_network(executor)

            orchestration = build_orchestration(
                model_client,
                limits=gate_limits,
                code_executor=executor,
                scripted_input=["", "", ""],
            )

            print("--- live agent run ---")
            result = await orchestration.run(
                "Inspect /workspace by emitting one bash code block that lists "
                "its files. Do not modify anything. Then state that you are done."
            )
            # Usage/latency already captured by the instrumented client;
            # take only the stop reason from the result.
            telemetry.stop_reason = getattr(result, "stop_reason", None)
        finally:
            await executor.stop()
            await model_client.close()

    telemetry.finalize()

    print(f"  calls recorded    : {telemetry.call_count}")
    print(f"  prompt_tokens     : {telemetry.total_prompt_tokens}")
    print(f"  completion_tokens : {telemetry.total_completion_tokens}")
    print(f"  total_tokens      : {telemetry.total_tokens}")
    print(f"  wall_seconds      : {telemetry.wall_seconds:.2f}")
    print(f"  network_isolated  : {telemetry.network_isolated}")
    print(
        f"  T (vs {profile.limits.max_total_tokens}) : "
        f"{telemetry.token_efficiency(profile.limits.max_total_tokens):.2f}"
    )

    if telemetry.call_count == 0:
        failures.append("no model calls were recorded")
    if telemetry.total_tokens == 0:
        failures.append("token counts are zero; T would be meaningless")

    # Brief section 5 requires latency_seconds. A serialized 0.0 looks like a
    # measured zero rather than a missing measurement, so assert it is real.
    latencies = [c.latency_seconds for c in telemetry.calls]
    if latencies and all(latency <= 0 for latency in latencies):
        failures.append("latency_seconds is zero for every call; not instrumented")
    else:
        print(f"  latency per call  : {[round(x, 3) for x in latencies]}")

    path = telemetry.write(max_tokens=profile.limits.max_total_tokens)
    print(f"\n--- artifact ---\n  {path}")

    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"  FAIL artifact is not valid JSON: {exc}")
        return 1

    for key in ("schema_version", "task_id", "run_id", "model", "usage", "calls"):
        if key not in payload:
            failures.append(f"artifact missing '{key}'")

    if payload.get("usage", {}).get("total_tokens", 0) <= 0:
        failures.append("artifact reports zero total_tokens")

    if payload.get("model", {}).get("benchmark_valid") is not profile.benchmark_valid:
        failures.append("artifact does not stamp benchmark validity correctly")

    print(f"  schema_version={payload['schema_version']} "
          f"total_tokens={payload['usage']['total_tokens']} "
          f"T={payload['usage'].get('token_efficiency')}")

    print()
    if failures:
        print(f"PHASE 4 GATE: FAILED ({len(failures)} problem(s))")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PHASE 4 GATE: PASSED")
    print("  Telemetry captured with real token counts and serialized to logs/.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-profile", dest="model_profile", default=None)
    args = parser.parse_args()
    return asyncio.run(run(args.model_profile))


if __name__ == "__main__":
    raise SystemExit(main())
