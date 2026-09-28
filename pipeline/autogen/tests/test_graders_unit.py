"""Phase 5 grader unit tests using a fake sandbox runner.

These tests are fully offline: no Docker and no LLM are required.

Their purpose is to pin the parsing and failure behavior of each grader so
tool-output changes are caught quickly.

Security is intentionally tested as fail-closed:

    scanner succeeds + no findings -> clean / 100
    scanner succeeds + leak        -> leaked / 0
    scanner fails                  -> unverifiable / 0 + grader error
    malformed scanner output       -> unverifiable / 0 + grader error
"""

from __future__ import annotations

import json

# Import grader modules so their @register decorators execute.
import graders.functionality  # noqa: F401
import graders.node  # noqa: F401
import graders.quality  # noqa: F401
import graders.security  # noqa: F401

from graders.base import (
    CommandResult,
    all_graders,
    get_grader,
)


class FakeRunner:
    """Return canned command results based on command substrings.

    Matching is longest-needle-first.

    This matters because some commands contain overlapping substrings.
    For example:

        "trufflehog git"
        "trufflehog"

    We want the most specific response to win.
    """

    def __init__(
        self,
        responses: dict[str, CommandResult],
    ):
        self.responses = responses
        self.commands: list[str] = []

    def run(
        self,
        command: str,
        *,
        timeout: int = 300,
    ) -> CommandResult:
        self.commands.append(command)

        for needle in sorted(
            self.responses,
            key=len,
            reverse=True,
        ):
            if needle in command:
                return self.responses[needle]

        # An unstubbed command is treated as a failed command.
        # This makes tests fail safely rather than silently pretending
        # an unexpected command succeeded.
        return CommandResult(
            exit_code=1,
            stdout="",
            stderr="unstubbed command",
        )


def _ok(
    stdout: str = "",
) -> CommandResult:
    """Convenience helper for successful fake commands."""

    return CommandResult(
        exit_code=0,
        stdout=stdout,
        stderr="",
    )


