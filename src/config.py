from __future__ import annotations

from pathlib import Path
from typing import Any

SECRET_FIELD_NAMES = {
    "qq_client_secret",
    "qq_bot_secret",
    "ai_api_key",
}


try:
    from pydantic import field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

        host: str = "0.0.0.0"
        port: int = 8088

        qq_app_id: str = ""
        qq_client_secret: str = ""
        qq_bot_secret: str = ""
        qq_api_base_url: str = "https://api.sgroup.qq.com"
        qq_token_url: str = "https://bots.qq.com/app/getAppAccessToken"
        qq_webhook_path: str = "/qq/callback"

        ai_api_key: str = ""
        ai_base_url: str = "https://api.x.ai/v1"
        ai_model: str = "grok-4.3"
        ai_api_style: str = "responses"
        ai_temperature: float = 0.7
        ai_max_tokens: int = 1200
        ai_timeout_seconds: int = 60

        bot_persona_file: Path = Path("./persona/default.md")

        database_url: str = "sqlite+aiosqlite:///./data/bot.db"
        max_history_messages: int = 20
        max_memory_items: int = 12
        max_reply_chars: int = 1800

        memory_enabled: bool = True
        memory_extract_enabled: bool = True
        memory_min_importance: int = 3
        emotion_enabled: bool = True

        @field_validator("ai_api_style")
        @classmethod
        def validate_ai_api_style(cls, value: str) -> str:
            if value not in {"responses", "chat_completions"}:
                raise ValueError("AI_API_STYLE must be responses or chat_completions")
            return value

        def redacted_dict(self) -> dict[str, Any]:
            data = self.model_dump()
            for field_name in SECRET_FIELD_NAMES:
                if data.get(field_name):
                    data[field_name] = "***"
            return data

except ImportError:

    class Settings:
        def __init__(self, _env_file: str | None = ".env", **kwargs: Any) -> None:
            defaults = {
                "host": "0.0.0.0",
                "port": 8088,
                "qq_app_id": "",
                "qq_client_secret": "",
                "qq_bot_secret": "",
                "qq_api_base_url": "https://api.sgroup.qq.com",
                "qq_token_url": "https://bots.qq.com/app/getAppAccessToken",
                "qq_webhook_path": "/qq/callback",
                "ai_api_key": "",
                "ai_base_url": "https://api.x.ai/v1",
                "ai_model": "grok-4.3",
                "ai_api_style": "responses",
                "ai_temperature": 0.7,
                "ai_max_tokens": 1200,
                "ai_timeout_seconds": 60,
                "bot_persona_file": Path("./persona/default.md"),
                "database_url": "sqlite+aiosqlite:///./data/bot.db",
                "max_history_messages": 20,
                "max_memory_items": 12,
                "max_reply_chars": 1800,
                "memory_enabled": True,
                "memory_extract_enabled": True,
                "memory_min_importance": 3,
                "emotion_enabled": True,
            }
            defaults.update(kwargs)
            for key, value in defaults.items():
                setattr(self, key, value)

        def redacted_dict(self) -> dict[str, Any]:
            data = self.__dict__.copy()
            data.pop("_env_file", None)
            for field_name in SECRET_FIELD_NAMES:
                if data.get(field_name):
                    data[field_name] = "***"
            return data
