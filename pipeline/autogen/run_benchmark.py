#!/usr/bin/env python
"""Agentic IDE Evaluation Suite -- benchmark runner.

Wires together every phase of the pipeline for a single benchmark task:

  1. Load the task definition.
  2. Stage an isolated workspace.
  3. Measure the pre-agent quality baseline.
  4. Run the Coder/Executor agent loop.
  5. Record model usage and latency.
  6. Grade functionality, security and quality.
  7. Combine scores with token efficiency and collaboration.
  8. Write the telemetry artifact.
  9. Optionally export the resulting change as a PR.

Functionality grading is selected from each task's declared
`test_framework`, allowing different benchmark codebases to use different
test ecosystems instead of forcing every project through pytest.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time

# Import grader modules so their @register decorators run before get_grader().
import graders.functionality  # noqa: F401
import graders.node  # noqa: F401
import graders.quality  # noqa: F401
import graders.security  # noqa: F401

from graders.base import (
    DockerSandboxRunner,
    get_grader,
)
from graders.quality import measure_baseline
from harness.executor import (
    IsolatedDockerCodeExecutor,
    probe_network,
)
from harness.instrumented_client import (
    InstrumentedChatCompletionClient,
)
from harness.license_scan import (
    UNAVAILABLE,
    scan_workspace,
    tree_manifest,
)
from harness.model_profiles import (
    ProfileError,
    build_client,
    load_profile,
)
from harness.orchestrator import (
    build_orchestration,
)
from harness.scoring import (
    build_scorecard,
)
from harness.staging import (
    Lifecycle,
    stage_workspace,
)
from harness.tasks import (
    TaskError,
    load_all_tasks,
    resolve_target,
)
from harness.telemetry import (
    RunTelemetry,
)


IMAGE = "agentic-eval-sandbox:latest"


async def run_benchmark(
    args: argparse.Namespace,
) -> int:
    """Execute one complete benchmark task."""

    try:
        tasks = {
            task.task_id: task
            for task in load_all_tasks()
        }

    except TaskError as exc:
        print(
            f"error: {exc}"
        )
        return 1

    if args.task not in tasks:
        print(
            f"error: unknown task "
            f"'{args.task}'"
        )

        print(
            "available: "
            + ", ".join(
                sorted(tasks)
            )
        )

        return 1

    task = tasks[
        args.task
    ]

    # Every scored task must explicitly state which functionality grader
    # should be used.
    #
    # Current examples:
    #
    #     node-test
    #     pytest
    #
    # This prevents a Node project from accidentally being evaluated with
    # pytest, which was the original bug in this pipeline.
    if not task.test_framework:
        print(
            f"error: task '{task.task_id}' "
            f"does not declare acceptance.test_framework"
        )

        return 1

    try:
        functionality_grader = get_grader(
            task.test_framework
        )

    except KeyError as exc:
        print(
            f"error: task '{task.task_id}' "
            f"requests unsupported test framework "
            f"'{task.test_framework}'"
        )

        print(
            str(exc)
        )

        return 1

    try:
        profile = load_profile(
            args.model_profile
        )

    except ProfileError as exc:
        print(
            f"error: {exc}"
        )
        return 1

    print(
        f"task           : "
        f"{task.task_id}  "
        f"({task.title})"
    )

    print(
        f"model          : "
        f"{profile.label}  "
        f"[{profile.name}]"
    )

    print(
        f"test framework : "
        f"{task.test_framework}"
    )

    print(
        f"benchmark_valid: "
        f"{profile.benchmark_valid}"
    )

    if task.ipi_trap:
        print(
            "note           : "
            "this task contains an IPI trap"
        )

    if not profile.benchmark_valid:
        print(
            "note           : "
            "plumbing validation only; "
            "NOT a scored result"
        )

    print()

    telemetry = RunTelemetry(
        task_id=task.task_id,
        model_label=profile.label,
        model_profile=profile.name,
        benchmark_valid=profile.benchmark_valid,
    )

    repo = (
        args.repo
        or resolve_target(task)
    )

    model_client = (
        InstrumentedChatCompletionClient(
            build_client(profile),
            telemetry,
        )
    )

    scorecard = None
    license_result = None
    lifecycle = Lifecycle()

    with stage_workspace(
        repo,
        keep=args.keep_scratch,
        lifecycle=lifecycle,
    ) as workspace:

        print(
            f"workspace      : "
            f"{workspace.path}"
        )

        print(
            f"source         : "
            f"{workspace.source}\n"
        )

        grade_runner = DockerSandboxRunner(
            workspace=workspace.path
        )

        # Quality baseline is measured before the agent changes the target.
        baseline = measure_baseline(
            grade_runner
        )

        executor = IsolatedDockerCodeExecutor(
            image=IMAGE,
            work_dir=workspace.path,
            timeout=args.timeout,
            network_mode=(
                None
                if args.network
                else "none"
            ),
        )

        # Everything hashed here is the starting code. Whatever differs after
        # the agent loop is agent-generated and gets license-scanned.
        baseline_files = tree_manifest(
            workspace.path
        )

        ready_started = time.monotonic()
        await executor.start()
        lifecycle.ready_seconds = (
            time.monotonic() - ready_started
        )

        try:
            telemetry.network_isolated = (
                not await probe_network(
                    executor
                )
            )

            state = (
                "isolated"
                if telemetry.network_isolated
                else "ENABLED"
            )

            print(
                f"network        : "
                f"{state}\n"
            )

            orchestration = build_orchestration(
                model_client,
                limits=profile.limits,
                code_executor=executor,

                # The operator is asked only after two failed turns or
                # before a dangerous command (SRS Spec 2.4). A headless run
                # has no operator, so such a request times out and is
                # rejected; nothing is approved automatically.
                unattended=not args.interactive,
            )

            print(
                "--- agent loop ---"
            )

            result = await orchestration.run(
                task.prompt
            )

            telemetry.stop_reason = getattr(
                result,
                "stop_reason",
                None,
            )

            print(
                f"\nstop reason    : "
                f"{telemetry.stop_reason}"
            )

            print(
                f"messages       : "
                f"{len(result.messages)}"
            )

            log = orchestration.interventions
            telemetry.command_timeouts = executor.command_timeouts
            telemetry.approval_wait_seconds = log.approval_wait_seconds
            telemetry.aborted = log.aborted

            if log.aborted:
                print(
                    "status         : aborted "
                    "(approval request unanswered)"
                )

        finally:
            removal_started = time.monotonic()
            await executor.stop()
            lifecycle.removal_seconds = (
                time.monotonic() - removal_started
            )
            await model_client.close()

        telemetry.finalize()

        print(
            "\n--- grading ---"
        )

        # IMPORTANT CHANGE:
        #
        # Previously every task was hard-coded to:
        #
        #     get_grader("pytest")
        #
        # even when the task metadata explicitly declared `node-test`.
        #
        # The benchmark now uses the grader requested by the task itself.
        functionality = functionality_grader(
            grade_runner,
            test_command=task.test_command,
        )

        security = get_grader(
            "trufflehog"
        )(
            grade_runner,
            forbidden_patterns=task.forbidden_patterns,
        )

        quality = get_grader(
            "quality"
        )(
            grade_runner,
            baseline=baseline,
        )

        scorecard = build_scorecard(
            functionality=functionality,
            security=security,
            quality=quality,
            telemetry=telemetry,
            interventions=orchestration.interventions,
            max_tokens=profile.limits.max_total_tokens,
        )

        for name, value in scorecard.dimensions.items():
            print(
                f"  {name:<18} "
                f"{value:6.2f}"
            )

        print(
            f"  {'FINAL':<18} "
            f"{scorecard.final_score:6.2f}   "
            f"reliable={scorecard.reliable}"
        )

        # License scan of agent-generated code (SRS Spec 4.3). A scan that
        # cannot complete is a grader error, exactly like a failed secret
        # scan, so the scorecard is not reported as reliable.
        license_result = scan_workspace(
            workspace.path,
            baseline=baseline_files,
        )

        if license_result.status == UNAVAILABLE:
            scorecard.grader_errors.append(
                f"license: {UNAVAILABLE}: {license_result.error}"
            )

        print(
            f"  {'license scan':<18} "
            f"{license_result.status}"
        )

        for match in license_result.matches:
            print(
                f"    {match['license']}: {match['path']}"
            )

        for error in scorecard.grader_errors:
            print(
                f"    error: {error}"
            )

        if args.export_pr:
            _maybe_export(
                args,
                task,
                profile,
                telemetry,
                workspace,
                scorecard,
                license_result,
            )

    payload = telemetry.to_dict(
        max_tokens=(
            profile.limits.max_total_tokens
        )
    )

    payload["scorecard"] = (
        scorecard.to_dict()
        if scorecard
        else None
    )

    # Written after the workspace is wiped, so the cleanup outcome is final.
    payload["lifecycle"] = lifecycle.to_dict()

    payload["provenance"] = (
        license_result.to_dict()
        if license_result
        else {"license_scan": UNAVAILABLE}
    )

    path = telemetry.write(
        max_tokens=(
            profile.limits.max_total_tokens
        )
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        )
        + "\n"
    )

    print(
        f"\nartifact       : "
        f"{path}"
    )

    return 0


def _maybe_export(
    args,
    task,
    profile,
    telemetry,
    workspace,
    scorecard,
    license_result,
) -> None:
    """Open a PR only for benchmark-valid runs with a clean license scan."""

    from harness.pr_export import (
        ExportError,
        export_pr,
    )

    if not profile.benchmark_valid:
        print(
            "\nrefusing PR export: "
            "profile is not benchmark-valid."
        )

        return

    # SRS clause 4.3.3: a flagged run is never published, and neither is one
    # whose scan could not run (fail closed).
    if not license_result.publishable:
        print(
            "\nrefusing PR export: "
            f"license scan is {license_result.status}."
        )

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

        print(
            f"\nbranch         : "
            f"{result.branch}"
        )

        if result.pr_url:
            print(
                f"PR             : "
                f"{result.pr_url}"
            )

    except ExportError as exc:
        print(
            f"\nPR export failed: "
            f"{exc}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--task",
        required=True,
        help="task_id from pipeline/tasks/",
    )

    parser.add_argument(
        "--model-profile",
        dest="model_profile",
        default=None,
    )

    parser.add_argument(
        "--repo",
        default=None,
        help="override the task's target",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help=(
            "seconds before the sandbox watchdog stops a command "
            "(SRS clause 1.3.4)"
        ),
    )

    parser.add_argument(
        "--network",
        action="store_true",
        help=(
            "allow sandbox network access "
            "(development only)"
        ),
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help=(
            "prompt for real operator input "
            "instead of auto-approving"
        ),
    )

    parser.add_argument(
        "--keep-scratch",
        action="store_true",
    )

    parser.add_argument(
        "--export-pr",
        action="store_true",
    )

    parser.add_argument(
        "--push",
        action="store_true",
        help=(
            "actually open the PR "
            "(default is a dry run)"
        ),
    )

    parser.add_argument(
        "--remote",
        default=(
            "https://github.com/"
            "brunor560/"
            "Microsoft-Capstone.git"
        ),
    )

    args = parser.parse_args()

    try:
        return asyncio.run(
            run_benchmark(args)
        )

    except KeyboardInterrupt:
        print(
            "\ninterrupted; "
            "scratch workspace wiped."
        )

        return 130


if __name__ == "__main__":
    sys.exit(
        main()
    )
