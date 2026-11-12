"""Agent watchdog checks; no model calls."""
import asyncio
import time
import docker
import pytest

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from harness.executor import IsolatedDockerCodeExecutor

CHILD = (
    "import time,signal; from pathlib import Path; i=0\n"
    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
    "while True:\n"
    " Path('/workspace/agent-heartbeat').write_text(str(i)); "
    "i+=1; time.sleep(.05)\n"
)
PARENT = (
    "import subprocess,sys,time; "
    f"subprocess.Popen([sys.executable,'-c',{CHILD!r}],start_new_session=True); "
    "time.sleep(300)"
)

def assert_stopped(container_id):
    client = docker.from_env()
    try:
        try:
            info = client.api.inspect_container(container_id)
        except docker.errors.NotFound:
            return
        assert info["State"]["Running"] is False
    finally:
        client.close()

@pytest.mark.parametrize("mode", ["normal", "timeout", "cancel"])
async def test_agent_watchdog(tmp_path, mode):
    executor = IsolatedDockerCodeExecutor(
        image="agentic-eval-sandbox:latest",
        work_dir=tmp_path,
        timeout=2 if mode == "timeout" else 30,
    )
    token = CancellationToken()
    await executor.start()
    code = "import sys; print('ready'); sys.exit(7)" if mode == "normal" else PARENT
    task = asyncio.create_task(executor.execute_code_blocks(
        [CodeBlock(language="python", code=code)], token,
    ))
    try:
        heartbeat = tmp_path / "agent-heartbeat"
        if mode == "cancel":
            expires = time.monotonic() + 10
            while not heartbeat.exists() and time.monotonic() < expires:
                await asyncio.sleep(.05)
            assert heartbeat.exists(), "Child did not start"
            token.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=3)
        else:
            result = await task
            if mode == "normal":
                assert result.exit_code == 7
                assert "ready" in result.output
                assert executor.command_events == []
                return
            assert result.exit_code == 124, result.output

        event = executor.command_events[-1]
        expected = "command_cancelled" if mode == "cancel" else "command_timeout"
        assert event["kind"] == expected
        assert event["route"] == "agent"
        assert event["termination"] == "succeeded"
        if mode == "timeout":
            assert event["limit_seconds"] == 2
            assert 2 <= event["termination_requested_seconds"] <= 3
            assert event["termination_completed_seconds"] <= 3
        assert_stopped(event["container_id"])

        before = heartbeat.read_text()
        await asyncio.sleep(.3)
        assert heartbeat.read_text() == before, "Detached child survived"

        with pytest.raises(RuntimeError, match="closed"):
            await executor.execute_code_blocks(
                [CodeBlock(language="python",
                           code="open('/workspace/should-not-run','w').close()")],
                CancellationToken(),
            )
        assert not (tmp_path / "should-not-run").exists()
    finally:
        token.cancel()
        await executor.stop()
        await asyncio.gather(task, return_exceptions=True)

    assert executor.command_events[-1]["cleanup"] == "succeeded"

def test_timeout_request_cannot_raise_cap(tmp_path):
    executor = IsolatedDockerCodeExecutor(
        image="agentic-eval-sandbox:latest",
        work_dir=tmp_path,
        timeout=300,
    )
    assert executor.timeout == 60
