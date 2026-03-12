from __future__ import annotations

import os
from dataclasses import dataclass


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


class ConfigError(ValueError):
    """Raised when environment-based configuration is invalid."""


@dataclass(frozen=True)
class AppConfig:
    model_name: str
    temperature: float
    web_search_enabled: bool


def _read_float_env(
    name: str,
    default: float,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default

    try:
        parsed_value = float(raw_value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number. Received: {raw_value!r}") from exc

    if min_value is not None and parsed_value < min_value:
        raise ConfigError(f"{name} must be >= {min_value}. Received: {parsed_value}")
    if max_value is not None and parsed_value > max_value:
        raise ConfigError(f"{name} must be <= {max_value}. Received: {parsed_value}")
    return parsed_value


def _read_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default

    normalized = raw_value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ConfigError(
        f"{name} must be a boolean value ({sorted(TRUE_VALUES | FALSE_VALUES)}). Received: {raw_value!r}"
    )


def _required_env_for_model(model_name: str) -> tuple[str, ...]:
    normalized = model_name.strip().lower()

    if ":" in normalized:
        provider_prefix = normalized.split(":", 1)[0]
        if provider_prefix == "openai":
            return ("OPENAI_API_KEY",)
        if provider_prefix == "anthropic":
            return ("ANTHROPIC_API_KEY",)
        if provider_prefix in {"google", "google_genai"}:
            return ("GOOGLE_API_KEY",)
        if provider_prefix in {"vertexai", "google_vertexai"}:
            return ("GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS")
        if provider_prefix == "ollama":
            return ()

    if normalized.startswith(("gpt-", "o1", "o3", "o4")):
        return ("OPENAI_API_KEY",)
    if normalized.startswith("claude"):
        return ("ANTHROPIC_API_KEY",)
    if normalized.startswith("gemini"):
        return ("GOOGLE_API_KEY",)
    return ()


def load_config() -> AppConfig:
    model_name = os.getenv("AGENT_MODEL", "gpt-5-nano").strip() or "gpt-5-nano"
    temperature = _read_float_env("AGENT_TEMPERATURE", default=0.7, min_value=0.0, max_value=2.0)
    web_search_enabled = _read_bool_env("ENABLE_WEB_SEARCH", default=True)

    return AppConfig(
        model_name=model_name,
        temperature=temperature,
        web_search_enabled=web_search_enabled,
    )


def validate_runtime_config(config: AppConfig) -> list[str]:
    required_env = _required_env_for_model(config.model_name)
    if required_env:
        has_required_env = any(os.getenv(var_name, "").strip() for var_name in required_env)
        if not has_required_env:
            expected = " or ".join(required_env)
            raise ConfigError(
                f"Model {config.model_name!r} requires {expected}. Set it in your environment or .env file."
            )

    warnings: list[str] = []
    if config.web_search_enabled and not os.getenv("TAVILY_API_KEY", "").strip():
        warnings.append(
            "ENABLE_WEB_SEARCH is true but TAVILY_API_KEY is missing; web_search will return an error until it is set."
        )
    return warnings
