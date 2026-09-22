"""Q -- Code Quality grader (20% weight).

### Interpreting "stable"

The brief awards "25 points each for successful formatting, stable cognitive
complexity, stable duplication, and stable runtime". Three of those four are
*relative* terms with no stated reference point.

This implementation resolves the ambiguity by comparing the agent's final
tree against the **baseline commit** that Phase 2 stages before the agent
runs (`baseline: pre-agent state`). That is the only reference available
that is both per-task and per-repository, and it makes "stable" mean "the
agent did not degrade the codebase it was given".

Sub-criteria (25 points each):

  1. `formatting`  -- every Python file still parses. A tree the toolchain
     cannot read is the clearest possible formatting failure.
  2. `complexity`  -- total cognitive complexity (complexipy) has not grown
     beyond TOLERANCE versus baseline.
  3. `duplication` -- DRYness (scc ULOC / Code) has not worsened beyond
     TOLERANCE versus baseline.
  4. `runtime`     -- test-suite wall time has not grown beyond
     RUNTIME_TOLERANCE versus baseline.

A metric that IMPROVES always earns its points. Tolerance bands exist
because exact equality is unachievable: adding a feature legitimately adds
some complexity, and runtime is inherently noisy.

### Known limitations

* `complexipy` is Python-only. On a non-Python target the complexity
  sub-criterion is skipped and excluded from the denominator, rather than
  silently awarded or silently lost.
* Runtime on a single sample is noisy; RUNTIME_TOLERANCE is deliberately
  loose so normal variance does not cost points.
"""

from __future__ import annotations

import json
import re

from graders.base import GraderResult, SandboxRunner, register

# Complexity/duplication may grow by this fraction before losing points.
TOLERANCE = 0.10
# Runtime is noisy on a single sample; allow a 2x band.
RUNTIME_TOLERANCE = 1.00


def _measure_complexity(runner: SandboxRunner) -> int | None:
    """Total cognitive complexity, or None if no Python files exist."""
    probe = runner.run(
        "cd /workspace && find . -name '*.py' -not -path './.git/*' | head -1",
        timeout=60,
    )
    if not probe.stdout.strip():
        return None

    # complexipy writes its JSON report to the CWD; -j is the short form.
    #
    # CRITICAL: complexipy is a LINTER, not just a reporter -- it exits 1
    # when any function exceeds its default complexity threshold (15). An
    # `&& cat` chain therefore silently fails exactly when the code is most
    # complex, returning None and causing the complexity criterion to be
    # SKIPPED rather than FAILED. That would reward an agent for writing
    # deeply nested code. Use `;` and ignore the exit status.
    # complexipy writes complexipy.json to its CWD, so it is run from /tmp
    # with /workspace as the analysis target. Running it *in* /workspace
    # would drop an artifact into the bind-mounted host directory --
    # contaminating a shared read-only testbed such as `app/`.
    #
    # The report is removed first so a stale file from a previous
    # measurement can never be mistaken for the current one.
    result = runner.run(
        "cd /tmp && rm -f complexipy.json && "
        "complexipy /workspace -j >/dev/null 2>&1; cat /tmp/complexipy.json",
        timeout=180,
    )
    if not result.stdout.strip():
        return None
    try:
        entries = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return sum(int(e.get("complexity", 0)) for e in entries)


def _measure_dryness(runner: SandboxRunner) -> float | None:
    """ULOC / Code ratio across all languages. Higher is DRYer.

    NOTE: scc requires the path BEFORE the flags. `scc --format json PATH`
    silently returns an empty array, which would make this metric look
    identical every time and award the points for free.
    """
    result = runner.run(
        "cd /workspace && scc . --dryness --format json", timeout=180
    )
    if not result.ok or not result.stdout.strip():
        return None
    try:
        entries = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    code = sum(int(e.get("Code", 0)) for e in entries)
    uloc = sum(int(e.get("ULOC", 0)) for e in entries)
    if code == 0:
        return None
    return uloc / code


