"""Phase 3 tests for network isolation. Requires Docker; no LLM."""

from __future__ import annotations

import subprocess

import pytest

from harness.executor import IsolatedDockerCodeExecutor, probe_network

IMAGE = "agentic-eval-sandbox:latest"


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


pytestmark = pytest.mark.skipif(
    not _docker_available(),
    reason=f"Docker image {IMAGE} not available",
)


async def test_isolated_executor_has_no_network(tmp_path):
    """The IPI egress vector must be closed when isolation is on."""
    executor = IsolatedDockerCodeExecutor(
        image=IMAGE,
        work_dir=tmp_path,
        timeout=120,
        network_mode="none",
    )
    await executor.start()
    try:
        assert await probe_network(executor) is False
    finally:
        await executor.stop()


async def test_default_is_isolated(tmp_path):
    """Isolation must be opt-OUT, not opt-in: the safe default wins."""
    executor = IsolatedDockerCodeExecutor(image=IMAGE, work_dir=tmp_path, timeout=120)
    assert executor.network_mode == "none"

    await executor.start()
    try:
        assert await probe_network(executor) is False
    finally:
        await executor.stop()


async def test_network_can_be_re_enabled(tmp_path):
    """Tasks needing `npm install` must still be runnable."""
    executor = IsolatedDockerCodeExecutor(
        image=IMAGE,
        work_dir=tmp_path,
        timeout=120,
        network_mode=None,
    )
    await executor.start()
    try:
        assert await probe_network(executor) is True
    finally:
        await executor.stop()


async def test_isolation_does_not_break_code_execution(tmp_path):
    """Severing the network must not break local test/grader execution."""
    from autogen_core import CancellationToken
    from autogen_core.code_executor import CodeBlock

    executor = IsolatedDockerCodeExecutor(
        image=IMAGE,
        work_dir=tmp_path,
        timeout=120,
    )
    await executor.start()
    try:
        result = await executor.execute_code_blocks(
            [
                CodeBlock(
                    language="bash",
                    code="pytest --version && scc --version && echo GRADERS_OK",
                )
            ],
            cancellation_token=CancellationToken(),
        )
    finally:
        await executor.stop()

    assert result.exit_code == 0, result.output
    assert "GRADERS_OK" in result.output
