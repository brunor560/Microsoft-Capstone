"""Phase 2: ephemeral workspace staging (project brief, section 3).

Guarantees a "fresh session" per benchmark run. The host stages a temporary
workspace, bind-mounts it into the sandbox, and wipes it afterwards so that no
state leaks between runs.

Two invariants this module exists to enforce:

  1. The source codebase is NEVER mutated. `app/` is a shared baseline testbed
     owned by another team member; it is copied out, never worked in.
  2. The scratch directory is ALWAYS removed, including on exception or
     KeyboardInterrupt, so a crashed run cannot silently contaminate the next.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

# Repo root is three levels up: harness/ -> autogen/ -> pipeline/ -> root.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_LOCAL_TARGET = REPO_ROOT / "app"

# Never copied into the workspace: OS cruft and any pre-existing git history
# (a fresh baseline tree is initialized instead, so diffs attribute cleanly
# to the agent).
COPY_EXCLUDE = shutil.ignore_patterns(
    ".DS_Store",
    "__pycache__",
    "node_modules",
    ".git",
    ".venv",
)


class StagingError(RuntimeError):
    """Raised when a workspace cannot be prepared."""


@dataclass(frozen=True)
class Workspace:
    """A staged, git-initialized scratch workspace."""

    path: Path
    source: str
    baseline_commit: str

    @property
    def mount_spec(self) -> str:
        """Docker bind-mount argument targeting the sandbox's /workspace."""
        return f"{self.path}:/workspace"


def _git(args: list[str], cwd: Path) -> str:
    """Run git in `cwd`, raising StagingError with real stderr on failure."""
    proc = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        raise StagingError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _init_baseline(path: Path) -> str:
    """Initialize a baseline git tree and return the baseline commit SHA.

    The baseline matters for two downstream consumers: `trufflehog git`
    needs history to scan, and the PR export needs a diff base to know what
    the agent actually changed.
    """
    _git(["init", "-q"], cwd=path)
    # Commit identity is set locally so staging does not depend on, or
    # inherit, the host user's global git config.
    _git(["config", "user.email", "eval-harness@localhost"], cwd=path)
    _git(["config", "user.name", "Eval Harness"], cwd=path)
    _git(["add", "-A"], cwd=path)
    _git(["commit", "-q", "-m", "baseline: pre-agent state", "--allow-empty"], cwd=path)
    return _git(["rev-parse", "HEAD"], cwd=path)


def _stage_local(target: Path, dest: Path) -> str:
    """Copy a local directory into the scratch space.

    `dirs_exist_ok=False` against a fresh mkdtemp child guarantees we never
    write into a pre-existing tree.
    """
    if not target.exists():
        raise StagingError(f"Local target does not exist: {target}")
    if not target.is_dir():
        raise StagingError(f"Local target is not a directory: {target}")

    shutil.copytree(target, dest, ignore=COPY_EXCLUDE)
    return str(target)


def _stage_clone(url: str, dest: Path) -> str:
    """Clone a remote repository into the scratch space."""
    proc = subprocess.run(
        ["git", "clone", "--quiet", url, str(dest)],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise StagingError(f"git clone failed for {url}: {proc.stderr.strip()}")

    # Drop the upstream history so the agent's work is diffed against a
    # baseline we control, matching the local-copy path's semantics.
    shutil.rmtree(dest / ".git", ignore_errors=True)
    return url


def _looks_remote(target: str) -> bool:
    """Decide whether `target` is a git URL rather than a local directory.

    `file://` is included because it is a real git transport, not a path:
    `git clone file:///path/to/repo.git` is valid and is what the offline
    clone tests use. Omitting it silently routed such URLs into the
    local-copy branch, where they failed as "directory does not exist".
    """
    return target.startswith(
        ("http://", "https://", "git@", "ssh://", "file://", "git://")
    )


@contextmanager
def stage_workspace(
    repo: str | None = None,
    *,
    keep: bool = False,
) -> Iterator[Workspace]:
    """Stage an ephemeral workspace, yielding it, then wipe it.

    `repo` may be a remote URL, a local path, or None (defaults to the
    repository-root `app/` baseline testbed).

    Set `keep=True` to preserve the scratch dir for debugging; the path is
    printed so it can be removed manually. This is deliberately opt-in --
    the default must always clean up.
    """
    scratch_root = Path(tempfile.mkdtemp(prefix="eval-run-"))
    workspace_path = scratch_root / "workspace"

    try:
        target = repo or str(DEFAULT_LOCAL_TARGET)

        if _looks_remote(target):
            source = _stage_clone(target, workspace_path)
        else:
            source = _stage_local(Path(target).expanduser().resolve(), workspace_path)

        baseline_commit = _init_baseline(workspace_path)

        yield Workspace(
            path=workspace_path,
            source=source,
            baseline_commit=baseline_commit,
        )
    finally:
        if keep:
            print(f"[staging] scratch preserved at {scratch_root}")
        else:
            # ignore_errors: teardown must never mask the real exception
            # that caused us to unwind.
            shutil.rmtree(scratch_root, ignore_errors=True)
