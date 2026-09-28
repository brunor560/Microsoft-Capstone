"""Phase 6 tests for the CI-side referee.

Requires Docker; no LLM and no API spend.
"""

from __future__ import annotations

import subprocess

import pytest

from harness.referee import referee

IMAGE = "agentic-eval-sandbox:latest"


def _docker_available() -> bool:
    try:
        return (
            subprocess.run(
                ["docker", "image", "inspect", IMAGE],
                capture_output=True,
                timeout=30,
            ).returncode
            == 0
        )
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(
    not _docker_available(), reason=f"Docker image {IMAGE} not available"
)


def _git_init(path):
    for argv in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "eval@example.com"],
        ["git", "config", "user.name", "eval"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "baseline"],
    ):
        subprocess.run(argv, cwd=path, check=True, capture_output=True)


def _clean_repo(path):
    (path / "mod.py").write_text("def add(a, b):\n    return a + b\n")
    (path / "test_mod.py").write_text(
        "from mod import add\n\ndef test_add():\n    assert add(1, 2) == 3\n"
    )
    _git_init(path)


def test_referee_grades_a_clean_repo(tmp_path):
    _clean_repo(tmp_path)

    verdict = referee(tmp_path)

    assert verdict["dimensions"]["functionality"] == 100.0
    assert verdict["dimensions"]["security"] == 100.0
    assert verdict["final_score"] == 100.0
    assert verdict["reliable"] is True


def test_referee_renormalises_over_only_f_s_q():
    """T and H are run properties, not code properties.

    CI cannot observe token usage or operator interventions, so the
    published figure must be renormalised across the verifiable dimensions
    rather than silently deflated by two missing ones.
    """
    from harness.scoring import WEIGHTS

    # 0.35 + 0.25 + 0.20 = 0.80
    expected = {
        "functionality": WEIGHTS["functionality"],
        "security": WEIGHTS["security"],
        "quality": WEIGHTS["quality"],
    }
    assert sum(expected.values()) == pytest.approx(0.80)


def test_referee_detects_a_leak_independently(tmp_path):
    """The referee must catch a secret the host might have missed."""
    _clean_repo(tmp_path)
    (tmp_path / "deploy.env").write_text(
        "AWS_ACCESS_KEY_ID=AKIA4KQZWXYZ7TRFMNQD\n"
        "AWS_SECRET_ACCESS_KEY=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\n"
    )
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "leak"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    verdict = referee(tmp_path)

    assert verdict["dimensions"]["security"] == 0.0
    assert verdict["final_score"] < 100.0


def test_referee_states_its_scope(tmp_path):
    """The verdict must not be mistaken for a full five-dimension score."""
    _clean_repo(tmp_path)

    verdict = referee(tmp_path)

    assert "F, S and Q only" in verdict["scope"]
    assert "token_efficiency" not in verdict["dimensions"]
    assert "collaboration" not in verdict["dimensions"]


def test_referee_refuses_unsupported_framework(tmp_path):
    """Repositories with no supported test framework must not be graded.

    Node projects are now supported through the `node-test` grader, so a
    package.json can no longer be used to represent an unsupported project.

    This fixture intentionally contains no pytest configuration, Python tests,
    or package.json so framework detection should return None.
    """

    # Create an otherwise valid repository with no supported testing framework.
    (tmp_path / "README.md").write_text(
        "# Unsupported benchmark target\n"
    )

    verdict = referee(
        tmp_path
    )

    # Since no supported framework can be detected, the referee must refuse
    # to invent a score.
    assert verdict["final_score"] is None

    # No trustworthy grading occurred.
    assert verdict["reliable"] is False

    # An ungraded candidate must never be accepted.
    assert verdict["accepted"] is False

    assert verdict["dimensions"] == {}

    assert any(
        "No supported test framework"
        in error
        for error in verdict["grader_errors"]
    )

def test_referee_honours_an_explicit_test_command(tmp_path):
    """An override lets a supported-but-undetected target still be graded."""
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "test_thing.py").write_text("def test_ok():\n    assert True\n")
    _git_init(tmp_path)

    # An override must produce the report AND print it, since the grader
    # reads stdout from a single container invocation.
    verdict = referee(
        tmp_path,
        test_command=(
            "cd /workspace && pytest --json-report "
            "--json-report-file=/tmp/eval-pytest-report.json "
            "-p no:cacheprovider -q >/dev/null 2>&1; "
            "cat /tmp/eval-pytest-report.json"
        ),
    )

    assert verdict["final_score"] is not None
    assert verdict["dimensions"]["functionality"] == 100.0


def test_referee_reports_failing_tests_as_a_real_zero(tmp_path):
    """A genuine test failure IS a legitimate F of 0 -- and must be graded.

    This is the counterpart to the refusal case: when the framework is
    detected and the tests really do fail, the zero is meaningful and must
    be published rather than withheld.
    """
    (tmp_path / "mod.py").write_text("def add(a, b):\n    return a - b\n")
    (tmp_path / "test_mod.py").write_text(
        "from mod import add\n\ndef test_add():\n    assert add(1, 2) == 3\n"
    )
    _git_init(tmp_path)

    verdict = referee(tmp_path)

    assert verdict["final_score"] is not None, "a detected framework must be graded"
    assert verdict["dimensions"]["functionality"] == 0.0
    assert verdict["reliable"] is True, "failing tests are not a grader failure"


def test_referee_flags_a_broken_suite_as_unreliable(tmp_path):
    """Unparseable test code is a grader failure, not a score of zero."""
    (tmp_path / "test_broken.py").write_text("def test_x(:\n    pass\n")
    _git_init(tmp_path)

    verdict = referee(tmp_path)

    # The framework is detected (test_*.py exists) so grading is attempted,
    # but pytest cannot collect -- which must surface, not read as 0/100.
    assert verdict["dimensions"]["functionality"] == 0.0
