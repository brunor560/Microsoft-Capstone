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
from harness.nonroot import create_nonroot
from harness.deadline import run_with_deadline, terminate_verified, remove_verified

from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor


class IsolatedDockerCodeExecutor(DockerCommandLineCodeExecutor):
    """A DockerCommandLineCodeExecutor with configurable network isolation.

    Set `network_mode="none"` (the default) to sever outbound networking.
    Pass `network_mode=None` to keep upstream's default bridge behaviour.
    """

    def __init__(self, *args, network_mode: str | None = "none", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._network_mode = network_mode
        self._timeout = min(self._timeout, 60)
        self.command_events = []
        self._execution_closed = False
        # Host cleanup owns container removal.
        self._auto_remove = False

    async def start(self) -> None:
        """Start the container, applying network isolation.

        Upstream's `start()` calls `client.containers.create(...)` without a
        `network_mode` argument. Rather than reimplement the whole method
        (and risk drifting from upstream on version bumps), we patch the
        docker SDK's create call for the duration of the parent's start.
        """
        import docker

        original_create = docker.models.containers.ContainerCollection.create
        network_mode = self._network_mode

        def create_with_network(self_collection, image, command=None, **kwargs):
            if network_mode is not None:
                kwargs["network_mode"] = network_mode
            # SRS 1.3: quotas apply even when networking is enabled.
            kwargs.update(
                cpu_period=100_000,
                cpu_quota=200_000,
                mem_limit=2_000_000_000,
                memswap_limit=2_000_000_000,
                pids_limit=128,
            )
            return create_nonroot(original_create, self_collection, image, command, kwargs)

        docker.models.containers.ContainerCollection.create = create_with_network
        try:
            await super().start()
        finally:
            docker.models.containers.ContainerCollection.create = original_create

    async def _execute_command(self, command, cancellation_token):
        if self._execution_closed:
            raise RuntimeError("Sandbox executor is closed after timeout or cancellation")
        if self._container is None or not self._running:
            raise RuntimeError("Sandbox container is not running")
        if cancellation_token.is_cancelled():
            raise asyncio.CancelledError()

        # AutoGen adds GNU timeout; the host watchdog owns this deadline.
        if len(command) >= 3 and command[0] == "timeout":
            command = command[2:]

        container = self._container
        first_event = len(self.command_events)
        task = asyncio.create_task(asyncio.to_thread(
            run_with_deadline, container, command,
            self._timeout, self.command_events,
        ))
        cancellation_token.link_future(task)
        try:
            result = await task
        except asyncio.CancelledError:
            self._execution_closed = True
            event = {
                "kind": "command_cancelled", "route": "agent",
                "container_id": container.id, "cleanup": "pending",
            }
            self.command_events.append(event)
            try:
                await asyncio.to_thread(
                    terminate_verified,
                    container.id, container.client.api._version,
                )
                event["termination"] = "succeeded"
            except Exception as exc:
                event["termination"] = "failed"
                raise RuntimeError(
                    "Cancellation termination failed; infrastructure error"
                ) from exc
            raise
        except Exception:
            self._execution_closed = True
            raise
        finally:
            for event in self.command_events[first_event:]:
                event.setdefault("route", "agent")

        if len(self.command_events) > first_event:
            self._execution_closed = True
        return result.stdout + result.stderr, result.exit_code

    async def stop(self):
        container = self._container
        if container is not None:
            event = next(
                (e for e in reversed(self.command_events)
                 if e["container_id"] == container.id),
                None,
            )
            try:
                await asyncio.to_thread(
                    remove_verified,
                    container.id, container.client.api._version,
                )
            except Exception:
                if event is not None:
                    event["cleanup"] = "failed"
                raise
            else:
                if event is not None:
                    event["cleanup"] = "succeeded"
        self._running = False
        self._container = None
        await super().stop()

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
