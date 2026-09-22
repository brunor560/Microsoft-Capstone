"""Phase 5 gate: end-to-end scoring harness verification.

Runs the real graders inside the sandbox against two deliberately
constructed workspaces and checks the resulting scorecards:

  1. A "clean" tree -- tests pass, no secrets, quality stable => high score.
  2. A "leaky" tree -- a committed credential                  => S = 0.

No LLM is involved: telemetry and intervention values are supplied directly,
so this gate costs nothing and is fully deterministic.

Usage:
    ./.venv/bin/python -m harness.verify_scoring
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import graders.functionality  # noqa: F401 - registers the grader
import graders.quality  # noqa: F401
import graders.security  # noqa: F401
from graders.base import DockerSandboxRunner, get_grader
from graders.quality import measure_baseline
from harness.orchestrator import InterventionLog
from harness.scoring import build_scorecard
from harness.telemetry import RunTelemetry

IMAGE = "agentic-eval-sandbox:latest"
MAX_TOKENS = 15000

GOOD_MODULE = "def add(a, b):\n    return a + b\n"
GOOD_TESTS = (
    "from mod import add\n\n"
    "def test_add():\n    assert add(1, 2) == 3\n\n"
    "def test_add_negative():\n    assert add(-1, 1) == 0\n"
)


def _git_init(path: Path) -> None:
    for argv in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "eval@example.com"],
        ["git", "config", "user.name", "eval"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "baseline"],
    ):
        subprocess.run(argv, cwd=path, check=True, capture_output=True)


def _score(workspace: Path, *, total_tokens: int, interventions: int):
    runner = DockerSandboxRunner(workspace=workspace)
    baseline = measure_baseline(runner)

    functionality = get_grader("pytest")(runner)
    security = get_grader("trufflehog")(runner)
    quality = get_grader("quality")(runner, baseline=baseline)

    telemetry = RunTelemetry(
        task_id="gate",
        model_label="none/offline",
        model_profile="offline",
        benchmark_valid=False,
    )
    telemetry.record_call(
        prompt_tokens=total_tokens, completion_tokens=0, latency_seconds=0.5
    )

    log = InterventionLog()
    for index in range(interventions):
        log.record("prompt> ", f"correction {index}")

    return build_scorecard(
        functionality=functionality,
        security=security,
        quality=quality,
        telemetry=telemetry,
        interventions=log,
        max_tokens=MAX_TOKENS,
    )


def _report(label: str, card) -> None:
    print(f"--- {label} ---")
    for name, value in card.dimensions.items():
        print(f"  {name:<18} {value:6.2f}")
    print(f"  {'FINAL':<18} {card.final_score:6.2f}   reliable={card.reliable}")
    for error in card.grader_errors:
        print(f"    error: {error}")
    print()


def main() -> int:
    if (
        subprocess.run(
            ["docker", "image", "inspect", IMAGE], capture_output=True
        ).returncode
        != 0
    ):
        print(f"PHASE 5 GATE: FAILED\n  Image '{IMAGE}' not found.")
        return 1

    failures: list[str] = []

    with tempfile.TemporaryDirectory() as raw:
        # --- case 1: a clean, passing workspace ------------------------
        good = Path(raw) / "good"
        good.mkdir()
        (good / "mod.py").write_text(GOOD_MODULE)
        (good / "test_mod.py").write_text(GOOD_TESTS)
        _git_init(good)

        good_card = _score(good, total_tokens=1500, interventions=0)
        _report("clean workspace", good_card)

        if good_card.functionality != 100.0:
            failures.append(f"F should be 100, got {good_card.functionality}")
        if good_card.security != 100.0:
            failures.append(f"S should be 100, got {good_card.security}")
        if not good_card.reliable:
            failures.append("clean run produced grader errors")
        # T = 100 * (1 - 1500/15000) = 90
        if round(good_card.token_efficiency) != 90:
            failures.append(f"T should be 90, got {good_card.token_efficiency}")
        if good_card.collaboration != 100.0:
            failures.append("H should be 100 with zero interventions")

        # --- case 2: a leaked credential -------------------------------
        leaky = Path(raw) / "leaky"
        leaky.mkdir()
        (leaky / "mod.py").write_text(GOOD_MODULE)
        (leaky / "test_mod.py").write_text(GOOD_TESTS)
        # Realistic key material: TruffleHog filters AWS's documentation key.
        (leaky / "deploy.env").write_text(
            "AWS_ACCESS_KEY_ID=AKIA4KQZWXYZ7TRFMNQD\n"
            "AWS_SECRET_ACCESS_KEY=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\n"
        )
        _git_init(leaky)

        leaky_card = _score(leaky, total_tokens=1500, interventions=2)
        _report("leaked credential", leaky_card)

        if leaky_card.security != 0.0:
            failures.append(
                f"S must be 0 when a secret is committed, got {leaky_card.security}"
            )
        if leaky_card.functionality != 100.0:
            failures.append("F should be unaffected by the leak")
        if leaky_card.collaboration != 80.0:
            failures.append(f"H should be 80, got {leaky_card.collaboration}")

        # The leak must cost exactly its weight: S contributes 25% of 100,
        # and 2 interventions cost 20 H points weighted at 10%.
        delta = good_card.final_score - leaky_card.final_score
        expected = 25.0 + 2.0
        if abs(delta - expected) > 0.5:
            failures.append(f"score delta {delta:.2f} != expected {expected:.2f}")
        else:
            print(
                f"  leak + 2 interventions cost {delta:.2f} points "
                f"(expected {expected:.2f})\n"
            )

    if failures:
        print(f"PHASE 5 GATE: FAILED ({len(failures)} problem(s))")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PHASE 5 GATE: PASSED")
    print("  Graders run in the sandbox and the weighted score is correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
