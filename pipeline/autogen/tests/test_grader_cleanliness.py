"""Graders must not contaminate the directory they grade.

Requires Docker; no LLM, no API spend.

### Why this file exists

During Phase 6 the referee was pointed at the repository's `app/` directory
and left `.eval-pytest-report.json` behind in it. `app/` is a shared
baseline testbed owned by another team member and is meant to be strictly
read-only.

No tracked file was modified, so `git diff` stayed clean and only
`git status` revealed it. That is exactly the kind of quiet side effect that
survives review, so it is pinned here with a byte-level digest.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

import graders.functionality  # noqa: F401 - registers the grader
import graders.quality  # noqa: F401
import graders.security  # noqa: F401
from graders.base import DockerSandboxRunner, get_grader
from graders.quality import measure_baseline

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


def _snapshot(root: Path) -> tuple[str, set[str]]:
    """Digest of all file contents, plus the set of relative paths.

    Returning both distinguishes "a file changed" from "a file appeared".
    """
    digest = hashlib.sha256()
    names: set[str] = set()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = str(path.relative_to(root))
        names.add(rel)
        digest.update(rel.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest(), names


def _fixture(path: Path) -> None:
    (path / "mod.py").write_text("def add(a, b):\n    return a + b\n")
    (path / "test_mod.py").write_text(
        "from mod import add\n\ndef test_add():\n    assert add(1, 2) == 3\n"
    )
    for argv in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "eval@example.com"],
        ["git", "config", "user.name", "eval"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "baseline"],
    ):
        subprocess.run(argv, cwd=path, check=True, capture_output=True)


def test_functionality_grader_leaves_no_artifacts(tmp_path):
    """The pytest report must be written inside the container, not the mount."""
    _fixture(tmp_path)
    before_digest, before_names = _snapshot(tmp_path)

    result = get_grader("pytest")(DockerSandboxRunner(workspace=tmp_path))
    assert result.score == 100.0, "grader must still work"

    after_digest, after_names = _snapshot(tmp_path)

    assert after_names - before_names == set(), (
        f"grader created files in the graded tree: {after_names - before_names}"
    )
    assert after_digest == before_digest


def test_quality_grader_leaves_no_artifacts(tmp_path):
    """complexipy writes to its CWD and compileall writes __pycache__."""
    _fixture(tmp_path)
    before_digest, before_names = _snapshot(tmp_path)

    runner = DockerSandboxRunner(workspace=tmp_path)
    baseline = measure_baseline(runner)
    assert baseline["complexity"] is not None, "grader must still work"

    result = get_grader("quality")(runner, baseline=baseline)
    assert result.score == 100.0

    after_digest, after_names = _snapshot(tmp_path)

    assert after_names - before_names == set(), (
        f"grader created files in the graded tree: {after_names - before_names}"
    )
    assert after_digest == before_digest


def test_security_grader_leaves_no_artifacts(tmp_path):
    _fixture(tmp_path)
    before_digest, before_names = _snapshot(tmp_path)

    result = get_grader("trufflehog")(DockerSandboxRunner(workspace=tmp_path))
    assert result.score == 100.0, "grader must still work"

    after_digest, after_names = _snapshot(tmp_path)

    assert after_names - before_names == set()
    assert after_digest == before_digest


def test_full_referee_pass_leaves_no_artifacts(tmp_path):
    """The exact scenario that contaminated app/ in Phase 6."""
    from harness.referee import referee

    _fixture(tmp_path)
    before_digest, before_names = _snapshot(tmp_path)

    verdict = referee(tmp_path)
    assert verdict["final_score"] is not None, "referee must still grade"

    after_digest, after_names = _snapshot(tmp_path)

    assert after_names - before_names == set(), (
        f"referee contaminated the graded tree: {after_names - before_names}"
    )
    assert after_digest == before_digest
