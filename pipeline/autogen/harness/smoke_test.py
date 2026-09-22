"""Phase 0.5 gate: model connectivity and token-capture smoke test.

Sends a deliberately tiny prompt through the configured profile and confirms:

  1. the endpoint is reachable,
  2. the credentials / model_info are accepted,
  3. the response carries real `usage` token counts.

Point 3 matters: T (token efficiency) and the 15,000-token ceiling are both
computed from `usage`. Some local servers return zeroed or absent counts, in
which case those metrics are meaningless and we need to know now, not at
scoring time.

Usage:
    ./.venv/bin/python -m harness.smoke_test --model-profile local-dev
"""

from __future__ import annotations

import argparse
import asyncio
import time

from autogen_core.models import UserMessage

from harness.model_profiles import ProfileError, build_client, load_profile

PROMPT = "Reply with exactly: OK"


async def run(profile_name: str | None) -> int:
    try:
        profile = load_profile(profile_name)
    except ProfileError as exc:
        print(f"PHASE 0.5 GATE: FAILED\n  {exc}")
        return 1

    print(f"profile         : {profile.name}")
    print(f"label           : {profile.label}")
    print(f"provider        : {profile.provider}")
    print(f"benchmark_valid : {profile.benchmark_valid}")
    if not profile.benchmark_valid:
        print("  note: plumbing validation only; not valid for scored runs.")
    print()

    try:
        client = build_client(profile)
    except ProfileError as exc:
        print(f"PHASE 0.5 GATE: FAILED\n  {exc}")
        return 1

    started = time.monotonic()
    try:
        result = await client.create([UserMessage(content=PROMPT, source="user")])
    except Exception as exc:  # noqa: BLE001 - surface the real transport error
        print("PHASE 0.5 GATE: FAILED")
        print(f"  Could not reach the model: {type(exc).__name__}: {exc}")
        print()
        print("  Checks:")
        print("   - Is the Ollama host reachable from this machine?")
        print("   - Is OLLAMA_BASE_URL in .env the LAN address (not 127.0.0.1)?")
        print("   - Has the model been pulled on the serving machine?")
        return 1
    finally:
        await client.close()

    latency = time.monotonic() - started
    usage = result.usage

    print(f"response        : {str(result.content).strip()[:80]}")
    print(f"latency_seconds : {latency:.2f}")
    print(f"prompt_tokens   : {usage.prompt_tokens}")
    print(f"completion_tokens: {usage.completion_tokens}")
    print()

    total = (usage.prompt_tokens or 0) + (usage.completion_tokens or 0)
    if total == 0:
        print("PHASE 0.5 GATE: FAILED")
        print("  Endpoint reachable, but reported ZERO tokens.")
        print("  T (token efficiency) and the 15k ceiling cannot be computed")
        print("  from this backend without a tokenizer-based fallback.")
        return 1

    print("PHASE 0.5 GATE: PASSED")
    print(f"  Endpoint reachable and reporting real token usage ({total} total).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model-profile",
        dest="model_profile",
        default=None,
        help="Profile name from config/models.yaml (default: MODEL_PROFILE or default_profile).",
    )
    args = parser.parse_args()
    return asyncio.run(run(args.model_profile))


if __name__ == "__main__":
    raise SystemExit(main())
