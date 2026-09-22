"""Phase 6 tests for host-side PR export.

Fully offline: pushes go to a local bare repo, and `gh pr create` is never
invoked (dry_run). No network, no LLM, no API spend.
"""

from __future__ import annotations

import subprocess

import pytest

from harness.pr_export import (
    ExportError,
    _repo_slug,
    build_pr_body,
    changed_files,
    commit_agent_work,
    export_pr,
)


@pytest.fixture
def workspace(tmp_path):
    """A staged workspace with a baseline commit, as Phase 2 produces."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "mod.py").write_text("def add(a, b):\n    return a + b\n")

    for argv in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "eval@example.com"],
        ["git", "config", "user.name", "eval"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "baseline: pre-agent state"],
    ):
        subprocess.run(argv, cwd=ws, check=True, capture_output=True)

    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ws,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return ws, sha


# --- diff detection ----------------------------------------------------------


def test_detects_modified_and_added_files(workspace):
    ws, sha = workspace
    (ws / "mod.py").write_text("def add(a, b):\n    return a + b + 0\n")
    (ws / "new.py").write_text("x = 1\n")

    assert set(changed_files(ws, baseline_commit=sha)) == {"mod.py", "new.py"}


def test_detects_deleted_files(workspace):
    ws, sha = workspace
    (ws / "mod.py").unlink()
    assert changed_files(ws, baseline_commit=sha) == ["mod.py"]


def test_no_changes_yields_empty_list(workspace):
    ws, sha = workspace
    assert changed_files(ws, baseline_commit=sha) == []


# --- committing --------------------------------------------------------------


def test_commit_records_agent_work(workspace):
    ws, sha = workspace
    (ws / "feature.py").write_text("def feature():\n    return True\n")

    commit_sha, files = commit_agent_work(
        ws,
        baseline_commit=sha,
        task_id="001-add-delete-endpoint",
        run_id="abc123",
        model_label="azure/gpt-4.1-mini",
    )

    assert len(commit_sha) == 40
    assert files == ["feature.py"]

    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=ws,
        capture_output=True,
        text=True,
    ).stdout
    assert "001-add-delete-endpoint" in log
    assert "azure/gpt-4.1-mini" in log
    # Provenance must be unmistakable in the history.
    assert "Not human-reviewed" in log


def test_empty_diff_refuses_to_export(workspace):
    """An agent that changed nothing must not open a PR."""
    ws, sha = workspace
    with pytest.raises(ExportError, match="no changes"):
        commit_agent_work(
            ws, baseline_commit=sha, task_id="t", run_id="r", model_label="m"
        )


# --- PR body -----------------------------------------------------------------


def _body(**overrides) -> str:
    defaults = dict(
        task_id="t",
        run_id="r",
        model_label="m",
        benchmark_valid=True,
        scorecard=None,
        files=["a.py"],
    )
    defaults.update(overrides)
    return build_pr_body(**defaults)


def test_body_warns_when_model_is_not_benchmark_valid():
    """A dev-model PR must not be mistaken for a scored benchmark run."""
    body = _body(benchmark_valid=False, model_label="azure/gpt-4.1-mini")
    assert "non-benchmark-valid" in body
    assert "must not be used for framework comparison" in body


def test_body_includes_scorecard_table():
    body = _body(
        scorecard={
            "final_score": 81.0,
            "reliable": True,
            "weights": {"functionality": 0.35},
            "dimensions": {"functionality": 80.0},
            "weighted_contributions": {"functionality": 28.0},
        }
    )
    assert "Final score: 81.0" in body
    assert "functionality" in body


def test_body_flags_unreliable_scorecard():
    """A crashed grader must be surfaced to the human reviewer."""
    body = _body(
        scorecard={
            "final_score": 40.0,
            "reliable": False,
            "grader_errors": ["functionality: no report produced"],
            "dimensions": {},
            "weights": {},
            "weighted_contributions": {},
        }
    )
    assert "Provisional" in body
    assert "no report produced" in body


def test_body_truncates_very_long_file_lists():
    body = _body(files=[f"file{i}.py" for i in range(60)])
    assert "and 20 more" in body


def test_body_always_states_it_is_unreviewed():
    assert "human-reviewed" in _body()


# --- remote slug parsing -----------------------------------------------------


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "https://github.com/brunor560/Microsoft-Capstone.git",
            "brunor560/Microsoft-Capstone",
        ),
        (
            "https://github.com/brunor560/Microsoft-Capstone",
            "brunor560/Microsoft-Capstone",
        ),
        (
            "git@github.com:brunor560/Microsoft-Capstone.git",
            "brunor560/Microsoft-Capstone",
        ),
    ],
)
def test_repo_slug_parsing(url, expected):
    assert _repo_slug(url) == expected


# --- dry run is the default --------------------------------------------------


def test_export_is_dry_by_default(workspace):
    """Opening PRs on a shared repo must be opted into explicitly."""
    ws, sha = workspace
    (ws / "feature.py").write_text("x = 1\n")

    result = export_pr(
        ws,
        baseline_commit=sha,
        task_id="t",
        run_id="r",
        model_label="m",
        benchmark_valid=False,
        remote_url="https://github.com/example/repo.git",
    )

    assert result.pushed is False
    assert result.pr_url is None


def test_export_creates_a_namespaced_branch(workspace):
    ws, sha = workspace
    (ws / "feature.py").write_text("x = 1\n")

    result = export_pr(
        ws,
        baseline_commit=sha,
        task_id="001-add-delete-endpoint",
        run_id="deadbeef",
        model_label="m",
        benchmark_valid=True,
        remote_url="https://github.com/example/repo.git",
    )

    # Namespacing keeps agent branches clearly separated from human work.
    assert result.branch == "agent/001-add-delete-endpoint/deadbeef"


def test_push_to_local_bare_repo(workspace, tmp_path):
    """Exercises the real push path without touching GitHub."""
    from harness.pr_export import _git

    ws, sha = workspace
    (ws / "feature.py").write_text("x = 1\n")

    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "-q", "--bare", str(origin)],
        check=True,
        capture_output=True,
    )

    _git(["checkout", "-q", "-b", "agent/t/r"], cwd=ws)
    commit_agent_work(
        ws, baseline_commit=sha, task_id="t", run_id="r", model_label="m"
    )
    _git(["remote", "add", "origin", str(origin)], cwd=ws)
    _git(["push", "-q", "--set-upstream", "origin", "agent/t/r"], cwd=ws)

    branches = subprocess.run(
        ["git", "branch", "--list"], cwd=origin, capture_output=True, text=True
    ).stdout
    assert "agent/t/r" in branches
