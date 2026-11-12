"""SRS 1.3: kernel quota checks through both execution paths."""
import json
import shlex
import pytest

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from graders.base import DockerSandboxRunner
from harness.executor import IsolatedDockerCodeExecutor

PROBE = (
    "import json; from pathlib import Path; "
    "print('SRS13=' + json.dumps({name: "
    "Path('/sys/fs/cgroup', name).read_text().strip() "
    "for name in ['cpu.max', 'memory.max', 'pids.max']}))"
)

def check_limits(output):
    lines = [s for s in output.splitlines() if s.startswith("SRS13=")]
    assert len(lines) == 1, output
    values = json.loads(lines[0].split("=", 1)[1])
    quota, period = values["cpu.max"].split()
    assert quota != "max", values
    assert 0 < int(quota) <= 2 * int(period), values
    assert 0 < int(values["memory.max"]) <= 2_000_000_000, values
    assert 0 < int(values["pids.max"]) <= 128, values

@pytest.mark.parametrize("network_mode", ["none", None])
async def test_executor_kernel_limits(tmp_path, network_mode):
    executor = IsolatedDockerCodeExecutor(
        image="agentic-eval-sandbox:latest",
        work_dir=tmp_path,
        network_mode=network_mode,
        timeout=30,
    )
    await executor.start()
    try:
        result = await executor.execute_code_blocks(
            [CodeBlock(language="python", code=PROBE)],
            cancellation_token=CancellationToken(),
        )
        assert result.exit_code == 0, result.output
        check_limits(result.output)
    finally:
        await executor.stop()

def test_grader_kernel_limits(tmp_path):
    result = DockerSandboxRunner(workspace=tmp_path).run(
        "python -c " + shlex.quote(PROBE), timeout=30
    )
    assert result.exit_code == 0, result.output
    check_limits(result.output)
