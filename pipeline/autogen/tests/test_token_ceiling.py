"""Phase 3: verify the token ceiling fires independently of the message ceiling.

The Phase 3 gate proved MaxMessageTermination works. This exercises the other
ceiling by setting an absurdly low token budget with a generous message
budget, so only TokenUsageTermination can stop the run.

Requires a live model and Docker; skipped otherwise. Costs a few hundred
tokens (fractions of a cent) on azure-dev.
"""

from __future__ import annotations

import os
import subprocess

import pytest

IMAGE = "agentic-eval-sandbox:latest"


def _live_profile_available() -> bool:
    """True only if azure-dev credentials are actually configured."""
    from harness.model_profiles import ProfileError, load_profile

    try:
        load_profile("azure-dev")
    except ProfileError:
        return False
    return True


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


pytestmark = [
    pytest.mark.skipif(
        not _docker_available(), reason=f"Docker image {IMAGE} not available"
    ),
    pytest.mark.skipif(
        not _live_profile_available(), reason="azure-dev credentials not configured"
    ),
    pytest.mark.skipif(
        os.environ.get("SKIP_LIVE_TESTS") == "1",
        reason="SKIP_LIVE_TESTS=1 set (avoids API spend)",
    ),
]


async def test_token_ceiling_terminates_the_loop(tmp_path):
    """A tiny token budget must stop the run even with messages to spare."""
    from harness.executor import IsolatedDockerCodeExecutor
    from harness.model_profiles import Limits, build_client, load_profile
    from harness.orchestrator import build_orchestration

    profile = load_profile("azure-dev")
    client = build_client(profile)

    executor = IsolatedDockerCodeExecutor(
        image=IMAGE, work_dir=tmp_path, timeout=120
    )
    await executor.start()
    try:
        orchestration = build_orchestration(
            client,
            # 20 message slots but only 50 tokens: the token ceiling is the
            # only condition that can realistically fire.
            limits=Limits(max_consecutive_auto_replies=10, max_total_tokens=50),
            code_executor=executor,
            scripted_input=[""] * 12,
        )
        result = await orchestration.run(
            "Describe the contents of /workspace in detail, file by file."
        )
    finally:
        await executor.stop()
        await client.close()

    assert result.stop_reason is not None
    # The stop reason must name the token condition, not the message one.
    assert "token" in result.stop_reason.lower(), (
        f"expected token-usage termination, got: {result.stop_reason}"
    )
