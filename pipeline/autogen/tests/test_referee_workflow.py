"""SRS Spec 4.5: the trusted-base grading workflow (TC-4.5-3).

These tests read the workflow file and check the properties the
specification depends on. They do not run GitHub Actions.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

WORKFLOW = (
    Path(__file__).resolve().parents[3] / ".github" / "workflows" / "agent-pr-referee.yml"
)

# The repository's default branch.
DEFAULT_BRANCH = "master"

PINNED = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")


@pytest.fixture(scope="module")
def workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _steps(job: dict) -> list[dict]:
    return job["steps"]


def _text(job: dict) -> str:
    return yaml.safe_dump(job)


def test_triggers_on_pull_requests_to_the_default_branch(workflow):
    """Clause 4.5.5."""
    # PyYAML reads the bare key `on` as the boolean True.
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["pull_request"]["branches"] == [DEFAULT_BRANCH]
    assert set(triggers) == {"pull_request"}


def test_every_action_is_pinned_by_commit_sha(workflow):
    """Clause 4.5.6."""
    used = [
        step["uses"]
        for job in workflow["jobs"].values()
        for step in _steps(job)
        if "uses" in step
    ]
    assert used, "the workflow should use at least one action"
    for action in used:
        assert PINNED.match(action), f"not pinned by SHA: {action}"


def test_no_permission_is_granted_by_default(workflow):
    assert workflow["permissions"] == {}


def test_grading_and_publishing_are_separate_jobs(workflow):
    """Clause 4.5.4."""
    assert set(workflow["jobs"]) == {"grade", "publish"}
    assert workflow["jobs"]["publish"]["needs"] == "grade"


def test_the_grading_job_has_no_write_permission(workflow):
    """Clause 4.5.4: untrusted code never runs next to a write token."""
    assert workflow["jobs"]["grade"]["permissions"] == {"contents": "read"}


def test_only_the_publishing_job_can_write(workflow):
    assert workflow["jobs"]["publish"]["permissions"] == {"pull-requests": "write"}


def test_the_publisher_never_touches_candidate_code(workflow):
    publish = workflow["jobs"]["publish"]
    assert not any("checkout" in step.get("uses", "") for step in _steps(publish))
    assert not any("run" in step for step in _steps(publish))
    assert "candidate" not in _text(publish)


def test_grading_logic_comes_from_the_base_branch(workflow):
    """Clause 4.5.1."""
    steps = _steps(workflow["jobs"]["grade"])
    checkouts = {
        step["with"]["path"]: step["with"]
        for step in steps
        if "checkout" in step.get("uses", "")
    }

    assert "pull_request.base.sha" in checkouts["trusted"]["ref"]
    assert "pull_request.head.sha" in checkouts["candidate"]["ref"]
    for options in checkouts.values():
        assert options["persist-credentials"] is False

    # Everything that executes does so from the trusted checkout.
    for step in steps:
        if "run" in step and "working-directory" in step:
            assert step["working-directory"].startswith("trusted/")

    grading = next(step for step in steps if "harness.referee" in step.get("run", ""))
    assert grading["working-directory"] == "trusted/pipeline/autogen"


def test_grading_must_finish_within_120_seconds(workflow):
    """Clause 4.5.3."""
    steps = _steps(workflow["jobs"]["grade"])
    grading = next(step for step in steps if "harness.referee" in step.get("run", ""))
    assert grading["timeout-minutes"] <= 2
