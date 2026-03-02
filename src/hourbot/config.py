"""Environment-driven application configuration."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    tz: str
    db_path: str
    reminder_hour: int
    reminder_minute: int
    owner_chat_id: int


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value.strip()


def _get_int_env(name: str, *, min_value: int | None = None, max_value: int | None = None) -> int:
    raw_value = _get_required_env(name)
    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc

    if min_value is not None and parsed < min_value:
        raise ValueError(f"Environment variable {name} must be >= {min_value}")
    if max_value is not None and parsed > max_value:
        raise ValueError(f"Environment variable {name} must be <= {max_value}")

    return parsed


def load_settings() -> Settings:
    """Load and validate settings from environment variables."""
    return Settings(
        bot_token=_get_required_env("BOT_TOKEN"),
        tz=_get_required_env("TZ"),
        db_path=_get_required_env("DB_PATH"),
        reminder_hour=_get_int_env("REMINDER_HOUR", min_value=0, max_value=23),
        reminder_minute=_get_int_env("REMINDER_MINUTE", min_value=0, max_value=59),
        owner_chat_id=_get_int_env("OWNER_CHAT_ID"),
    )
