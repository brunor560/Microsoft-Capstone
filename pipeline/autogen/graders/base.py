"""Grader interface and sandbox command runner.

A grader turns raw tool output from inside the container into a 0-100 score
plus the evidence behind it. Keeping the container interaction behind
`SandboxRunner` means graders are unit-testable with a fake runner and no
Docker.
"""

from __future__ import annotations

import subprocess
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

    def run(self, command: str, *, timeout: int = 300) -> CommandResult:
        argv = ["docker", "run", "--rm"]
        if self.network_mode:
            argv += ["--network", self.network_mode]
        argv += [
            "-v",
            f"{self.workspace.resolve()}:/workspace",
            self.image,
            "/bin/bash",
            "-lc",
            command,
        ]
        try:
            proc = subprocess.run(
                argv, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                exit_code=124, stdout="", stderr=f"timeout after {timeout}s"
            )
        return CommandResult(
            exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr
        )


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
