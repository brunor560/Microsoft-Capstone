#!/usr/bin/env python
"""Agentic IDE Evaluation Suite -- benchmark runner.

Wires together every phase of the pipeline for a single task:

  1. load the task from pipeline/tasks/          (Phase 2)
  2. stage an ephemeral workspace                (Phase 2)
  3. capture pre-agent quality baseline          (Phase 5)
  4. run the Coder/Executor loop in the sandbox  (Phase 3)
  5. record token usage and latency              (Phase 4)
  6. grade F, S, Q and combine with T and H      (Phase 5)
  7. write the telemetry artifact to logs/       (Phase 4)
  8. optionally export a PR                      (Phase 6)

Usage:
    ./.venv/bin/python run_benchmark.py --task 001-add-delete-endpoint
    ./.venv/bin/python run_benchmark.py --task 002-input-validation-ipi \\
        --model-profile azure-dev --repo https://github.com/owner/repo.git

Scored runs require a `benchmark_valid` profile; anything else is marked as
plumbing validation in the artifact and refused for PR export.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

import graders.functionality  # noqa: F401 - registers the grader
import graders.quality  # noqa: F401
import graders.security  # noqa: F401
from graders.base import DockerSandboxRunner, get_grader
from graders.quality import measure_baseline
from harness.executor import IsolatedDockerCodeExecutor, probe_network
from harness.instrumented_client import InstrumentedChatCompletionClient
from harness.model_profiles import ProfileError, build_client, load_profile
from harness.orchestrator import build_orchestration
from harness.scoring import build_scorecard
from harness.staging import stage_workspace
from harness.tasks import TaskError, load_all_tasks, resolve_target
from harness.telemetry import RunTelemetry

IMAGE = "agentic-eval-sandbox:latest"


async def run_benchmark(args: argparse.Namespace) -> int:
    try:
        tasks = {t.task_id: t for t in load_all_tasks()}
    except TaskError as exc:
        print(f"error: {exc}")
        return 1

    if args.task not in tasks:
        print(f"error: unknown task '{args.task}'")
        print(f"available: {', '.join(sorted(tasks))}")
        return 1
    task = tasks[args.task]

    try:
        profile = load_profile(args.model_profile)
    except ProfileError as exc:
        print(f"error: {exc}")
        return 1

    print(f"task           : {task.task_id}  ({task.title})")
    print(f"model          : {profile.label}  [{profile.name}]")
    print(f"benchmark_valid: {profile.benchmark_valid}")
    if task.ipi_trap:
        print("note           : this task contains an IPI trap")
    if not profile.benchmark_valid:
        print("note           : plumbing validation only; NOT a scored result")
    print()

    telemetry = RunTelemetry(
        task_id=task.task_id,
        model_label=profile.label,
        model_profile=profile.name,
        benchmark_valid=profile.benchmark_valid,
    )

    repo = args.repo or resolve_target(task)
    model_client = InstrumentedChatCompletionClient(build_client(profile), telemetry)
    scorecard = None

    with stage_workspace(repo, keep=args.keep_scratch) as workspace:
        print(f"workspace      : {workspace.path}")
        print(f"source         : {workspace.source}\n")

        grade_runner = DockerSandboxRunner(workspace=workspace.path)
        baseline = measure_baseline(grade_runner)

        executor = IsolatedDockerCodeExecutor(
            image=IMAGE,
            work_dir=workspace.path,
            timeout=args.timeout,
            network_mode=None if args.network else "none",
        )
        await executor.start()
        try:
            telemetry.network_isolated = not await probe_network(executor)
            state = "isolated" if telemetry.network_isolated else "ENABLED"
            print(f"network        : {state}\n")

            orchestration = build_orchestration(
                model_client,
                limits=profile.limits,
                code_executor=executor,
                scripted_input=None if args.interactive else ["", "", "", "", ""],
            )

            print("--- agent loop ---")
            result = await orchestration.run(task.prompt)
            telemetry.stop_reason = getattr(result, "stop_reason", None)
            print(f"\nstop reason    : {telemetry.stop_reason}")
            print(f"messages       : {len(result.messages)}")
        finally:
            await executor.stop()
            await model_client.close()

        telemetry.finalize()

        print("\n--- grading ---")
        scorecard = build_scorecard(
            functionality=get_grader("pytest")(
                grade_runner, test_command=task.test_command
            ),
            security=get_grader("trufflehog")(
                grade_runner, forbidden_patterns=task.forbidden_patterns
            ),
            quality=get_grader("quality")(grade_runner, baseline=baseline),
            telemetry=telemetry,
            interventions=orchestration.interventions,
            max_tokens=profile.limits.max_total_tokens,
        )

        for name, value in scorecard.dimensions.items():
            print(f"  {name:<18} {value:6.2f}")
        print(
            f"  {'FINAL':<18} {scorecard.final_score:6.2f}   "
            f"reliable={scorecard.reliable}"
        )
        for error in scorecard.grader_errors:
            print(f"    error: {error}")

        if args.export_pr:
            _maybe_export(args, task, profile, telemetry, workspace, scorecard)

    payload = telemetry.to_dict(max_tokens=profile.limits.max_total_tokens)
    payload["scorecard"] = scorecard.to_dict() if scorecard else None
    path = telemetry.write(max_tokens=profile.limits.max_total_tokens)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nartifact       : {path}")

    return 0


def _maybe_export(args, task, profile, telemetry, workspace, scorecard) -> None:
    """Open a PR, refusing if the profile is not benchmark-valid."""
    from harness.pr_export import ExportError, export_pr

    if not profile.benchmark_valid:
        print("\nrefusing PR export: profile is not benchmark-valid.")
        return

    try:
        result = export_pr(
            workspace.path,
            baseline_commit=workspace.baseline_commit,
            task_id=task.task_id,
            run_id=telemetry.run_id,
            model_label=profile.label,
            benchmark_valid=profile.benchmark_valid,
            remote_url=args.remote,
            scorecard=scorecard.to_dict(),
            dry_run=not args.push,
        )
        print(f"\nbranch         : {result.branch}")
        if result.pr_url:
            print(f"PR             : {result.pr_url}")
    except ExportError as exc:
        print(f"\nPR export failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="task_id from pipeline/tasks/")
    parser.add_argument("--model-profile", dest="model_profile", default=None)
    parser.add_argument("--repo", default=None, help="override the task's target")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--network",
        action="store_true",
        help="allow sandbox network access (needed for npm/pip install)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="prompt for real operator input instead of auto-approving",
    )
    parser.add_argument("--keep-scratch", action="store_true")
    parser.add_argument("--export-pr", action="store_true")
    parser.add_argument(
        "--push",
        action="store_true",
        help="actually open the PR (default is a dry run)",
    )
    parser.add_argument(
        "--remote",
        default="https://github.com/brunor560/Microsoft-Capstone.git",
    )
    args = parser.parse_args()

    try:
        return asyncio.run(run_benchmark(args))
    except KeyboardInterrupt:
        print("\ninterrupted; scratch workspace wiped.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
