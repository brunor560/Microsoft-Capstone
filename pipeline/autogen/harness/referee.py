"""CI-side referee: independently re-grade a checked-out workspace.

The host computes F, S and Q locally, but a self-reported score is not
evidence. This entry point re-runs the same graders in the same pinned
container so the numbers can be verified by a party that does not trust the
machine which produced them.

Supported functionality graders:

  * Python projects -> pytest
  * Node projects   -> Node's built-in test runner / TAP

Differences from the host-side scoring path:

  * T and H are NOT recomputed. Token usage and operator interventions are
    properties of the original agent run and cannot be reconstructed from
    the resulting repository alone.
  * No language model is invoked, so CI-side verification has no model cost.

Usage:
    python -m harness.referee \
        --workspace /path/to/repo \
        --output referee.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Import grader modules so their @register decorators execute before
# get_grader() is called.
import graders.functionality  # noqa: F401
import graders.node  # noqa: F401
import graders.quality  # noqa: F401
import graders.security  # noqa: F401

from graders.base import DockerSandboxRunner, get_grader
from harness.scoring import WEIGHTS


def detect_framework(workspace: Path) -> str | None:
    """Detect which functionality grader should evaluate the workspace.

    The previous implementation correctly recognized package.json as a
    Node project, but deliberately refused to grade it because there was
    no Node grader.

    Now that the `node-test` grader exists, Node repositories can be graded
    directly instead of incorrectly falling back to pytest.
    """

    # Python test discovery.
    if list(workspace.glob("test_*.py")) or list(
        workspace.glob("**/test_*.py")
    ):
        return "pytest"

    if (
        (workspace / "pytest.ini").exists()
        or (workspace / "pyproject.toml").exists()
    ):
        return "pytest"

    # Current baseline application uses package.json and Node's native
    # test runner.
    if (workspace / "package.json").exists():
        return "node-test"

    return None


def referee(
    workspace: Path,
    *,
    test_command: str | None = None,
) -> dict:
    """Re-grade `workspace` and return an independent CI verdict."""

    framework = detect_framework(workspace)

    # Refuse to guess when the repository type cannot be identified.
    #
    # Using the wrong grader would be worse than refusing to grade because
    # it could make a real failure look like a trustworthy score.
    if framework is None:
        return {
            "verified_by": "ci-referee",
            "dimensions": {},
            "final_score": None,
            "scope": "not graded",
            "reliable": False,
            "accepted": False,
            "grader_errors": [
                "No supported test framework could be detected."
            ],
            "evidence": {},
        }

    runner = DockerSandboxRunner(
        workspace=workspace
    )

    # Select the correct functionality grader based on the target language.
    #
    # Python:
    #     pytest JSON report
    #
    # Node:
    #     TAP output from Node's native test runner
    functionality = get_grader(framework)(
        runner,
        test_command=test_command,
    )

    security = get_grader("trufflehog")(
        runner
    )

    # No pre-agent quality baseline is available inside the referee.
    #
    # CI therefore evaluates only the absolute quality checks it can observe
    # from the submitted repository rather than inventing a comparison.
    quality = get_grader("quality")(
        runner,
        baseline=None,
    )

    results = {
        "functionality": functionality,
        "security": security,
        "quality": quality,
    }

    # A grader error means the result could not be reliably measured.
    #
    # This is different from a legitimate score of zero. For example:
    #
    #   test assertions fail -> valid functionality score of 0
    #   Node executable missing -> grader error / unreliable
    errors = [
        f"{name}: {result.error}"
        for name, result in results.items()
        if result.failed
    ]

    # CI can independently verify only F, S and Q.
    #
    # T (token efficiency) and H (human collaboration) occurred during
    # the original model run and cannot be reconstructed from the PR.
    verifiable = {
        key: WEIGHTS[key]
        for key in results
    }

    total_weight = sum(
        verifiable.values()
    )

    final = (
        sum(
            verifiable[name] * result.score
            for name, result in results.items()
        )
        / total_weight
    )

    # Passing the referee should mean more than "the graders did not crash."
    #
    # A repository is accepted only when:
    #
    #   - every grader executed reliably
    #   - functionality is 100
    #   - security is 100
    #   - quality is 100
    #
    # This prevents a submission with failing tests from producing a green
    # CI result simply because the grader itself executed successfully.
    accepted = (
        not errors
        and functionality.score == 100.0
        and security.score == 100.0
        and quality.score == 100.0
    )

    return {
        "verified_by": "ci-referee",
        "dimensions": {
            name: round(result.score, 2)
            for name, result in results.items()
        },
        "final_score": round(final, 2),

        "scope": (
            "F, S and Q only. Token efficiency (T) and collaboration (H) "
            "are properties of the original agent run and cannot be "
            "reconstructed by CI."
        ),

        "renormalised_over": verifiable,

        # Reliable means the graders successfully produced trustworthy data.
        "reliable": not errors,

        # Accepted means the candidate actually passed the required checks.
        "accepted": accepted,

        "grader_errors": errors,

        "evidence": {
            name: result.to_dict()
            for name, result in results.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--workspace",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("referee.json"),
    )

    parser.add_argument(
        "--test-command",
        default=None,
        help=(
            "Optional explicit test command. "
            "Normally the referee detects the framework automatically."
        ),
    )

    args = parser.parse_args()

    if not args.workspace.is_dir():
        print(
            f"Referee: workspace not found: "
            f"{args.workspace}"
        )
        return 1

    verdict = referee(
        args.workspace,
        test_command=args.test_command,
    )

    args.output.write_text(
        json.dumps(
            verdict,
            indent=2,
        )
        + "\n"
    )

    print(
        f"--- referee verdict "
        f"({args.workspace}) ---"
    )

    for name, score in verdict["dimensions"].items():
        print(
            f"  {name:<18} "
            f"{score:6.2f}"
        )

    if verdict["final_score"] is None:
        print("  NOT GRADED")
    else:
        print(
            f"  {'FINAL (F,S,Q)':<18} "
            f"{verdict['final_score']:6.2f}"
        )

    print(
        f"  reliable: "
        f"{verdict['reliable']}"
    )

    print(
        f"  accepted: "
        f"{verdict.get('accepted', False)}"
    )

    for error in verdict["grader_errors"]:
        print(
            f"    error: {error}"
        )

    print(
        f"\nWrote {args.output}"
    )

    # IMPORTANT:
    #
    # The old code returned success whenever the graders merely completed.
    # That allowed legitimately failing submissions to produce a successful
    # CI process.
    #
    # CI is now green only when the candidate is actually accepted.
    return 0 if verdict.get("accepted", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
