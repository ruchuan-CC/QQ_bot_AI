from src.config import Settings


def test_settings_defaults_are_c2c_only():
    settings = Settings(_env_file=None)

    assert settings.qq_enable_c2c is True
    assert settings.qq_enable_group is False
    assert settings.qq_enable_guild is False
    assert settings.qq_event_mode == "webhook"
    assert settings.proactive_enabled is False


def test_settings_redacts_secret_values():
    settings = Settings(
        _env_file=None,
        qq_client_secret="client-secret",
        qq_bot_secret="bot-secret",
        ai_api_key="ai-secret",
    )

    redacted = settings.redacted_dict()

    assert redacted["qq_client_secret"] == "***"
    assert redacted["qq_bot_secret"] == "***"
    assert redacted["ai_api_key"] == "***"
    assert "client-secret" not in str(redacted)
