"""Configuration loading for Cipher.

Reads settings from environment variables, loading a local .env file first
(if present) without overriding any variable already set in the real
environment. No third-party .env parser — the format needed is trivial
(KEY=VALUE lines).
"""

import os
from pathlib import Path

from pydantic import BaseModel, ValidationError

DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


class Settings(BaseModel):
    openrouter_api_key: str
    model: str = DEFAULT_MODEL


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def load_settings() -> Settings:
    _load_dotenv(Path.cwd() / ".env")

    try:
        return Settings(
            openrouter_api_key=os.environ["OPENROUTER_API_KEY"],
            model=os.environ.get("CIPHER_MODEL", DEFAULT_MODEL),
        )
    except KeyError as e:
        raise ConfigError(
            f"Missing required environment variable: {e}. "
            "Set OPENROUTER_API_KEY in your .env file or environment."
        ) from e
    except ValidationError as e:
        raise ConfigError(f"Invalid configuration: {e}") from e
