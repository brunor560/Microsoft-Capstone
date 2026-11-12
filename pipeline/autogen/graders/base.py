"""Grader interface and sandbox command runner.

A grader turns raw tool output from inside the container into a 0-100 score
plus the evidence behind it. Keeping the container interaction behind
`SandboxRunner` means graders are unit-testable with a fake runner and no
Docker.
"""

from __future__ import annotations

import docker
import time
from harness.nonroot import create_nonroot
from harness.deadline import remove_verified, run_with_deadline
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

IMAGE = "agentic-eval-sandbox:latest"


@dataclass
class CommandResult:
    """Outcome of one command executed inside the sandbox."""

    exit_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def output(self) -> str:
        return self.stdout + self.stderr


class SandboxRunner(Protocol):
    """Executes a shell command inside the grading container."""

    def run(self, command: str, *, timeout: int = 300) -> CommandResult: ...


@dataclass
class DockerSandboxRunner:
    """Runs grader commands in the pinned sandbox image.

    Network is disabled by default: graders analyse code, they do not need
    to reach the internet, and a grader with network access would reopen the
    exfiltration vector Phase 3 closed.
    """

    workspace: Path
    image: str = IMAGE
    network_mode: str | None = "none"

    command_events: list[dict[str, Any]] = field(default_factory=list)

    def run(self, command: str, *, timeout: int = 300) -> CommandResult:
        client = docker.from_env()
        container = None
        try:
            options = dict(
                volumes={
                    str(self.workspace.resolve()): {
                        "bind": "/workspace", "mode": "rw"
                    }
                },
                working_dir="/workspace", auto_remove=False,
                tty=True, detach=True, entrypoint="/bin/sh",
                cpu_period=100_000, cpu_quota=200_000,
                mem_limit=2_000_000_000, memswap_limit=2_000_000_000,
                pids_limit=128,
            )
            if self.network_mode:
                options["network_mode"] = self.network_mode
            container = create_nonroot(
                type(client.containers).create, client.containers,
                self.image, None, options,
            )
            container.start()
            result = run_with_deadline(
                container, ["/bin/bash", "-lc", command],
                timeout, self.command_events,
            )
            return CommandResult(*result)
        finally:
            try:
                if container is not None:
                    event = next(
                        (e for e in reversed(self.command_events)
                         if e["container_id"] == container.id),
                        None,
                    )
                    cleanup_started = time.monotonic()
                    try:
                        remove_verified(container.id, client.api._version)
                    except Exception:
                        if event is not None:
                            event["cleanup"] = "failed"
                        raise
                    else:
                        if event is not None:
                            event["cleanup"] = "succeeded"
                            event["cleanup_seconds"] = (
                                time.monotonic() - cleanup_started
                            )
            finally:
                client.close()


@dataclass
class GraderResult:
    """A single dimension's score with supporting evidence.

    `score` is always 0-100; the weighted combination happens in the
    scoring harness, not here.
    """

    name: str
    score: float
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def failed(self) -> bool:
        """True when the grader could not run at all.

        Distinguished from a legitimate score of 0: a crashed grader must
        not be silently reported as "the agent scored zero".
        """
        return self.error is not None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "score": round(self.score, 2),
            "details": self.details,
        }
        if self.error:
            payload["error"] = self.error
        return payload


# --- registry ---------------------------------------------------------------

_REGISTRY: dict[str, Callable[..., GraderResult]] = {}


def register(name: str):
    """Decorator registering a grader function under `name`."""

    def decorator(func: Callable[..., GraderResult]):
        _REGISTRY[name] = func
        return func

    return decorator


def get_grader(name: str) -> Callable[..., GraderResult]:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "(none registered)"
        raise KeyError(f"Unknown grader '{name}'. Available: {available}")
    return _REGISTRY[name]


def all_graders() -> dict[str, Callable[..., GraderResult]]:
    return dict(_REGISTRY)
