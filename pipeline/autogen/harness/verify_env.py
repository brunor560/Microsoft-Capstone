"""Phase 0 gate: verify the orchestration host dependency stack.

Confirms that every required package imports on this interpreter and that the
AutoGen v0.4+ API surface the pipeline depends on actually exists. Run:

    ./.venv/bin/python -m harness.verify_env
"""

from __future__ import annotations

import importlib
import sys

# (import path, human label) for top-level package availability.
PACKAGES: list[tuple[str, str]] = [
    ("autogen_agentchat", "autogen-agentchat"),
    ("autogen_core", "autogen-core"),
    ("autogen_ext", "autogen-ext"),
    ("litellm", "litellm"),
    ("opentelemetry.sdk", "opentelemetry-sdk"),
    ("yaml", "pyyaml"),
    ("dotenv", "python-dotenv"),
    ("docker", "docker"),
]

# (module, attribute) pairs the pipeline binds to directly. These are the v0.4
# symbols that would silently differ if the resolved version drifted to v0.2.
API_SURFACE: list[tuple[str, str]] = [
    ("autogen_agentchat.agents", "AssistantAgent"),
    ("autogen_agentchat.agents", "UserProxyAgent"),
    ("autogen_agentchat.conditions", "MaxMessageTermination"),
    ("autogen_agentchat.conditions", "TokenUsageTermination"),
    ("autogen_ext.code_executors.docker", "DockerCommandLineCodeExecutor"),
    ("autogen_ext.models.openai", "OpenAIChatCompletionClient"),
    ("autogen_ext.models.openai", "AzureOpenAIChatCompletionClient"),
    ("autogen_core.models", "ModelInfo"),
]


def main() -> int:
    failures: list[str] = []

    print(f"python              : {sys.version.split()[0]}")
    print("\n--- packages ---")
    for module_path, label in PACKAGES:
        try:
            module = importlib.import_module(module_path)
        except Exception as exc:  # noqa: BLE001 - report, do not mask
            failures.append(f"import {module_path}: {exc}")
            print(f"  FAIL {label}: {exc}")
            continue
        version = getattr(module, "__version__", "n/a")
        print(f"  OK   {label} {version}")

    print("\n--- AutoGen v0.4 API surface ---")
    for module_path, attribute in API_SURFACE:
        try:
            module = importlib.import_module(module_path)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"import {module_path}: {exc}")
            print(f"  FAIL {module_path}.{attribute}: {exc}")
            continue
        if hasattr(module, attribute):
            print(f"  OK   {module_path}.{attribute}")
        else:
            failures.append(f"missing {module_path}.{attribute}")
            print(f"  FAIL {module_path}.{attribute} not found")

    print()
    if failures:
        print(f"PHASE 0 GATE: FAILED ({len(failures)} problem(s))")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PHASE 0 GATE: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