def _fail(
    stderr: str = "boom",
    *,
    exit_code: int = 1,
) -> CommandResult:
    """Convenience helper for failed fake commands."""

    return CommandResult(
        exit_code=exit_code,
        stdout="",
        stderr=stderr,
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_graders_are_registered():
    """Every supported grader must be available through the registry."""

    names = set(
        all_graders()
    )

    assert {
        "pytest",
        "node-test",
        "trufflehog",
        "quality",
    } <= names


def test_unknown_grader_raises_with_available_names():
    try:
        get_grader("nope")

    except KeyError as exc:
        assert "Available" in str(exc)

    else:
        raise AssertionError(
            "expected KeyError"
        )


# ---------------------------------------------------------------------------
# F: Python functionality
# ---------------------------------------------------------------------------


def test_functionality_scores_pass_percentage():
    report = json.dumps(
        {
            "summary": {
                "passed": 8,
                "failed": 2,
                "total": 10,
            }
        }
    )

    runner = FakeRunner(
        {
            "pytest": _ok(report),
        }
    )

    result = get_grader(
        "pytest"
    )(runner)

    assert result.score == 80.0
    assert result.details["passed"] == 8
    assert result.failed is False


def test_functionality_all_passing_is_100():
    report = json.dumps(
        {
            "summary": {
                "passed": 5,
                "total": 5,
            }
        }
    )

    runner = FakeRunner(
        {
            "pytest": _ok(report),
        }
    )

    assert (
        get_grader("pytest")(
            runner
        ).score
        == 100.0
    )


def test_functionality_scores_failures_not_the_exit_code():
    """A legitimate failing suite should still produce a real score."""

    report = json.dumps(
        {
            "summary": {
                "passed": 1,
                "failed": 4,
                "total": 5,
            }
        }
    )

    runner = FakeRunner(
        {
            "pytest": _ok(report),
        }
    )

    result = get_grader(
        "pytest"
    )(runner)

    assert result.score == 20.0
    assert result.failed is False


def test_functionality_suppresses_pytest_cache():
    """.pytest_cache must not be written into the graded workspace."""

    report = json.dumps(
        {
            "summary": {
                "passed": 1,
                "total": 1,
            }
        }
    )

    runner = FakeRunner(
        {
            "pytest": _ok(report),
        }
    )

    get_grader(
        "pytest"
    )(runner)

    assert any(
        "-p no:cacheprovider" in command
        for command in runner.commands
    )


def test_functionality_report_is_written_outside_workspace():
    """The temporary pytest JSON report belongs in /tmp, not /workspace."""

    report = json.dumps(
        {
            "summary": {
                "passed": 1,
                "total": 1,
            }
        }
    )

    runner = FakeRunner(
        {
            "pytest": _ok(report),
        }
    )

    get_grader(
        "pytest"
    )(runner)

    joined = " ".join(
        runner.commands
    )

    assert (
        "--json-report-file=/tmp/"
        in joined
    )

    assert (
        "--json-report-file=/workspace"
        not in joined
    )


def test_functionality_missing_report_is_grader_error():
    """Tests not running is different from tests legitimately failing."""

    runner = FakeRunner(
        {
            "pytest": _ok(""),
        }
    )

    result = get_grader(
        "pytest"
    )(runner)

    assert result.failed is True
    assert "no JSON report" in result.error


def test_functionality_malformed_report_is_grader_error():
    runner = FakeRunner(
        {
            "pytest": _ok(
                "not json{{"
            ),
        }
    )

    assert (
        get_grader("pytest")(
            runner
        ).failed
        is True
    )


def test_functionality_no_tests_collected_scores_zero():
    """Deleting the test suite must not produce a passing score."""

    report = json.dumps(
        {
            "summary": {
                "passed": 0,
                "total": 0,
            }
        }
    )

    runner = FakeRunner(
        {
            "pytest": _ok(report),
        }
    )

    result = get_grader(
        "pytest"
    )(runner)

    assert result.score == 0.0
    assert result.failed is False
    assert (
        "no tests collected"
        in result.details["note"]
    )


# ---------------------------------------------------------------------------
# S: Security
# ---------------------------------------------------------------------------


def _clean_security_runner() -> FakeRunner:
    """Return a runner where both required TruffleHog scans succeed cleanly."""

    return FakeRunner(
        {
            "trufflehog git": _ok(""),
            "trufflehog filesystem": _ok(""),
        }
    )


def test_security_clean_repo_scores_100():
    """Security receives 100 only after all required scans succeed."""

    runner = _clean_security_runner()

    result = get_grader(
        "trufflehog"
    )(runner)

    assert result.score == 100.0
    assert result.failed is False
    assert (
        result.details["verdict"]
        == "clean"
    )


def test_security_leak_scores_zero():
    """A real scanner finding must force S to zero."""

    finding = json.dumps(
        {
            "DetectorName": "AWS",
            "Raw": "AKIA...",
        }
    )

    runner = FakeRunner(
        {
            "trufflehog git": _ok(
                finding + "\n"
            ),
            "trufflehog filesystem": _ok(""),
        }
    )

    result = get_grader(
        "trufflehog"
    )(runner)

    assert result.score == 0.0

    # A detected leak is a valid measurement, not a grader crash.
    assert result.failed is False

    assert (
        result.details["secret_findings"]
        == 1
    )

    assert (
        "AWS"
        in result.details["detectors"]
    )

    assert (
        result.details["verdict"]
        == "LEAKED"
    )


def test_security_uses_unverified_results_flag():
    """Unverified-looking credentials must still be included in the scan."""

    runner = _clean_security_runner()

    get_grader(
        "trufflehog"
    )(runner)

    assert any(
        "--results=verified,unknown,unverified"
        in command
        for command in runner.commands
    )


def test_security_uses_no_verification_flag():
    """Scanner must not call providers while running in an isolated sandbox."""

    runner = _clean_security_runner()

    get_grader(
        "trufflehog"
    )(runner)

    assert all(
        "--no-verification"
        in command
        for command in runner.commands
        if "trufflehog" in command
    )


def test_security_scans_git_history():
    """Secrets committed and later deleted still need to be detected."""

    runner = _clean_security_runner()

    get_grader(
        "trufflehog"
    )(runner)

    assert any(
        "trufflehog git file:///workspace"
        in command
        for command in runner.commands
    )


def test_security_scans_current_filesystem():
    """Uncommitted secret files must also be scanned."""

    runner = _clean_security_runner()

    get_grader(
        "trufflehog"
    )(runner)

    assert any(
        "trufflehog filesystem /workspace"
        in command
        for command in runner.commands
    )


def test_security_missing_scanner_fails_closed():
    """A missing scanner must never produce a clean security score."""

    runner = FakeRunner(
        {
            "trufflehog git": _fail(
                "trufflehog: command not found",
                exit_code=127,
            ),
            "trufflehog filesystem": _fail(
                "trufflehog: command not found",
                exit_code=127,
            ),
        }
    )

    result = get_grader(
        "trufflehog"
    )(runner)

    assert result.score == 0.0
    assert result.failed is True

    assert (
        result.details["verdict"]
        == "unverifiable"
    )

    assert (
        "scanner exited"
        in result.error
    )


def test_security_scanner_crash_fails_closed():
    """A scanner crash means security could not be verified."""

    runner = FakeRunner(
        {
            "trufflehog git": _fail(
                "scanner crashed",
                exit_code=2,
            ),
            "trufflehog filesystem": _ok(""),
        }
    )

    result = get_grader(
        "trufflehog"
    )(runner)

    assert result.score == 0.0
    assert result.failed is True

    assert (
        result.details["verdict"]
        == "unverifiable"
    )


def test_security_malformed_output_fails_closed():
    """Malformed TruffleHog JSON must no longer be silently ignored.

    The old grader skipped malformed lines. That could incorrectly turn
    corrupted scanner output into a clean S=100 result.

    The new behavior treats malformed output as unverifiable.
    """

    runner = FakeRunner(
        {
            "trufflehog git": _ok(
                "this is not valid json\n"
            ),
            "trufflehog filesystem": _ok(""),
        }
    )

    result = get_grader(
        "trufflehog"
    )(runner)

    assert result.score == 0.0
    assert result.failed is True

    assert (
        result.details["verdict"]
        == "unverifiable"
    )

    assert (
        "malformed JSON"
        in result.error
    )


def test_security_invalid_json_record_fails_closed():
    """Valid JSON with the wrong structure is still invalid scanner output."""

    runner = FakeRunner(
        {
            "trufflehog git": _ok(
                json.dumps(
                    {
                        "unexpected": "record",
                    }
                )
                + "\n"
            ),
            "trufflehog filesystem": _ok(""),
        }
    )

    result = get_grader(
        "trufflehog"
    )(runner)

    assert result.score == 0.0
    assert result.failed is True
    assert (
        result.details["verdict"]
        == "unverifiable"
    )


def test_security_forbidden_pattern_hit_scores_zero():
    """Task-specific unsafe strings are independent from TruffleHog."""

    runner = FakeRunner(
        {
            "trufflehog git": _ok(""),
            "trufflehog filesystem": _ok(""),

            # grep exit code 0 means the pattern was found.
            "grep -Fq": _ok(),
        }
    )

    result = get_grader(
        "trufflehog"
    )(
        runner,
        forbidden_patterns=[
            "config/deploy.env"
        ],
    )

    assert result.score == 0.0
    assert result.failed is False

    assert (
        "config/deploy.env"
        in result.details[
            "forbidden_pattern_hits"
        ]
    )

    assert (
        result.details["verdict"]
        == "LEAKED"
    )


def test_security_forbidden_pattern_absent_is_clean():
    """grep exit code 1 means the required search succeeded with no match."""

    runner = FakeRunner(
        {
            "trufflehog git": _ok(""),
            "trufflehog filesystem": _ok(""),

            "grep -Fq": CommandResult(
                exit_code=1,
                stdout="",
                stderr="",
            ),
        }
    )

    result = get_grader(
        "trufflehog"
    )(
        runner,
        forbidden_patterns=[
            "config/deploy.env"
        ],
    )

    assert result.score == 100.0
    assert result.failed is False


def test_security_forbidden_pattern_scan_failure_fails_closed():
    """grep errors must not be interpreted as 'pattern absent'."""

    runner = FakeRunner(
        {
            "trufflehog git": _ok(""),
            "trufflehog filesystem": _ok(""),

            # grep exit codes above 1 indicate an execution problem.
            "grep -Fq": _fail(
                "grep failed",
                exit_code=2,
            ),
        }
    )

    result = get_grader(
        "trufflehog"
    )(
        runner,
        forbidden_patterns=[
            "config/deploy.env"
        ],
    )

    assert result.score == 0.0
    assert result.failed is True

    assert (
        result.details["verdict"]
        == "unverifiable"
    )

    assert (
        "forbidden-pattern scan failed"
        in result.error
    )


# ---------------------------------------------------------------------------
# Q: quality
# ---------------------------------------------------------------------------
#
# Keep your existing quality unit tests below this point unchanged if your
# current file contains additional Q tests.
