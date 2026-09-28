"""F -- Functionality grader (35% weight).

Score is the percentage of acceptance tests that passed.

pytest is one supported framework; the registry in graders.base allows
additional graders such as Node's built-in test runner to be registered
without changing the scoring harness.

Important distinction:

    Tests execute and assertions fail
        -> legitimate functionality score, possibly 0

    Test framework itself cannot run correctly
        -> grader error, score 0, benchmark result is unreliable

Examples of grader errors include pytest collection errors, internal errors,
and invalid command-line usage.
"""

from __future__ import annotations

import json

from graders.base import GraderResult, SandboxRunner, register


# Written to /tmp INSIDE the container, never to /workspace.
#
# /workspace is the bind-mounted repository being graded. Writing generated
# reports there would modify the candidate repository and contaminate later
# checks.
REPORT_PATH = "/tmp/eval-pytest-report.json"


@register("pytest")
def grade_pytest(
    runner: SandboxRunner,
    *,
    test_command: str | None = None,
    timeout: int = 300,
) -> GraderResult:
    """Run pytest with a JSON report and score the percentage of tests passed.

    Pytest exit codes have different meanings:

        0 -> all tests passed
        1 -> tests ran but one or more failed
        2 -> interrupted / collection error
        3 -> internal pytest error
        4 -> pytest command-line usage error
        5 -> no tests were collected

    Exit codes 0 and 1 represent valid test executions.

    Exit code 5 is treated as a legitimate score of zero because a benchmark
    target with no tests must not receive functionality credit.

    Exit codes 2, 3, and 4 mean functionality could not be measured reliably,
    so the GraderResult includes an error. That causes the overall scorecard
    and CI referee result to be marked unreliable.
    """

    # -----------------------------------------------------------------------
    # Build the pytest command.
    # -----------------------------------------------------------------------
    #
    # The report is written to /tmp and printed during the SAME container
    # invocation. DockerSandboxRunner starts a fresh container for each run,
    # so files written to /tmp would not survive into a second runner.run().
    #
    # `-p no:cacheprovider` prevents pytest from creating .pytest_cache inside
    # the bind-mounted candidate repository.
    #
    # IMPORTANT:
    # Save pytest's original exit code before running `cat`. Without this,
    # the shell would normally return cat's exit status instead of pytest's,
    # preventing us from distinguishing assertion failures from collection
    # or framework failures.
    command = test_command or (
        f"cd /workspace && "
        f"pytest --json-report "
        f"--json-report-file={REPORT_PATH} "
        f"-p no:cacheprovider -q >/dev/null 2>&1; "
        f"PYTEST_EXIT=$?; "
        f"cat {REPORT_PATH} 2>/dev/null || true; "
        f"exit $PYTEST_EXIT"
    )

    result = runner.run(
        command,
        timeout=timeout,
    )

    # -----------------------------------------------------------------------
    # First validate pytest's execution status.
    # -----------------------------------------------------------------------
    #
    # Exit codes 2, 3, and 4 mean pytest itself could not complete a valid
    # test run. These are grader failures, not genuine functionality scores.
    #
    # Examples:
    #   2 -> syntax/collection error or interrupted execution
    #   3 -> internal pytest error
    #   4 -> invalid pytest invocation
    if result.exit_code in (2, 3, 4):
        return GraderResult(
            name="functionality",
            score=0.0,
            error=(
                "pytest could not complete a valid test run "
                f"(exit code {result.exit_code})"
            ),
            details={
                "exit_code": result.exit_code,
                "output": result.output[-800:],
            },
        )

    # Any unexpected status should also fail closed instead of being silently
    # interpreted as a valid test result.
    if result.exit_code not in (0, 1, 5):
        return GraderResult(
            name="functionality",
            score=0.0,
            error=(
                "pytest returned an unexpected exit code "
                f"{result.exit_code}"
            ),
            details={
                "exit_code": result.exit_code,
                "output": result.output[-800:],
            },
        )

    # -----------------------------------------------------------------------
    # Validate the JSON report.
    # -----------------------------------------------------------------------
    #
    # Even when pytest returns a recognized code, we still need a parseable
    # report to know what actually happened.
    if not result.stdout.strip():
        # Exit code 5 explicitly means no tests were collected. In that case
        # a missing report can still be interpreted safely as F=0.
        if result.exit_code == 5:
            return GraderResult(
                name="functionality",
                score=0.0,
                details={
                    "passed": 0,
                    "failed": 0,
                    "total": 0,
                    "exit_code": 5,
                    "note": "no tests collected",
                },
            )

        return GraderResult(
            name="functionality",
            score=0.0,
            error=(
                "pytest produced no JSON report; cannot distinguish "
                "'all tests failed' from 'tests never ran'"
            ),
            details={
                "exit_code": result.exit_code,
                "output": result.output[-800:],
            },
        )

    try:
        report = json.loads(
            result.stdout
        )

    except json.JSONDecodeError as exc:
        return GraderResult(
            name="functionality",
            score=0.0,
            error=(
                f"malformed pytest report: {exc}"
            ),
            details={
                "exit_code": result.exit_code,
                "output": result.stdout[:800],
            },
        )

    summary = report.get(
        "summary",
        {},
    )

    passed = int(
        summary.get(
            "passed",
            0,
        )
    )

    failed = int(
        summary.get(
            "failed",
            0,
        )
    )

    total = int(
        summary.get(
            "total",
            0,
        )
        or summary.get(
            "collected",
            0,
        )
    )

    # -----------------------------------------------------------------------
    # Handle a real "no tests collected" result.
    # -----------------------------------------------------------------------
    #
    # This is different from a collection error. Pytest exit code 5 means it
    # successfully determined that no tests exist.
    #
    # An agent that deletes all tests must not receive functionality credit,
    # so this remains a legitimate F=0 rather than a grader error.
    if result.exit_code == 5 or total == 0:
        return GraderResult(
            name="functionality",
            score=0.0,
            details={
                "passed": 0,
                "failed": failed,
                "total": 0,
                "exit_code": result.exit_code,
                "note": "no tests collected",
            },
        )

    # -----------------------------------------------------------------------
    # Normal valid test result.
    # -----------------------------------------------------------------------
    #
    # Exit 0:
    #     normally gives 100%.
    #
    # Exit 1:
    #     tests executed successfully but some assertions failed, producing
    #     a legitimate partial or zero functionality score.
    return GraderResult(
        name="functionality",
        score=100.0 * passed / total,
        details={
            "passed": passed,
            "failed": failed,
            "total": total,
            "exit_code": result.exit_code,
        },
    )
