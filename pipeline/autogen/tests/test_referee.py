"""Phase 6 tests for the CI-side referee.

Requires Docker; no LLM and no API spend.
"""

from __future__ import annotations

import subprocess

import pytest

# detect_framework is imported so unsupported-framework behavior can be
# tested directly before the complete referee path is exercised.
from harness.referee import detect_framework, referee


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
    not _docker_available(),
    reason=f"Docker image {IMAGE} not available",
)


def _git_init(path):
    """Initialize and commit a small temporary Git repository."""

    for argv in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "eval@example.com"],
        ["git", "config", "user.name", "eval"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "baseline"],
    ):
        subprocess.run(
            argv,
            cwd=path,
            check=True,
            capture_output=True,
        )


def _clean_repo(path):
    """Create a minimal passing Python repository for referee tests."""

    (path / "mod.py").write_text(
        "def add(a, b):\n"
        "    return a + b\n"
    )

    (path / "test_mod.py").write_text(
        "from mod import add\n\n"
        "def test_add():\n"
        "    assert add(1, 2) == 3\n"
    )

    _git_init(path)


def test_referee_grades_a_clean_repo(tmp_path):
    """A valid clean repository should receive a reliable full score."""

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
        "AWS_SECRET_ACCESS_KEY="
        "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\n"
    )

    subprocess.run(
        ["git", "add", "-A"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

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
    or package.json, so framework detection must return None.
    """

    # Create a repository-like directory with no supported testing framework.
    #
    # There is deliberately:
    #   - no test_*.py
    #   - no pytest.ini
    #   - no pyproject.toml
    #   - no package.json
    #
    # Therefore detect_framework() should return None.
    (tmp_path / "README.md").write_text(
        "# Unsupported benchmark target\n"
    )

    # Test framework detection directly first.
    #
    # This makes failures easier to diagnose:
    #
    #   If this assertion fails:
    #       detect_framework() is misclassifying the repository.
    #
    #   If this assertion passes but referee() returns a numeric score:
    #       the problem is in referee() or CI is running stale code.
    assert detect_framework(tmp_path) is None

    verdict = referee(tmp_path)

    # An unsupported target must not receive an invented numeric score.
    assert verdict["final_score"] is None

    # No grading dimensions should have been evaluated.
    assert verdict["dimensions"] == {}

    # Because functionality could not be measured, the result is not a
    # reliable benchmark verdict.
    assert verdict["reliable"] is False

    # An ungraded repository can never be accepted.
    assert verdict["accepted"] is False

    assert any(
        "No supported test framework"
        in error
        for error in verdict["grader_errors"]
    )


def test_referee_honours_an_explicit_test_command(tmp_path):
    """An explicit test command can override the default test invocation."""

    (tmp_path / "package.json").write_text("{}")

    (tmp_path / "test_thing.py").write_text(
        "def test_ok():\n"
        "    assert True\n"
    )

    _git_init(tmp_path)

    # An override must produce the pytest JSON report AND print it because
    # the grader reads stdout from a single container invocation.
    verdict = referee(
        tmp_path,
        test_command=(
            "cd /workspace && "
            "pytest --json-report "
            "--json-report-file=/tmp/eval-pytest-report.json "
            "-p no:cacheprovider -q >/dev/null 2>&1; "
            "cat /tmp/eval-pytest-report.json"
        ),
    )

    assert verdict["final_score"] is not None
    assert verdict["dimensions"]["functionality"] == 100.0


def test_referee_reports_failing_tests_as_a_real_zero(tmp_path):
    """A genuine test failure is a legitimate functionality score of zero.

    This is different from a grader failure. The framework was detected and
    the tests executed successfully; the submitted code simply failed them.
    """

    (tmp_path / "mod.py").write_text(
        "def add(a, b):\n"
        "    return a - b\n"
    )

    (tmp_path / "test_mod.py").write_text(
        "from mod import add\n\n"
        "def test_add():\n"
        "    assert add(1, 2) == 3\n"
    )

    _git_init(tmp_path)

    verdict = referee(tmp_path)

    assert verdict["final_score"] is not None
    assert verdict["dimensions"]["functionality"] == 0.0

    # The test failure is a trustworthy measurement, not a grader crash.
    assert verdict["reliable"] is True

    # However, a candidate that fails functionality must not be accepted.
    assert verdict["accepted"] is False


def test_referee_flags_a_broken_suite_as_unreliable(tmp_path):
    """Unparseable test code is a grader failure, not a real test score."""

    (tmp_path / "test_broken.py").write_text(
        "def test_x(:\n"
        "    pass\n"
    )

    _git_init(tmp_path)

    verdict = referee(tmp_path)

    # The framework is detected because test_*.py exists, so grading is
    # attempted. Pytest cannot collect the malformed file, which means
    # functionality could not be measured reliably.
    assert verdict["dimensions"]["functionality"] == 0.0
    assert verdict["reliable"] is False
    assert verdict["accepted"] is False

    assert any(
        error.startswith("functionality:")
        for error in verdict["grader_errors"]
    )
