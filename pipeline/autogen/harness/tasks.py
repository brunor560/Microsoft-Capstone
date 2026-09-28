"""Task ingestion (project brief, section 3).

Loads benchmark task definitions from `pipeline/tasks/*.md`.

Each task contains:

  * task metadata in YAML front matter
  * the agent prompt in Markdown
  * acceptance-test configuration
  * optional security checks

Tasks live at the pipeline level rather than inside one specific model
implementation so the same task matrix can be evaluated across different
agent frameworks and model providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


TASKS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "tasks"
)

_DELIMITER = "---"


class TaskError(RuntimeError):
    """Raised when a benchmark task file is missing or malformed."""


@dataclass(frozen=True)
class Task:
    """A single benchmark task."""

    task_id: str
    title: str
    target: str
    prompt: str
    ipi_trap: bool
    path: Path

    acceptance: dict[str, Any] = field(
        default_factory=dict
    )

    security_check: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def test_command(self) -> str | None:
        """Return the command used to execute this task's acceptance tests."""

        return self.acceptance.get(
            "test_command"
        )

    @property
    def test_framework(self) -> str | None:
        """Return the functionality grader declared by the task.

        Example task metadata:

            acceptance:
              test_command: "npm test"
              test_framework: node-test

        Previously the framework value existed in the Markdown task file
        but was never exposed by the Task object. As a result,
        run_benchmark.py ignored it and always invoked the pytest grader.

        Exposing it here lets each task explicitly choose the correct
        language-specific grader.
        """

        value = self.acceptance.get(
            "test_framework"
        )

        return (
            str(value)
            if value
            else None
        )

    @property
    def forbidden_patterns(self) -> list[str]:
        """Return strings that cause the security dimension to fail."""

        return list(
            self.security_check.get(
                "forbidden_patterns",
                [],
            )
        )


def _split_front_matter(
    text: str,
    path: Path,
) -> tuple[dict[str, Any], str]:
    """Separate the YAML task header from the Markdown prompt body."""

    lines = text.splitlines()

    if (
        not lines
        or lines[0].strip() != _DELIMITER
    ):
        raise TaskError(
            f"{path.name}: missing opening "
            f"'---' front-matter delimiter"
        )

    for index in range(
        1,
        len(lines),
    ):
        if (
            lines[index].strip()
            == _DELIMITER
        ):
            header_raw = "\n".join(
                lines[1:index]
            )

            body = "\n".join(
                lines[index + 1 :]
            ).strip()

            break

    else:
        raise TaskError(
            f"{path.name}: front matter is "
            f"never closed with '---'"
        )

    try:
        header = (
            yaml.safe_load(
                header_raw
            )
            or {}
        )

    except yaml.YAMLError as exc:
        raise TaskError(
            f"{path.name}: invalid YAML "
            f"front matter: {exc}"
        ) from exc

    if not isinstance(
        header,
        dict,
    ):
        raise TaskError(
            f"{path.name}: front matter "
            f"must be a mapping"
        )

    return header, body


def load_task(
    path: Path,
) -> Task:
    """Load and validate one benchmark task definition."""

    if not path.exists():
        raise TaskError(
            f"Task file not found: {path}"
        )

    header, body = _split_front_matter(
        path.read_text(),
        path,
    )

    for required in (
        "task_id",
        "title",
        "target",
    ):
        if not header.get(
            required
        ):
            raise TaskError(
                f"{path.name}: front matter "
                f"missing required '{required}'"
            )

    if not body:
        raise TaskError(
            f"{path.name}: task body "
            f"(the agent prompt) is empty"
        )

    return Task(
        task_id=str(
            header["task_id"]
        ),
        title=str(
            header["title"]
        ),
        target=str(
            header["target"]
        ),
        prompt=body,
        ipi_trap=bool(
            header.get(
                "ipi_trap",
                False,
            )
        ),
        path=path,
        acceptance=dict(
            header.get(
                "acceptance"
            )
            or {}
        ),
        security_check=dict(
            header.get(
                "security_check"
            )
            or {}
        ),
    )


def load_all_tasks(
    tasks_dir: Path | None = None,
) -> list[Task]:
    """Load all benchmark tasks, sorted by task ID."""

    directory = (
        tasks_dir
        or TASKS_DIR
    )

    if not directory.is_dir():
        raise TaskError(
            f"Tasks directory not found: "
            f"{directory}"
        )

    tasks = [
        load_task(path)
        for path in sorted(
            directory.glob("*.md")
        )
        if path.name != "README.md"
    ]

    seen: dict[str, Path] = {}

    for task in tasks:
        if task.task_id in seen:
            raise TaskError(
                f"Duplicate task_id "
                f"'{task.task_id}' in "
                f"{task.path.name} and "
                f"{seen[task.task_id].name}; "
                f"telemetry artifacts would collide."
            )

        seen[
            task.task_id
        ] = task.path

    return sorted(
        tasks,
        key=lambda task: task.task_id,
    )


def resolve_target(
    task: Task,
) -> str | None:
    """Translate the task target into a staging source.

    `app` and `local` refer to the repository's local benchmark target.
    Remote paths or repository URLs are returned unchanged.
    """

    if task.target in {
        "app",
        "local",
    }:
        return None

    return task.target
