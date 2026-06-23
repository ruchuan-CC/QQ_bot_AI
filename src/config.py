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
        public_base_url: str = "https://your-domain.com"

        qq_app_id: str = ""
        qq_client_secret: str = ""
        qq_bot_secret: str = ""
        qq_api_base_url: str = "https://api.sgroup.qq.com"
        qq_token_url: str = "https://bots.qq.com/app/getAppAccessToken"
        qq_event_mode: str = "webhook"
        qq_webhook_path: str = "/qq/callback"
        qq_enable_websocket: bool = False
        qq_enable_c2c: bool = True
        qq_enable_group: bool = False
        qq_enable_guild: bool = False

        ai_provider: str = "xai"
        ai_api_key: str = ""
        ai_base_url: str = "https://api.x.ai/v1"
        ai_model: str = "grok-4.3"
        ai_temperature: float = 0.7
        ai_max_tokens: int = 1200
        ai_timeout_seconds: int = 60

        bot_name: str = "希恩X"
        bot_persona_file: Path = Path("./persona/default.md")
        bot_language: str = "zh-CN"
        admin_openids: str = ""

        database_url: str = "sqlite+aiosqlite:///./data/bot.db"
        max_history_messages: int = 20
        max_memory_items: int = 12
        max_reply_chars: int = 1800

        memory_enabled: bool = True
        memory_extract_enabled: bool = True
        memory_min_importance: int = 3
        emotion_enabled: bool = True

        proactive_enabled: bool = False
        proactive_require_user_opt_in: bool = True
        proactive_scan_interval_seconds: int = 300
        proactive_max_per_user_per_month: int = 4
        proactive_min_interval_hours: int = 24
        wakeup_enabled: bool = True
        wakeup_respect_official_periods: bool = True
        default_quiet_hours_start: str = "23:30"
        default_quiet_hours_end: str = "08:30"
        auto_delete_user_data_on_friend_del: bool = False

        assets_enabled: bool = True
        assets_dir: Path = Path("./assets")
        asset_public_base_url: str = "https://your-domain.com/assets"
        asset_send_probability: float = 0.25

        log_level: str = "INFO"
        log_dir: Path = Path("./logs")

        @field_validator("qq_event_mode")
        @classmethod
        def validate_event_mode(cls, value: str) -> str:
            if value not in {"webhook", "websocket"}:
                raise ValueError("QQ_EVENT_MODE must be webhook or websocket")
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
                "public_base_url": "https://your-domain.com",
                "qq_app_id": "",
                "qq_client_secret": "",
                "qq_bot_secret": "",
                "qq_api_base_url": "https://api.sgroup.qq.com",
                "qq_token_url": "https://bots.qq.com/app/getAppAccessToken",
                "qq_event_mode": "webhook",
                "qq_webhook_path": "/qq/callback",
                "qq_enable_websocket": False,
                "qq_enable_c2c": True,
                "qq_enable_group": False,
                "qq_enable_guild": False,
                "ai_provider": "xai",
                "ai_api_key": "",
                "ai_base_url": "https://api.x.ai/v1",
                "ai_model": "grok-4.3",
                "ai_temperature": 0.7,
                "ai_max_tokens": 1200,
                "ai_timeout_seconds": 60,
                "bot_name": "希恩X",
                "bot_persona_file": Path("./persona/default.md"),
                "bot_language": "zh-CN",
                "admin_openids": "",
                "database_url": "sqlite+aiosqlite:///./data/bot.db",
                "max_history_messages": 20,
                "max_memory_items": 12,
                "max_reply_chars": 1800,
                "memory_enabled": True,
                "memory_extract_enabled": True,
                "memory_min_importance": 3,
                "emotion_enabled": True,
                "proactive_enabled": False,
                "proactive_require_user_opt_in": True,
                "proactive_scan_interval_seconds": 300,
                "proactive_max_per_user_per_month": 4,
                "proactive_min_interval_hours": 24,
                "wakeup_enabled": True,
                "wakeup_respect_official_periods": True,
                "default_quiet_hours_start": "23:30",
                "default_quiet_hours_end": "08:30",
                "auto_delete_user_data_on_friend_del": False,
                "assets_enabled": True,
                "assets_dir": Path("./assets"),
                "asset_public_base_url": "https://your-domain.com/assets",
                "asset_send_probability": 0.25,
                "log_level": "INFO",
                "log_dir": Path("./logs"),
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
