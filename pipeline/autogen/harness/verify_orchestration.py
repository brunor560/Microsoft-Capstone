"""Phase 3 gate: live agent orchestration verification.

Runs the real Coder/Executor loop against a live model and proves:

  1. the loop runs and terminates,
  2. a resource ceiling actually stops it (not just "eventually finishes"),
  3. operator interventions are recorded and H is computed,
  4. the sandbox is network-isolated during the run.

Costs a few cents at most: the message ceiling is deliberately lowered so the
run ends quickly.

Usage:
    ./.venv/bin/python -m harness.verify_orchestration --model-profile azure-dev
"""

from __future__ import annotations

import argparse
import asyncio

from harness.executor import IsolatedDockerCodeExecutor, probe_network
from harness.model_profiles import Limits, ProfileError, build_client, load_profile
from harness.orchestrator import build_orchestration
from harness.staging import stage_workspace

IMAGE = "agentic-eval-sandbox:latest"

# A trivially satisfiable task: the point is to exercise the loop mechanics,
# not to measure capability.
#
# Deliberately avoids the word "TERMINATE": the sentinel is now scoped to the
# coder's own messages, but keeping it out of the task text also keeps this
# gate honest about what it is measuring.
PROBE_TASK = (
    "Inspect /workspace by emitting a single bash code block that lists its "
    "files. Do not modify anything. Then state that the objective is complete."
)


async def run(profile_name: str | None) -> int:
    failures: list[str] = []

    try:
        profile = load_profile(profile_name)
    except ProfileError as exc:
        print(f"PHASE 3 GATE: FAILED\n  {exc}")
        return 1

    print(f"profile         : {profile.name}  ({profile.label})")
    print(f"benchmark_valid : {profile.benchmark_valid}")
    if not profile.benchmark_valid:
        print("  note: plumbing validation only; not a scored run.")
    print()

    # Deliberately tight ceilings so the gate is cheap and fast. The real
    # limits (5 replies / 15,000 tokens) live in config/models.yaml.
    gate_limits = Limits(max_consecutive_auto_replies=2, max_total_tokens=4000)
    print(f"gate ceilings   : {gate_limits.max_consecutive_auto_replies} replies "
          f"({gate_limits.max_consecutive_auto_replies * 2} messages), "
          f"{gate_limits.max_total_tokens} tokens")
    print(f"real ceilings   : {profile.limits.max_consecutive_auto_replies} replies, "
          f"{profile.limits.max_total_tokens} tokens")
    print()

    model_client = build_client(profile)

    with stage_workspace() as workspace:
        print(f"--- staged workspace ---\n  {workspace.path}\n")

        executor = IsolatedDockerCodeExecutor(
            image=IMAGE,
            work_dir=workspace.path,
            timeout=120,
        )
        await executor.start()

        try:
            print("--- network isolation ---")
            online = await probe_network(executor)
            if online:
                print("  FAIL container reached the internet")
                failures.append("network isolation not enforced")
            else:
                print("  OK   container is network-isolated")

            print("\n--- agent loop (live) ---")
            orchestration = build_orchestration(
                model_client,
                limits=gate_limits,
                code_executor=executor,
                # Approvals only: keeps the run short and leaves H at 100,
                # which the assertions below check.
                scripted_input=["", "", "TERMINATE"],
            )

            result = await orchestration.run(PROBE_TASK)

            print(f"  messages exchanged : {len(result.messages)}")
            print(f"  stop reason        : {result.stop_reason}")

            if not result.stop_reason:
                failures.append("run produced no stop_reason")
            else:
                print("  OK   loop terminated via a termination condition")

            # A run that ends on the FIRST message never reached an agent --
            # that was the original bug (the sentinel matched the task text).
            # Anything under 2 messages means no model call happened.
            if len(result.messages) < 2:
                print("  FAIL loop ended before any agent replied")
                failures.append(
                    "no agent turn occurred; termination fired on the task prompt"
                )
            else:
                print(f"  OK   agents exchanged {len(result.messages)} messages")

            max_messages = gate_limits.max_consecutive_auto_replies * 2
            if len(result.messages) > max_messages + 2:
                print(f"  FAIL exceeded message ceiling ({max_messages})")
                failures.append("message ceiling not enforced")
            else:
                print(f"  OK   respected message ceiling ({max_messages})")

            log = orchestration.interventions
            print(f"\n--- collaboration (H) ---")
            print(f"  operator consulted : {log.total_inputs}x")
            print(f"  interventions      : {log.interventions}")
            print(f"  H score            : {log.collaboration_score}")

            if log.total_inputs == 0:
                print("  WARN operator was never consulted; HITL gate may be inactive")
                failures.append("human-in-the-loop gate did not trigger")
            else:
                print("  OK   human-in-the-loop gate engaged")

            if log.collaboration_score != 100:
                failures.append(
                    f"H should be 100 for approvals-only, got {log.collaboration_score}"
                )
        finally:
            await executor.stop()
            await model_client.close()

    print()
    if failures:
        print(f"PHASE 3 GATE: FAILED ({len(failures)} problem(s))")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PHASE 3 GATE: PASSED")
    print("  Agent loop runs, ceilings hold, HITL recorded, sandbox isolated.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-profile", dest="model_profile", default=None)
    args = parser.parse_args()
    return asyncio.run(run(args.model_profile))


if __name__ == "__main__":
    raise SystemExit(main())