def _measure_runtime(runner: SandboxRunner, test_command: str) -> float | None:
    """Wall-clock seconds for the test suite, or None if unmeasurable.

    `-p no:cacheprovider` is appended to pytest invocations so the run does
    not create .pytest_cache/ inside the bind-mounted host tree.
    """
    if test_command.strip().startswith("pytest"):
        test_command = test_command.replace(
            "pytest", "pytest -p no:cacheprovider", 1
        )
    result = runner.run(
        f"cd /workspace && /usr/bin/time -f '%e' {test_command} 2>&1 | tail -1",
        timeout=600,
    )
    match = re.search(r"(\d+\.\d+)", result.output)
    return float(match.group(1)) if match else None


def _check_parses(runner: SandboxRunner) -> bool:
    """Every Python file must still compile.

    `-q` keeps it quiet; `-b` would write .pyc files next to the sources, so
    the cache is redirected to /tmp via PYTHONPYCACHEPREFIX to avoid leaving
    __pycache__ directories in the bind-mounted host tree.
    """
    result = runner.run(
        "cd /workspace && PYTHONPYCACHEPREFIX=/tmp/pycache "
        "python -m compileall -q . >/dev/null 2>&1 && echo PARSE_OK",
        timeout=180,
    )
    return "PARSE_OK" in result.output


def measure_baseline(
    runner: SandboxRunner, *, test_command: str = "pytest -q"
) -> dict:
    """Capture pre-agent metrics for later comparison.

    Must be called on the staged workspace BEFORE the agent modifies it.
    """
    return {
        "complexity": _measure_complexity(runner),
        "dryness": _measure_dryness(runner),
        "runtime_seconds": _measure_runtime(runner, test_command),
    }


@register("quality")
def grade_quality(
    runner: SandboxRunner,
    *,
    baseline: dict | None = None,
    test_command: str = "pytest -q",
    timeout: int = 600,
) -> GraderResult:
    """Score Q against a baseline measurement.

    `baseline` is the dict returned by `measure_baseline()` before the agent
    ran. Without it only the absolute `formatting` criterion can be judged,
    so the score is computed over that criterion alone rather than inventing
    comparisons.
    """
    criteria: dict[str, bool | None] = {"formatting": _check_parses(runner)}

    complexity = _measure_complexity(runner)
    dryness = _measure_dryness(runner)
    runtime = _measure_runtime(runner, test_command)

    measured = {
        "complexity": complexity,
        "dryness": dryness,
        "runtime_seconds": runtime,
    }

    if baseline is None:
        criteria["complexity"] = None
        criteria["duplication"] = None
        criteria["runtime"] = None
    else:
        base_complexity = baseline.get("complexity")
        if complexity is None or base_complexity is None:
            criteria["complexity"] = None
        else:
            criteria["complexity"] = complexity <= base_complexity * (1 + TOLERANCE)

        base_dryness = baseline.get("dryness")
        if dryness is None or base_dryness is None:
            criteria["duplication"] = None
        else:
            # DRYness is "higher is better", so a DROP beyond tolerance fails.
            criteria["duplication"] = dryness >= base_dryness * (1 - TOLERANCE)

        base_runtime = baseline.get("runtime_seconds")
        if runtime is None or not base_runtime:
            criteria["runtime"] = None
        else:
            criteria["runtime"] = runtime <= base_runtime * (1 + RUNTIME_TOLERANCE)

    # Skipped criteria are excluded from the denominator so their points are
    # neither given away nor silently deducted.
    judged = {k: v for k, v in criteria.items() if v is not None}
    if not judged:
        return GraderResult(
            name="quality",
            score=0.0,
            error="no quality criteria could be evaluated",
            details={"criteria": criteria, "measured": measured},
        )

    return GraderResult(
        name="quality",
        score=100.0 * sum(1 for v in judged.values() if v) / len(judged),
        details={
            "criteria": criteria,
            "measured": measured,
            "baseline": baseline,
            "judged_count": len(judged),
            "tolerance": TOLERANCE,
        },
    )
