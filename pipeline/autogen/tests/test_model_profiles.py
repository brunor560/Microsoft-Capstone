"""Phase 0 tests for the model provider profile layer.

These run entirely offline: no LLM, no Docker, no network.
"""

from __future__ import annotations

import pytest

from harness import model_profiles
from harness.model_profiles import ProfileError

AZURE_VARS = (
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT",
    "AZURE_OPENAI_API_VERSION",
)


def load_profile(name=None):
    """Load a profile with dotenv disabled.

    The developer's local `.env` holds placeholder Azure values; letting it
    load would mask genuine "missing credential" failures and make these
    tests pass or fail depending on whose machine they run on.
    """
    return model_profiles.load_profile(name, env_path=None)


@pytest.fixture
def no_azure_env(monkeypatch):
    """Simulate a host that has never configured Azure credentials."""
    for var in AZURE_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    return monkeypatch


def test_local_dev_resolves_without_azure_credentials(no_azure_env):
    """Selecting local-dev must not require Azure secrets to exist."""
    profile = load_profile("local-dev")

    assert profile.name == "local-dev"
    assert profile.provider == "openai-compatible"
    assert profile.model == "qwen3:8b"
    assert profile.settings["base_url"] == "http://127.0.0.1:11434/v1"


def test_local_dev_is_not_benchmark_valid(no_azure_env):
    """qwen3:8b is plumbing validation only and must never score a benchmark."""
    assert load_profile("local-dev").benchmark_valid is False


def test_local_dev_disables_qwen_thinking_mode(no_azure_env):
    """Reasoning tokens would inflate counts against the 15k ceiling."""
    profile = load_profile("local-dev")
    kwargs = profile.settings["extra_args"]["chat_template_kwargs"]
    assert kwargs["enable_thinking"] is False


def test_local_dev_declares_model_info(no_azure_env):
    """AutoGen v0.4 refuses non-OpenAI clients that omit model_info."""
    info = load_profile("local-dev").settings["model_info"]
    assert info["function_calling"] is True
    assert info["vision"] is False


def test_limits_match_project_brief(no_azure_env):
    """Section 4: 5 consecutive auto-replies, 15,000 total tokens."""
    limits = load_profile("local-dev").limits
    assert limits.max_consecutive_auto_replies == 5
    assert limits.max_total_tokens == 15000


def test_azure_profile_fails_loudly_without_credentials(no_azure_env):
    """A missing key must raise, never silently resolve to an empty string.

    All absent variables are reported in one pass so the user is not forced
    to fix them one re-run at a time.
    """
    with pytest.raises(ProfileError) as excinfo:
        load_profile("azure-prod")

    message = str(excinfo.value)
    for var in AZURE_VARS:
        assert var in message, f"{var} missing from error message"


def test_unknown_profile_is_rejected(no_azure_env):
    with pytest.raises(ProfileError) as excinfo:
        load_profile("does-not-exist")
    assert "Unknown profile" in str(excinfo.value)


def test_azure_profile_resolves_when_credentials_present(no_azure_env):
    """The profile swap must work with zero code change."""
    no_azure_env.setenv("AZURE_OPENAI_API_KEY", "fake-key-for-test")
    no_azure_env.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    no_azure_env.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-test")
    no_azure_env.setenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

    profile = load_profile("azure-prod")

    assert profile.provider == "azure-openai"
    assert profile.benchmark_valid is True
    assert profile.model == "gpt-4o-test"
    # The label is stamped into telemetry so runs are never confused.
    assert profile.label == "azure/gpt-4o-test"
