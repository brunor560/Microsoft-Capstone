"""Phase 2 tests for ephemeral workspace staging.

Fully offline: no LLM, no Docker, no network (remote-clone paths are tested
against a local bare repo rather than the internet).
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

from harness.staging import (
    DEFAULT_LOCAL_TARGET,
    StagingError,
    stage_workspace,
)


def _tree_digest(root: Path) -> str:
    """Stable digest of every file path + content under `root`.

    Used to prove the shared baseline testbed is untouched.
    """
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


# --- workspace creation ------------------------------------------------------


def test_defaults_to_app_baseline():
    with stage_workspace() as workspace:
        assert workspace.path.is_dir()
        assert (workspace.path / "server.js").is_file()
        assert (workspace.path / "package.json").is_file()
        assert (workspace.path / "public" / "index.html").is_file()


def test_workspace_is_git_initialized_with_baseline_commit():
    """trufflehog needs history; PR export needs a diff base."""
    with stage_workspace() as workspace:
        assert (workspace.path / ".git").is_dir()
        assert len(workspace.baseline_commit) == 40

        log = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=workspace.path,
            capture_output=True,
            text=True,
        )
        assert "baseline: pre-agent state" in log.stdout


def test_baseline_tree_is_clean():
    """A dirty baseline would make the agent's diff unattributable."""
    with stage_workspace() as workspace:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=workspace.path,
            capture_output=True,
            text=True,
        )
        assert status.stdout.strip() == ""


def test_os_cruft_is_excluded():
    """.DS_Store exists in app/ and must not reach the workspace."""
    with stage_workspace() as workspace:
        assert not (workspace.path / ".DS_Store").exists()


def test_mount_spec_targets_sandbox_workspace():
    with stage_workspace() as workspace:
        assert workspace.mount_spec == f"{workspace.path}:/workspace"


# --- the read-only guarantee -------------------------------------------------


def test_source_app_is_never_mutated():
    """The central Phase 2 invariant.

    `app/` is owned by another team member. Staging, committing, and
    modifying the workspace must leave it byte-identical.
    """
    before = _tree_digest(DEFAULT_LOCAL_TARGET)

    with stage_workspace() as workspace:
        # Simulate destructive agent behaviour inside the sandbox copy.
        (workspace.path / "server.js").write_text("// agent overwrote this\n")
        (workspace.path / "NEW_FILE.md").write_text("agent artifact\n")
        (workspace.path / "package.json").unlink()

    assert _tree_digest(DEFAULT_LOCAL_TARGET) == before


def test_workspace_is_outside_the_repository():
    """Scratch must live in tempfile space, not inside the git repo."""
    repo_root = DEFAULT_LOCAL_TARGET.parent
    with stage_workspace() as workspace:
        assert repo_root not in workspace.path.parents


# --- teardown ----------------------------------------------------------------


def test_scratch_is_wiped_on_success():
    with stage_workspace() as workspace:
        path = workspace.path
        assert path.exists()
    assert not path.exists()


def test_scratch_is_wiped_on_exception():
    """A crashed run must not leave state behind for the next benchmark."""
    captured: Path | None = None

    with pytest.raises(ValueError, match="simulated agent crash"):
        with stage_workspace() as workspace:
            captured = workspace.path
            raise ValueError("simulated agent crash")

    assert captured is not None
    assert not captured.exists()


def test_scratch_is_wiped_on_keyboard_interrupt():
    """Ctrl-C during a human-in-the-loop pause is an expected exit path."""
    captured: Path | None = None

    with pytest.raises(KeyboardInterrupt):
        with stage_workspace() as workspace:
            captured = workspace.path
            raise KeyboardInterrupt

    assert captured is not None
    assert not captured.exists()


def test_keep_flag_preserves_scratch():
    with stage_workspace(keep=True) as workspace:
        path = workspace.path
    try:
        assert path.exists(), "keep=True must preserve the scratch dir"
    finally:
        shutil.rmtree(path.parent, ignore_errors=True)


def test_runs_are_isolated_from_each_other():
    """Zero cross-contamination between benchmark runs."""
    with stage_workspace() as first:
        (first.path / "RUN_ONE.txt").write_text("leaked\n")
        first_path = first.path

    with stage_workspace() as second:
        assert second.path != first_path
        assert not (second.path / "RUN_ONE.txt").exists()


# --- explicit targets --------------------------------------------------------


def test_explicit_local_path(tmp_path):
    source = tmp_path / "custom-target"
    source.mkdir()
    (source / "main.py").write_text("print('hi')\n")

    with stage_workspace(str(source)) as workspace:
        assert (workspace.path / "main.py").read_text() == "print('hi')\n"


def test_remote_clone_from_local_bare_repo(tmp_path):
    """Exercise the remote-clone path without accessing the network.

    A local bare Git repository is used to simulate a normal remote such as
    GitHub.

    The bare repository's HEAD is explicitly pointed at `main`. A freshly
    created bare repository may still default HEAD to `master`, even though
    this test pushes the source commit to `main`. If HEAD points to a branch
    that does not exist, `git clone` can succeed without checking out the
    repository files, which would make README.md appear to be missing.
    """

    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"

    seed.mkdir()

    # Create a file that should appear in the staged clone.
    (seed / "README.md").write_text("# upstream\n")

    # Create an empty bare repository to act as the offline "remote".
    subprocess.run(
        [
            "git",
            "init",
            "-q",
            "--bare",
            str(origin),
        ],
        check=True,
    )

    # Build a normal source repository and push its initial commit to the
    # remote's `main` branch.
    for argv in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "e@x.com"],
        ["git", "config", "user.name", "e"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "upstream commit"],
        ["git", "remote", "add", "origin", str(origin)],
        ["git", "push", "-q", "origin", "HEAD:refs/heads/main"],
    ):
        subprocess.run(
            argv,
            cwd=seed,
            check=True,
            capture_output=True,
        )
    subprocess.run(
        [
            "git",
            "symbolic-ref",
            "HEAD",
            "refs/heads/main",
        ],
        cwd=origin,
        check=True,
        capture_output=True,
    )

    with stage_workspace(f"file://{origin}") as workspace:
        # The remote's files should have been checked out into the scratch
        # workspace before the harness creates its controlled baseline commit.
        assert (
            workspace.path / "README.md"
        ).read_text() == "# upstream\n"

        # Staging deliberately replaces upstream Git history with one clean
        # benchmark baseline commit. This allows subsequent diffs to represent
        # only the changes made by the coding agent.
        log = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
            ],
            cwd=workspace.path,
            capture_output=True,
            text=True,
        )

        assert (
            "baseline: pre-agent state"
            in log.stdout
        )

        assert (
            "upstream commit"
            not in log.stdout
        )


def test_file_instead_of_directory_raises(tmp_path):
    target = tmp_path / "a-file.txt"
    target.write_text("not a dir\n")

    with pytest.raises(StagingError, match="not a directory"):
        with stage_workspace(str(target)):
            pass


def test_bad_clone_url_raises_and_cleans_up():
    with pytest.raises(StagingError, match="git clone failed"):
        with stage_workspace("file:///nonexistent/repo.git"):
            pass
