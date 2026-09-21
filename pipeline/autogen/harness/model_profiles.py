"""Model provider profile loading.

Builds an AutoGen v0.4 chat completion client from a named profile in
`config/models.yaml`. The agent layer stays provider-agnostic: it receives a
constructed client and never learns which backend is behind it.

Secrets live only in the host `.env`; the YAML carries `${VAR}` placeholders
that are resolved here at load time.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "models.yaml"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

_PLACEHOLDER = re.compile(r"\$\{([A-Z0-9_]+)\}")

# Sentinel distinguishing "caller passed nothing" from an explicit None,
# which means "do not load any .env at all".
_USE_DEFAULT_ENV = Path("__use_default_env__")


class ProfileError(RuntimeError):
    """Raised when a profile is missing, malformed, or missing credentials."""


@dataclass(frozen=True)
class Limits:
    """Resource ceilings from the project brief, section 4."""

    max_consecutive_auto_replies: int
    max_total_tokens: int


@dataclass(frozen=True)
class ModelProfile:
    """A resolved provider profile, ready to build a client from."""

    name: str
    label: str
    provider: str
    model: str
    benchmark_valid: bool
    settings: dict[str, Any]
    limits: Limits


def _expand(value: Any, *, missing: set[str]) -> Any:
    """Recursively resolve ${VAR} placeholders against the environment.

    Unresolved names are accumulated into `missing` rather than raised
    immediately, so the caller can report every absent variable in one pass
    instead of making the user fix them one at a time.
    """
    if isinstance(value, dict):
        return {k: _expand(v, missing=missing) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(v, missing=missing) for v in value]
    if not isinstance(value, str):
        return value

    def substitute(match: re.Match[str]) -> str:
        var = match.group(1)
        resolved = os.environ.get(var)
        if not resolved:
            missing.add(var)
            return ""
        return resolved

    return _PLACEHOLDER.sub(substitute, value)


def load_profile(
    name: str | None = None,
    *,
    config_path: Path | None = None,
    env_path: Path | None = _USE_DEFAULT_ENV,
) -> ModelProfile:
    """Load and resolve a single profile by name.

    Falls back to MODEL_PROFILE in the environment, then to the YAML's
    `default_profile`.

    `env_path` defaults to the host `.env`. Pass `None` to skip dotenv loading
    entirely — tests rely on this so that a developer's local `.env` (which may
    hold placeholder Azure values) cannot leak in and mask a real failure.
    """
    if env_path is _USE_DEFAULT_ENV:
        env_path = ENV_PATH
    if env_path is not None and env_path.exists():
        load_dotenv(env_path)

    path = config_path or CONFIG_PATH
    if not path.exists():
        raise ProfileError(f"Model config not found at {path}")

    raw = yaml.safe_load(path.read_text())
    profiles = raw.get("profiles") or {}

    selected = name or os.environ.get("MODEL_PROFILE") or raw.get("default_profile")
    if not selected:
        raise ProfileError("No profile requested and no default_profile set.")
    if selected not in profiles:
        available = ", ".join(sorted(profiles))
        raise ProfileError(f"Unknown profile '{selected}'. Available: {available}")

    # Only expand the selected profile: an unused azure-prod block must not
    # force Azure credentials to exist during local-dev runs.
    missing: set[str] = set()
    entry = _expand(profiles[selected], missing=missing)
    if missing:
        raise ProfileError(
            f"Profile '{selected}' needs environment variable(s) "
            f"{', '.join(sorted(missing))}. "
            f"Copy .env.example to .env and fill them in."
        )

    limits_raw = raw.get("limits") or {}
    limits = Limits(
        max_consecutive_auto_replies=int(limits_raw.get("max_consecutive_auto_replies", 5)),
        max_total_tokens=int(limits_raw.get("max_total_tokens", 15000)),
    )

    settings = {
        k: v
        for k, v in entry.items()
        if k not in {"label", "provider", "model", "benchmark_valid"}
    }

    return ModelProfile(
        name=selected,
        label=entry["label"],
        provider=entry["provider"],
        model=entry["model"],
        benchmark_valid=bool(entry.get("benchmark_valid", False)),
        settings=settings,
        limits=limits,
    )


def build_client(profile: ModelProfile):
    """Construct the AutoGen v0.4 chat completion client for a profile.

    Imported lazily so that config parsing can be tested without the full
    AutoGen runtime loaded.
    """
    from autogen_core.models import ModelInfo

    settings = dict(profile.settings)
    extra_args = settings.pop("extra_args", None) or {}
    model_info_raw = settings.pop("model_info", None)

    if profile.provider == "openai-compatible":
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        if not model_info_raw:
            # AutoGen v0.4 refuses to build a non-OpenAI model client without
            # an explicit capability declaration.
            raise ProfileError(
                f"Profile '{profile.name}' is openai-compatible and must "
                f"declare a model_info block."
            )
        return OpenAIChatCompletionClient(
            model=profile.model,
            base_url=settings["base_url"],
            api_key=settings.get("api_key", "not-needed"),
            model_info=ModelInfo(**model_info_raw),
            **extra_args,
        )

    if profile.provider == "azure-openai":
        from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

        kwargs: dict[str, Any] = {
            "model": profile.model,
            "azure_endpoint": settings["azure_endpoint"],
            "azure_deployment": settings["azure_deployment"],
            "api_version": settings["api_version"],
            "api_key": settings["api_key"],
        }
        if model_info_raw:
            kwargs["model_info"] = ModelInfo(**model_info_raw)
        return AzureOpenAIChatCompletionClient(**kwargs, **extra_args)

    raise ProfileError(f"Unsupported provider '{profile.provider}' in profile '{profile.name}'.")
