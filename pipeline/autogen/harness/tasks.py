"""Task ingestion (project brief, section 3).

Loads benchmark task definitions from `pipeline/tasks/*.md`. Each file is
Markdown with a YAML front-matter header; the body is the prompt handed to
the agent under test.

Tasks live at the `pipeline/` level rather than under any one pipeline's
directory so the same matrix applies evenly to every framework evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

TASKS_DIR = Path(__file__).resolve().parent.parent.parent / "tasks"

_DELIMITER = "---"


class TaskError(RuntimeError):
    """Raised when a task file is missing or malformed."""


@dataclass(frozen=True)
class Task:
    """A single benchmark task."""

    task_id: str
    title: str
    target: str
    prompt: str
    ipi_trap: bool
    path: Path
    acceptance: dict[str, Any] = field(default_factory=dict)
    security_check: dict[str, Any] = field(default_factory=dict)

    @property
    def test_command(self) -> str | None:
        """Command the Functionality (F) grader runs inside the sandbox."""
        return self.acceptance.get("test_command")

    @property
    def forbidden_patterns(self) -> list[str]:
        """Strings that must not appear in the agent's diff (S = 0 if found)."""
        return list(self.security_check.get("forbidden_patterns", []))


def _split_front_matter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    """Separate the YAML header from the Markdown body."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != _DELIMITER:
        raise TaskError(f"{path.name}: missing opening '---' front-matter delimiter")

    for index in range(1, len(lines)):
        if lines[index].strip() == _DELIMITER:
            header_raw = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :]).strip()
            break
    else:
        raise TaskError(f"{path.name}: front matter is never closed with '---'")

    try:
        header = yaml.safe_load(header_raw) or {}
    except yaml.YAMLError as exc:
        raise TaskError(f"{path.name}: invalid YAML front matter: {exc}") from exc

    if not isinstance(header, dict):
        raise TaskError(f"{path.name}: front matter must be a mapping")

    return header, body


def load_task(path: Path) -> Task:
    """Load and validate a single task file."""
    if not path.exists():
        raise TaskError(f"Task file not found: {path}")

    header, body = _split_front_matter(path.read_text(), path)

    for required in ("task_id", "title", "target"):
        if not header.get(required):
            raise TaskError(f"{path.name}: front matter missing required '{required}'")

    if not body:
        raise TaskError(f"{path.name}: task body (the agent prompt) is empty")

    return Task(
        task_id=str(header["task_id"]),
        title=str(header["title"]),
        target=str(header["target"]),
        prompt=body,
        ipi_trap=bool(header.get("ipi_trap", False)),
        path=path,
        acceptance=dict(header.get("acceptance") or {}),
        security_check=dict(header.get("security_check") or {}),
    )


def load_all_tasks(tasks_dir: Path | None = None) -> list[Task]:
    """Load every task in the matrix, sorted by task_id.

    Raises on a duplicate task_id: two tasks sharing an id would overwrite
    each other's telemetry artifact at `logs/<task_id>_<run_id>.json`.
    """
    directory = tasks_dir or TASKS_DIR
    if not directory.is_dir():
        raise TaskError(f"Tasks directory not found: {directory}")

    tasks = [
        load_task(path)
        for path in sorted(directory.glob("*.md"))
        if path.name != "README.md"
    ]

    seen: dict[str, Path] = {}
    for task in tasks:
        if task.task_id in seen:
            raise TaskError(
                f"Duplicate task_id '{task.task_id}' in {task.path.name} "
                f"and {seen[task.task_id].name}; telemetry artifacts would collide."
            )
        seen[task.task_id] = task.path

    return sorted(tasks, key=lambda t: t.task_id)


def resolve_target(task: Task) -> str | None:
    """Translate a task's `target` into a staging argument.

    `app` (or `local`) means the repository-root baseline testbed, which
    staging resolves itself, so None is returned. Anything else is passed
    through verbatim as a URL or path.
    """
    if task.target in {"app", "local"}:
        return None
    return task.target
