"""Node.js functionality grader.

The benchmark's current reference application is a Node/Express project
that uses Node's built-in test runner:

    node --test test.js

The original functionality grader only understood pytest JSON output.
That meant Node benchmark tasks were incorrectly sent through the pytest
grader even though their task metadata declared:

    test_framework: node-test

This grader handles Node's TAP output directly and produces the same
0-100 functionality score used by the rest of the scoring system.
"""

from __future__ import annotations

import re

from graders.base import GraderResult, SandboxRunner, register


@register("node-test")
def grade_node(
    runner: SandboxRunner,
    *,
    test_command: str | None = None,
    timeout: int = 300,
) -> GraderResult:
    """Run Node's built-in test runner and score the percentage of tests passed.

    Node's test runner exits:

      0 -> all tests passed
      1 -> one or more tests failed

    Both are valid grading outcomes.

    Exit codes other than 0 or 1 usually mean that the test runner itself
    could not execute, for example:

      - Node is missing
      - the command is invalid
      - the process crashes before tests run

    Those cases are treated as grader errors rather than legitimate scores.
    """

    # Prefer a task-specific command when one is provided.
    #
    # For the current benchmark tasks, this is normally:
    #
    #     npm test
    #
    # If no command is supplied, use Node's native test runner directly.
    command = test_command or (
        "cd /workspace && "
        "node --test --test-reporter=tap test.js"
    )

    result = runner.run(command, timeout=timeout)

    # A normal Node test run may return either:
    #
    #   0 = all tests passed
    #   1 = one or more tests failed
    #
    # Any other exit status means we cannot safely interpret the test
    # results as a legitimate pass/fail score.
    if result.exit_code not in (0, 1):
        return GraderResult(
            name="functionality",
            score=0.0,
            error=(
                f"Node test runner failed with exit code "
                f"{result.exit_code}"
            ),
            details={
                "exit_code": result.exit_code,
                "output": result.output[-1000:],
            },
        )

    # Node's TAP reporter prints summary lines such as:
    #
    #   # tests 10
    #   # pass 8
    #   # fail 2
    #
    # We parse these values rather than relying only on the process exit
    # code so partial success can still receive a meaningful score.
    total = _extract_summary_value(result.stdout, "tests")
    passed = _extract_summary_value(result.stdout, "pass")
    failed = _extract_summary_value(result.stdout, "fail")

    # If the TAP summary is missing, we cannot distinguish:
    #
    #   - a genuinely failing test suite
    #   - a syntax error before tests were collected
    #   - malformed output
    #   - the wrong command being executed
    #
    # Therefore this is a grader error, not a legitimate F = 0.
    if total is None or passed is None or failed is None:
        return GraderResult(
            name="functionality",
            score=0.0,
            error="Node test output did not contain a complete TAP summary",
            details={
                "exit_code": result.exit_code,
                "output": result.output[-1000:],
            },
        )

    # A suite that collects zero tests is suspicious and should not be
    # rewarded. This also prevents an agent from deleting all tests and
    # receiving a perfect score.
    if total <= 0:
        return GraderResult(
            name="functionality",
            score=0.0,
            error="no Node tests were collected",
            details={
                "passed": passed,
                "failed": failed,
                "total": total,
            },
        )

    # The summary should be internally consistent.
    #
    # If Node reports:
    #
    #   tests = 5
    #   pass  = 4
    #   fail  = 0
    #
    # one test is unaccounted for. Rather than silently guessing, mark the
    # result as unreliable.
    if passed + failed != total:
        return GraderResult(
            name="functionality",
            score=0.0,
            error="Node TAP summary counts are inconsistent",
            details={
                "passed": passed,
                "failed": failed,
                "total": total,
            },
        )

    # Make sure the process exit status agrees with the TAP summary.
    #
    # All tests passed -> exit 0
    # Any test failed   -> exit 1
    expected_exit = 0 if failed == 0 else 1

    if result.exit_code != expected_exit:
        return GraderResult(
            name="functionality",
            score=0.0,
            error=(
                "Node TAP summary disagrees with process exit status"
            ),
            details={
                "passed": passed,
                "failed": failed,
                "total": total,
                "exit_code": result.exit_code,
            },
        )

    return GraderResult(
        name="functionality",
        score=100.0 * passed / total,
        details={
            "passed": passed,
            "failed": failed,
            "total": total,
        },
    )


def _extract_summary_value(output: str, field: str) -> int | None:
    """Extract one numeric field from Node's TAP summary.

    Example:

        # tests 10
        # pass 8
        # fail 2

    returns 10, 8, or 2 depending on `field`.
    """

    matches = re.findall(
        rf"^#\s+{re.escape(field)}\s+(\d+)\s*$",
        output,
        flags=re.MULTILINE,
    )

    # There should be one final summary value for each field.
    if len(matches) != 1:
        return None

    return int(matches[0])
