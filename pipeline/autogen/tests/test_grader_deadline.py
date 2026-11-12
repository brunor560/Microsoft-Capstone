"""Verify grader timeouts kill detached children and preserve real failures."""
import shlex
import time
import docker
import pytest

from graders.base import DockerSandboxRunner

def test_timeout_removes_detached_child(tmp_path):
    child = (
        "import time; from pathlib import Path; i=0\n"
        "while True:\n"
        " Path('/workspace/heartbeat').write_text(str(i)); "
        "i+=1; time.sleep(.05)\n"
    )
    parent = (
        "import subprocess,sys,time; "
        f"subprocess.Popen([sys.executable,'-c',{child!r}],"
        "start_new_session=True); time.sleep(300)"
    )
    runner = DockerSandboxRunner(workspace=tmp_path)
    result = runner.run("python -c " + shlex.quote(parent), timeout=2)

    assert result.exit_code == 124, result.output
    assert len(runner.command_events) == 1
    event = runner.command_events[0]
    assert event["kind"] == "command_timeout"
    assert event["termination"] == "succeeded"
    assert event["cleanup"] == "succeeded"
    assert 2 <= event["termination_requested_seconds"] <= 3
    assert event["termination_completed_seconds"] <= 3

    heartbeat = tmp_path / "heartbeat"
    before = heartbeat.read_text()
    time.sleep(.3)
    assert heartbeat.read_text() == before, "Detached child survived"

    client = docker.from_env()
    try:
        with pytest.raises(docker.errors.NotFound):
            client.api.inspect_container(event["container_id"])
    finally:
        client.close()

def test_real_failure_keeps_its_exit_code(tmp_path):
    runner = DockerSandboxRunner(workspace=tmp_path)
    result = runner.run("printf ready; exit 7", timeout=5)
    assert result.exit_code == 7
    assert "ready" in result.output
    assert runner.command_events == []


def test_runner_preserves_stdout_and_stderr(tmp_path):
    result = DockerSandboxRunner(workspace=tmp_path).run(
        "printf scanner-output; printf scanner-diagnostic >&2", timeout=5
    )
    assert result.exit_code == 0, result.output
    assert result.stdout == "scanner-output"
    assert "scanner-diagnostic" in result.stderr
    assert "scanner-diagnostic" not in result.stdout
    assert "scanner-output" not in result.stderr
