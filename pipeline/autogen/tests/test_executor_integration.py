"""Phase 1 integration test: AutoGen must be able to drive the sandbox image.

Phase 3 binds the UserProxyAgent to DockerCommandLineCodeExecutor. If that
executor cannot start our custom image or mount a workspace, the whole
orchestration layer is built on sand -- so it is verified here, before any
agent code exists.

No LLM is involved: the executor is driven directly with code blocks.
"""

from __future__ import annotations

import subprocess

import pytest

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

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


@pytest.mark.asyncio
async def test_executor_runs_python_in_custom_image(tmp_path):
    """The executor must start our image and return code output."""
    executor = DockerCommandLineCodeExecutor(
        image=IMAGE,
        work_dir=tmp_path,
        timeout=120,
    )
    await executor.start()
    try:
        result = await executor.execute_code_blocks(
            [CodeBlock(language="python", code="print('sandbox-alive')")],
            cancellation_token=CancellationToken(),
        )
    finally:
        await executor.stop()

    assert result.exit_code == 0, result.output
    assert "sandbox-alive" in result.output


@pytest.mark.asyncio
async def test_executor_has_grading_toolchain(tmp_path):
    """The graders Phase 5 depends on must be reachable from executed code."""
    executor = DockerCommandLineCodeExecutor(
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
                    code="pytest --version && scc --version && trufflehog --version",
                )
            ],
            cancellation_token=CancellationToken(),
        )
    finally:
        await executor.stop()

    assert result.exit_code == 0, result.output
    combined = result.output.lower()
    assert "pytest" in combined
    assert "scc" in combined
    assert "trufflehog" in combined


@pytest.mark.asyncio
async def test_executor_does_not_leak_host_credentials(tmp_path, monkeypatch):
    """Agent-authored code must not be able to read host secrets.

    This is the IPI mitigation stated in brief section 2.2, tested through
    the exact path an agent would use rather than through `docker run`.
    """
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "LEAK-CANARY-VIA-EXECUTOR")

    executor = DockerCommandLineCodeExecutor(
        image=IMAGE,
        work_dir=tmp_path,
        timeout=120,
    )
    await executor.start()
    try:
        result = await executor.execute_code_blocks(
            [
                CodeBlock(
                    language="python",
                    code=(
                        "import os\n"
                        "print('KEY=' + os.environ.get('AZURE_OPENAI_API_KEY', '<unset>'))"
                    ),
                )
            ],
            cancellation_token=CancellationToken(),
        )
    finally:
        await executor.stop()

    assert result.exit_code == 0, result.output
    assert "LEAK-CANARY-VIA-EXECUTOR" not in result.output
    assert "KEY=<unset>" in result.output
