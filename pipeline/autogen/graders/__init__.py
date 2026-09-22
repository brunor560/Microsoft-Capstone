"""Pluggable graders for the scoring harness (project brief, section 6).

Each grader runs inside the air-gapped sandbox and returns a `GraderResult`.
Graders are registered by name so the harness can select them per task --
pytest is the first implementation, not a hardcoded assumption.
"""

from graders.base import GraderResult, SandboxRunner, register, get_grader, all_graders

__all__ = [
    "GraderResult",
    "SandboxRunner",
    "register",
    "get_grader",
    "all_graders",
]
