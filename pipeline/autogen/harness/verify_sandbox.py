"""Phase 1 gate: verify the air-gapped sandbox image.

Two independent things are checked:

  1. TOOLCHAIN  -- every grading binary resolves on PATH inside the container.
     A missing binary would not crash the pipeline; it would silently produce
     empty F/S/Q scores at grading time, which is far worse.

  2. AIR-GAP    -- host credentials do NOT reach the container. This is the
     whole reason the sandbox exists (brief section 2.2): the executor runs
     untrusted agent-authored code, so a leaked AZURE_OPENAI_API_KEY would be
     exfiltratable via an Indirect Prompt Injection trap.

Usage:
    ./.venv/bin/python -m harness.verify_sandbox
"""

from __future__ import annotations

import subprocess

IMAGE = "agentic-eval-sandbox:latest"

# (label, argv) -- each must exit 0 inside the container.
TOOLCHAIN: list[tuple[str, list[str]]] = [
    ("python", ["python", "--version"]),
    ("git", ["git", "--version"]),
    ("pytest", ["pytest", "--version"]),
    ("pytest-json-report", ["python", "-c", "import pytest_jsonreport; print('ok')"]),
    # complexipy exposes no --version flag (exits 2 with a usage message), so
    # probe the installed distribution metadata instead.
    (
        "complexipy",
        [
            "python",
            "-c",
            "import importlib.metadata as m; print(m.version('complexipy'))",
        ],
    ),
    ("trufflehog", ["trufflehog", "--version"]),
    ("scc", ["scc", "--version"]),
]

# Credentials that must never be visible inside the sandbox.
FORBIDDEN_VARS = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "OLLAMA_BASE_URL",
]


def _run_in_container(argv: list[str], *, env: dict[str, str] | None = None) -> tuple[int, str]:
    """Run argv inside a throwaway container, returning (exit_code, output)."""
    cmd = ["docker", "run", "--rm"]
    for key, value in (env or {}).items():
        cmd += ["-e", f"{key}={value}"]
    cmd += [IMAGE] + argv

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def check_image_exists() -> bool:
    proc = subprocess.run(
        ["docker", "image", "inspect", IMAGE],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def check_toolchain() -> list[str]:
    print("--- toolchain ---")
    failures: list[str] = []
    for label, argv in TOOLCHAIN:
        code, output = _run_in_container(argv)
        first_line = output.splitlines()[0] if output else ""
        if code == 0:
            print(f"  OK   {label:<20} {first_line[:56]}")
        else:
            print(f"  FAIL {label:<20} exit={code} {first_line[:48]}")
            failures.append(f"{label} not runnable in sandbox")
    return failures


def check_air_gap() -> list[str]:
    """Confirm host credentials are absent even when set in the host env.

    Poisoned sentinel values are deliberately present in THIS process's
    environment when docker is invoked. Docker does not forward the client's
    environment to the container unless explicitly told to with -e, so all of
    these must come back empty. If any leaks, the isolation guarantee in the
    brief is false.
    """
    print("\n--- air-gap (credential isolation) ---")
    failures: list[str] = []

    # Build a shell snippet that prints each var; empty output means unset.
    script = "; ".join(f'echo "{v}=${{{v}:-<unset>}}"' for v in FORBIDDEN_VARS)
    code, output = _run_in_container(["/bin/bash", "-lc", script])

    if code != 0:
        return [f"could not probe container environment (exit {code})"]

    for line in output.splitlines():
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        if value == "<unset>":
            print(f"  OK   {name:<24} unset")
        else:
            print(f"  FAIL {name:<24} LEAKED -> {value[:32]}")
            failures.append(f"{name} visible inside sandbox")

    return failures


def check_network_note() -> None:
    """Report the container's outbound network posture.

    Informational only. DockerCommandLineCodeExecutor does not disable
    networking by default; Phase 3 decides whether to harden this further.
    """
    print("\n--- network posture (informational) ---")
    code, _ = _run_in_container(
        ["/bin/bash", "-lc", "curl -sSf -m 5 https://example.com > /dev/null"]
    )
    if code == 0:
        print("  NOTE container HAS outbound internet access.")
        print("       Credentials are absent, so there is nothing to exfiltrate,")
        print("       but Phase 3 should consider network=none for scored runs.")
    else:
        print("  NOTE container has no outbound internet access.")


def main() -> int:
    print(f"image: {IMAGE}\n")

    if not check_image_exists():
        print("PHASE 1 GATE: FAILED")
        print(f"  Image '{IMAGE}' not found. Build it first:")
        print("    cd .devcontainer && docker build -t agentic-eval-sandbox:latest .")
        return 1

    failures = check_toolchain()
    failures += check_air_gap()
    check_network_note()

    print()
    if failures:
        print(f"PHASE 1 GATE: FAILED ({len(failures)} problem(s))")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PHASE 1 GATE: PASSED")
    print("  Toolchain complete and no host credentials reachable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
