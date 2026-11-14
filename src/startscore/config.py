"""Read settings from environment variables (and an optional .env file)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_TIMEOUT = 30.0


class ConfigError(Exception):
    """Raised when a required setting is missing or invalid."""


@dataclass(frozen=True)
class Config:
    api_key: str
    model: str
    timeout: float


def load_config() -> Config:
    """Build a Config from the environment. Fails early with a clear message."""
    load_dotenv()  

    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "LLM_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    model = os.getenv("LLM_MODEL", "").strip() or DEFAULT_MODEL

    raw_timeout = os.getenv("LLM_TIMEOUT", "").strip()
    try:
        timeout = float(raw_timeout) if raw_timeout else DEFAULT_TIMEOUT
    except ValueError:
        raise ConfigError(f"LLM_TIMEOUT must be a number, got {raw_timeout!r}.")
    if timeout <= 0:
        raise ConfigError("LLM_TIMEOUT must be greater than 0.")

    return Config(api_key=api_key, model=model, timeout=timeout)