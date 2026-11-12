"""Non-root checks through both real harness execution paths."""
import json
import os
import shlex
import pytest

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from graders.base import DockerSandboxRunner
from harness.executor import IsolatedDockerCodeExecutor

PROBE = (
    "import os,json; from pathlib import Path; "
    "s=dict(line.split(':',1) for line in "
    "Path('/proc/self/status').read_text().splitlines() if ':' in line); "
    "Path('/workspace/nonroot-proof.txt').write_text('ok'); "
    "print('USERCHECK='+json.dumps({'uid':os.getuid(),'gid':os.getgid(),"
    "'caps':int(s['CapEff'].strip(),16),"
    "'nnp':int(s['NoNewPrivs'].strip())}))"
)

@pytest.mark.parametrize("route", ["grader", "executor-isolated", "executor-network"])
async def test_nonroot_and_workspace_access(tmp_path, route):
    if route == "grader":
        result = DockerSandboxRunner(workspace=tmp_path).run(
            "python -c " + shlex.quote(PROBE), timeout=30
        )
    else:
        executor = IsolatedDockerCodeExecutor(
            image="agentic-eval-sandbox:latest",
            work_dir=tmp_path,
            network_mode="none" if route == "executor-isolated" else None,
            timeout=30,
        )
        await executor.start()
        try:
            result = await executor.execute_code_blocks(
                [CodeBlock(language="python", code=PROBE)],
                cancellation_token=CancellationToken(),
            )
        finally:
            await executor.stop()

    assert result.exit_code == 0, result.output
    lines = [s for s in result.output.splitlines() if s.startswith("USERCHECK=")]
    assert len(lines) == 1, result.output
    observed = json.loads(lines[0].split("=", 1)[1])
    assert observed["uid"] == os.getuid() != 0, observed
    assert observed["gid"] == os.getgid() != 0, observed
    assert observed["caps"] == 0, observed
    assert observed["nnp"] == 1, observed
    proof = tmp_path / "nonroot-proof.txt"
    assert proof.read_text() == "ok"
    assert proof.stat().st_uid == os.getuid()
