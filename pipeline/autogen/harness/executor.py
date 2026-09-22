"""Network-isolated code executor (project brief, section 2.2).

`DockerCommandLineCodeExecutor` does not expose Docker's `network_mode`, so
its containers inherit the default bridge network and have full outbound
internet access. The Phase 1 gate confirmed this empirically.

For scored runs that is the last remaining exfiltration vector: the sandbox
holds no credentials, but an Indirect Prompt Injection trap could still make
agent-authored code POST workspace contents to an attacker-controlled host.

`IsolatedDockerCodeExecutor` closes it by creating the container with
`network_mode="none"`.

TRADE-OFF: with networking disabled, `npm install` / `pip install` fail. Tasks
that need to resolve dependencies must either run with isolation off or use an
image that already contains them. Choose per run via
`run_benchmark.py --network`.
"""

from __future__ import annotations

import asyncio

from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor


class IsolatedDockerCodeExecutor(DockerCommandLineCodeExecutor):
    """A DockerCommandLineCodeExecutor with configurable network isolation.

    Set `network_mode="none"` (the default) to sever outbound networking.
    Pass `network_mode=None` to keep upstream's default bridge behaviour.
    """

    def __init__(self, *args, network_mode: str | None = "none", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._network_mode = network_mode

    async def start(self) -> None:
        """Start the container, applying network isolation.

        Upstream's `start()` calls `client.containers.create(...)` without a
        `network_mode` argument. Rather than reimplement the whole method
        (and risk drifting from upstream on version bumps), we patch the
        docker SDK's create call for the duration of the parent's start.
        """
        if self._network_mode is None:
            await super().start()
            return

        import docker

        original_create = docker.models.containers.ContainerCollection.create
        network_mode = self._network_mode

        def create_with_network(self_collection, image, command=None, **kwargs):
            kwargs.setdefault("network_mode", network_mode)
            return original_create(self_collection, image, command, **kwargs)

        docker.models.containers.ContainerCollection.create = create_with_network
        try:
            await super().start()
        finally:
            docker.models.containers.ContainerCollection.create = original_create

    @property
    def network_mode(self) -> str | None:
        return self._network_mode


async def probe_network(executor: DockerCommandLineCodeExecutor) -> bool:
    """Return True if the executor's container can reach the internet.

    Used by the Phase 3 gate to prove isolation is real rather than assumed.
    """
    from autogen_core import CancellationToken
    from autogen_core.code_executor import CodeBlock

    result = await executor.execute_code_blocks(
        [
            CodeBlock(
                language="bash",
                code="curl -sSf -m 5 https://example.com > /dev/null && echo ONLINE || echo OFFLINE",
            )
        ],
        cancellation_token=CancellationToken(),
    )
    return "ONLINE" in result.output


__all__ = ["IsolatedDockerCodeExecutor", "probe_network", "asyncio"]
