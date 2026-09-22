"""Phase 2 gate: end-to-end ephemeral staging verification.

Proves the full staging lifecycle against the real sandbox image:

  1. the task matrix loads,
  2. a workspace stages from the `app/` baseline,
  3. it bind-mounts into the container and the code is visible there,
  4. destructive changes inside the container do not touch `app/`,
  5. the scratch directory is wiped on exit.

Usage:
    ./.venv/bin/python -m harness.verify_staging
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from harness.staging import DEFAULT_LOCAL_TARGET, stage_workspace
from harness.tasks import load_all_tasks

IMAGE = "agentic-eval-sandbox:latest"


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


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


def main() -> int:
    failures: list[str] = []

    print("--- task matrix ---")
    try:
        tasks = load_all_tasks()
        for task in tasks:
            flag = " [IPI TRAP]" if task.ipi_trap else ""
            print(f"  OK   {task.task_id:<32} {task.title[:34]}{flag}")
    except Exception as exc:  # noqa: BLE001
        print(f"  FAIL could not load tasks: {exc}")
        return 1

    print("\n--- baseline integrity ---")
    digest_before = _tree_digest(DEFAULT_LOCAL_TARGET)
    print(f"  app/ digest (before) {digest_before[:16]}...")

    print("\n--- staging lifecycle ---")
    docker_ok = _docker_available()
    if not docker_ok:
        print(f"  SKIP docker image {IMAGE} unavailable; mount check skipped")

    scratch: Path | None = None
    with stage_workspace() as workspace:
        scratch = workspace.path
        print(f"  OK   staged at {workspace.path}")
        print(f"  OK   baseline commit {workspace.baseline_commit[:12]}")

        if not (workspace.path / "server.js").is_file():
            failures.append("server.js missing from staged workspace")

        if docker_ok:
            # Verify the bind-mount, then have the CONTAINER destroy the
            # workspace -- the strongest form of the read-only guarantee.
            proc = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    workspace.mount_spec,
                    IMAGE,
                    "/bin/bash",
                    "-lc",
                    "ls /workspace/server.js && rm -rf /workspace/* "
                    "&& echo 'container wiped workspace'",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if proc.returncode == 0 and "container wiped workspace" in proc.stdout:
                print("  OK   bind-mount visible in container")
                print("  OK   container deleted workspace contents")
            else:
                print(f"  FAIL container mount check: {proc.stderr.strip()[:80]}")
                failures.append("bind-mount verification failed")

    if scratch is not None and scratch.exists():
        print(f"  FAIL scratch still present: {scratch}")
        failures.append("scratch directory was not wiped")
    else:
        print("  OK   scratch wiped on exit")

    print("\n--- baseline integrity (after) ---")
    digest_after = _tree_digest(DEFAULT_LOCAL_TARGET)
    print(f"  app/ digest (after)  {digest_after[:16]}...")
    if digest_after == digest_before:
        print("  OK   app/ is byte-identical")
    else:
        print("  FAIL app/ WAS MODIFIED")
        failures.append("app/ baseline testbed was mutated")

    print()
    if failures:
        print(f"PHASE 2 GATE: FAILED ({len(failures)} problem(s))")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PHASE 2 GATE: PASSED")
    print("  Staging is ephemeral and the shared baseline is untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
