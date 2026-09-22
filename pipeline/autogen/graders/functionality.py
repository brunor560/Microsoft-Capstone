"""F -- Functionality grader (35% weight).

Score is the percentage of acceptance tests that passed.

pytest is the first framework implemented; the registry in graders.base lets
other runners (node --test, go test, ...) be added without touching the
scoring harness.
"""

from __future__ import annotations

import json

from graders.base import GraderResult, SandboxRunner, register

# Written to /tmp INSIDE the container, never to /workspace.
#
# /workspace is a bind mount of the host directory being graded. Writing the
# report there leaves an artifact behind on the host -- which, when grading a
# shared read-only testbed such as the repository's `app/`, silently
# contaminates a directory another team member owns. Observed in Phase 6.
REPORT_PATH = "/tmp/eval-pytest-report.json"


@register("pytest")
def grade_pytest(
    runner: SandboxRunner,
    *,
    test_command: str | None = None,
    timeout: int = 300,
) -> GraderResult:
    """Run pytest with a JSON report and score pass percentage.

    A non-zero exit code is NOT itself a failure: pytest exits 1 when tests
    fail, which is exactly the case we need to score. Only an unreadable
    report means the grader could not do its job.
    """
    # The report is written to /tmp and read back in the SAME command: each
    # runner.run() starts a fresh container, so /tmp does not persist between
    # calls. `-p no:cacheprovider` suppresses .pytest_cache/, which pytest
    # would otherwise create inside the bind-mounted host tree.
    command = test_command or (
        f"cd /workspace && pytest --json-report "
        f"--json-report-file={REPORT_PATH} -p no:cacheprovider -q >/dev/null 2>&1; "
        f"cat {REPORT_PATH}"
    )
    read = runner.run(command, timeout=timeout)
    result = read

    if not read.stdout.strip():
        return GraderResult(
            name="functionality",
            score=0.0,
            error=(
                "pytest produced no JSON report; cannot distinguish "
                "'all tests failed' from 'tests never ran'"
            ),
            details={"exit_code": result.exit_code, "output": result.output[-800:]},
        )

    try:
        report = json.loads(read.stdout)
    except json.JSONDecodeError as exc:
        return GraderResult(
            name="functionality",
            score=0.0,
            error=f"malformed pytest report: {exc}",
            details={"output": read.stdout[:800]},
        )

    summary = report.get("summary", {})
    passed = int(summary.get("passed", 0))
    total = int(summary.get("total", 0) or summary.get("collected", 0))

    if total == 0:
        # No tests collected. Scoring 0 is correct -- an agent that deletes
        # the test suite must not be rewarded -- but flag it as suspicious.
        return GraderResult(
            name="functionality",
            score=0.0,
            details={
                "passed": 0,
                "total": 0,
                "note": "no tests collected; suite may be missing or broken",
            },
        )

    return GraderResult(
        name="functionality",
        score=100.0 * passed / total,
        details={
            "passed": passed,
            "failed": int(summary.get("failed", 0)),
            "total": total,
        },
    )
