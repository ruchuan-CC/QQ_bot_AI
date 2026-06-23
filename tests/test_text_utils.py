from src.utils.security import redact_secrets
from src.utils.text_utils import split_reply


def test_split_reply_respects_max_chars():
    chunks = split_reply("abcdef", max_chars=2)

    assert chunks == ["ab", "cd", "ef"]


def test_redact_secrets_masks_known_values():
    text = "client-secret and ai-secret"

    redacted = redact_secrets(text, ["client-secret", "ai-secret"])

    assert redacted == "*** and ***"
