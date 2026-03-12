from __future__ import annotations

from functools import lru_cache
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigError(ValueError):
    """Raised when environment-based configuration is invalid."""


class AppConfig(BaseSettings):
    model_name: str = Field(default="gpt-5-nano", validation_alias="AGENT_MODEL", min_length=1)
    temperature: float = Field(default=0.7, validation_alias="AGENT_TEMPERATURE", ge=0.0, le=2.0)
    web_search_enabled: bool = Field(default=True, validation_alias="ENABLE_WEB_SEARCH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
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


@lru_cache(maxsize=1)
def load_config() -> AppConfig:
    return AppConfig()


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
