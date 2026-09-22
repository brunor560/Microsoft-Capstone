"""Phase 2 tests for task ingestion. Fully offline."""

from __future__ import annotations

import pytest

from harness.tasks import (
    TASKS_DIR,
    Task,
    TaskError,
    load_all_tasks,
    load_task,
    resolve_target,
)


# --- the real task matrix ----------------------------------------------------


def test_shipped_tasks_all_parse():
    tasks = load_all_tasks()
    assert len(tasks) >= 2
    assert all(isinstance(t, Task) for t in tasks)


def test_task_ids_are_unique():
    """Colliding ids would overwrite each other's telemetry artifact."""
    tasks = load_all_tasks()
    ids = [t.task_id for t in tasks]
    assert len(ids) == len(set(ids))


def test_readme_is_not_treated_as_a_task():
    assert (TASKS_DIR / "README.md").exists()
    assert all(t.path.name != "README.md" for t in load_all_tasks())


def test_every_task_declares_a_test_command():
    """Functionality (F) is unmeasurable without one."""
    for task in load_all_tasks():
        assert task.test_command, f"{task.task_id} has no acceptance.test_command"


def test_ipi_task_is_flagged_and_has_forbidden_patterns():
    tasks = {t.task_id: t for t in load_all_tasks()}
    ipi = tasks["002-input-validation-ipi"]

    assert ipi.ipi_trap is True
    assert "AKIA" in ipi.forbidden_patterns
    # The injection payload must survive into the prompt the agent sees.
    assert "AKIA4KQZWXYZ7TRFMNQD" in ipi.prompt


def test_non_ipi_task_is_not_flagged():
    tasks = {t.task_id: t for t in load_all_tasks()}
    assert tasks["001-add-delete-endpoint"].ipi_trap is False


def test_shipped_tasks_target_the_local_baseline():
    for task in load_all_tasks():
        assert resolve_target(task) is None


# --- target resolution -------------------------------------------------------


def _write(tmp_path, name: str, text: str):
    path = tmp_path / name
    path.write_text(text)
    return path


VALID = """---
task_id: t-1
title: Example
target: app
acceptance:
  test_command: "npm test"
---

Do the thing.
"""


def test_remote_target_passes_through(tmp_path):
    path = _write(
        tmp_path,
        "remote.md",
        VALID.replace("target: app", "target: https://github.com/example/repo.git"),
    )
    assert resolve_target(load_task(path)) == "https://github.com/example/repo.git"


# --- malformed input ---------------------------------------------------------


def test_missing_front_matter_raises(tmp_path):
    path = _write(tmp_path, "bad.md", "Just a body, no header.\n")
    with pytest.raises(TaskError, match="missing opening"):
        load_task(path)


def test_unclosed_front_matter_raises(tmp_path):
    path = _write(tmp_path, "bad.md", "---\ntask_id: x\ntitle: y\ntarget: app\n")
    with pytest.raises(TaskError, match="never closed"):
        load_task(path)


def test_missing_required_field_raises(tmp_path):
    path = _write(tmp_path, "bad.md", VALID.replace("task_id: t-1\n", ""))
    with pytest.raises(TaskError, match="missing required 'task_id'"):
        load_task(path)


def test_empty_body_raises(tmp_path):
    """An empty prompt would send the agent nothing to do."""
    path = _write(tmp_path, "bad.md", VALID.replace("Do the thing.\n", ""))
    with pytest.raises(TaskError, match="body .* is empty"):
        load_task(path)


def test_invalid_yaml_raises(tmp_path):
    path = _write(tmp_path, "bad.md", "---\ntask_id: [unclosed\n---\n\nBody.\n")
    with pytest.raises(TaskError, match="invalid YAML"):
        load_task(path)


def test_duplicate_task_ids_raise(tmp_path):
    _write(tmp_path, "a.md", VALID)
    _write(tmp_path, "b.md", VALID.replace("title: Example", "title: Clone"))
    with pytest.raises(TaskError, match="Duplicate task_id"):
        load_all_tasks(tmp_path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(TaskError, match="not found"):
        load_task(tmp_path / "nope.md")
