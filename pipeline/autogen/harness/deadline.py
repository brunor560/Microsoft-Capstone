"""Host-enforced command deadlines and verified container removal."""
import math
import queue
import threading
import time
from typing import NamedTuple

import docker
from docker.errors import APIError, NotFound

def remove_verified(container_id, api_version):
    terminate_verified(container_id, api_version)
    client = docker.from_env(timeout=10, version=api_version)
    try:
        try:
            client.api.remove_container(container_id, force=True)
        except NotFound:
            pass
        try:
            client.api.inspect_container(container_id)
        except NotFound:
            return
        raise RuntimeError(f"Container survived removal: {container_id}")
    finally:
        client.close()

def terminate_verified(container_id, api_version):
    expires = time.monotonic() + 1
    client = docker.from_env(timeout=1, version=api_version)
    try:
        try:
            client.api.kill(container_id, signal="SIGKILL")
        except APIError as exc:
            if exc.status_code not in (404, 409):
                raise
        while True:
            remaining = expires - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Process termination exceeded one second")
            client.api.timeout = remaining
            try:
                info = client.api.inspect_container(container_id)
            except NotFound:
                return
            if info.get("State", {}).get("Running", True) is False:
                return
            time.sleep(min(.02, max(0, expires - time.monotonic())))
    finally:
        client.close()


class CommandOutcome(NamedTuple):
    exit_code: int
    stdout: str
    stderr: str

def run_with_deadline(container, command, timeout, events):
    requested = float(timeout)
    if not math.isfinite(requested) or requested <= 0:
        raise ValueError("Command timeout must be positive and finite")
    limit = min(requested, 60.0)
    replies = queue.Queue(maxsize=1)

    def execute():
        try:
            replies.put((container.exec_run(command, tty=False, demux=True), None))
        except Exception as exc:
            replies.put((None, exc))

    started = time.monotonic()
    threading.Thread(target=execute, daemon=True).start()
    try:
        remaining = max(0, limit - (time.monotonic() - started))
        result, error = replies.get(timeout=remaining)
    except queue.Empty:
        result, error = None, None

    if result is not None:
        streams = result.output or (None, None)
        if not isinstance(streams, tuple) or len(streams) != 2:
            raise RuntimeError("Container runtime did not separate stdout and stderr")
        stdout, stderr = streams
        return CommandOutcome(
            result.exit_code,
            (stdout or b"").decode(errors="replace"),
            (stderr or b"").decode(errors="replace"),
        )
    if error is not None and time.monotonic() - started < limit:
        raise error

    event = {
        "kind": "command_timeout",
        "container_id": container.id,
        "limit_seconds": limit,
        "termination_requested_seconds": time.monotonic() - started,
        "cleanup": "pending",
    }
    events.append(event)
    try:
        terminate_verified(container.id, container.client.api._version)
        event["termination_completed_seconds"] = time.monotonic() - started
        if event["termination_completed_seconds"] > limit + 1:
            raise RuntimeError("Termination exceeded the one-second allowance")
        event["termination"] = "succeeded"
    except Exception as exc:
        event["termination"] = "failed"
        raise RuntimeError("Timeout termination failed; infrastructure error") from exc

    return CommandOutcome(
        124, "", f"command_timeout: {limit:g}s; workload terminated"
    )
