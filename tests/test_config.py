from src.config import Settings


def test_settings_defaults_are_c2c_only():
    settings = Settings(_env_file=None)

    assert settings.qq_webhook_path == "/qq/callback"
    assert settings.ai_model == "grok-4.3"
    assert settings.ai_api_style == "responses"


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
