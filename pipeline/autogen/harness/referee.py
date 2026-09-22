"""CI-side referee: independently re-grade a checked-out workspace.

The host computes F, S and Q locally, but a self-reported score is not
evidence. This entry point re-runs the same graders in the same pinned
container so the numbers can be verified by a party that does not trust the
machine which produced them.

Differences from the host-side scoring path:

  * T and H are NOT recomputed. Token usage and operator interventions are
    properties of the run, not of the resulting code, so CI cannot observe
    them. They are reported as null rather than guessed at.
  * No model is invoked, so this costs nothing.

Usage:
    python -m harness.referee --workspace /path/to/repo --output referee.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import graders.functionality  # noqa: F401 - registers the grader
import graders.quality  # noqa: F401
import graders.security  # noqa: F401
from graders.base import DockerSandboxRunner, get_grader
from harness.scoring import WEIGHTS


def detect_framework(workspace: Path) -> str | None:
    """Identify the target's test framework, or None if unsupported.

    Returning None matters: pytest collects zero tests from a Node project
    and reports a legitimate-looking F = 0, which reads as "the agent's code
    fails every test" rather than "the wrong grader was used". Refusing to
    grade is the only honest outcome.
    """
    if list(workspace.glob("test_*.py")) or list(workspace.glob("**/test_*.py")):
        return "pytest"
    if (workspace / "pytest.ini").exists() or (workspace / "pyproject.toml").exists():
        return "pytest"
    if (workspace / "package.json").exists():
        # Recognised, but no Node grader is implemented yet (the sandbox is
        # python:3.11-slim and has no Node runtime).
        return "node"
    return None


def referee(workspace: Path, *, test_command: str | None = None) -> dict:
    """Re-grade `workspace` and return a verdict dict."""
    framework = detect_framework(workspace)
    if framework != "pytest" and test_command is None:
        return {
            "verified_by": "ci-referee",
            "dimensions": {},
            "final_score": None,
            "scope": "not graded",
            "reliable": False,
            "grader_errors": [
                f"no grader available for detected framework "
                f"'{framework or 'unknown'}'. Refusing to grade: running "
                f"pytest here would collect zero tests and report F=0, "
                f"which is indistinguishable from genuine test failures. "
                f"Pass --test-command to override."
            ],
            "evidence": {},
        }

    runner = DockerSandboxRunner(workspace=workspace)

    functionality = get_grader("pytest")(runner, test_command=test_command)
    security = get_grader("trufflehog")(runner)
    # No baseline is available in CI: the pre-agent tree is not checked out
    # here. Quality therefore judges only the absolute criteria it can, and
    # says so, rather than inventing a comparison.
    quality = get_grader("quality")(runner, baseline=None)

    results = {
        "functionality": functionality,
        "security": security,
        "quality": quality,
    }
    errors = [
        f"{name}: {result.error}"
        for name, result in results.items()
        if result.failed
    ]

    # Renormalise across only the dimensions CI can actually verify, so the
    # published figure is not silently deflated by absent T and H.
    verifiable = {k: WEIGHTS[k] for k in results}
    total_weight = sum(verifiable.values())
    final = (
        sum(verifiable[name] * result.score for name, result in results.items())
        / total_weight
    )

    return {
        "verified_by": "ci-referee",
        "dimensions": {name: round(r.score, 2) for name, r in results.items()},
        "final_score": round(final, 2),
        "scope": (
            "F, S and Q only. Token efficiency (T) and collaboration (H) are "
            "properties of the agent run, not of the resulting code, and "
            "cannot be observed in CI."
        ),
        "renormalised_over": verifiable,
        "reliable": not errors,
        "grader_errors": errors,
        "evidence": {name: r.to_dict() for name, r in results.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("referee.json"))
    parser.add_argument("--test-command", default=None)
    args = parser.parse_args()

    if not args.workspace.is_dir():
        print(f"Referee: workspace not found: {args.workspace}")
        return 1

    verdict = referee(args.workspace, test_command=args.test_command)
    args.output.write_text(json.dumps(verdict, indent=2) + "\n")

    print(f"--- referee verdict ({args.workspace}) ---")
    for name, score in verdict["dimensions"].items():
        print(f"  {name:<18} {score:6.2f}")
    if verdict["final_score"] is None:
        print("  NOT GRADED")
    else:
        print(f"  {'FINAL (F,S,Q)':<18} {verdict['final_score']:6.2f}")
    print(f"  reliable: {verdict['reliable']}")
    for error in verdict["grader_errors"]:
        print(f"    error: {error}")
    print(f"\nWrote {args.output}")

    # A failed grader is a CI failure: an unverifiable PR must not look green.
    return 0 if verdict["reliable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
