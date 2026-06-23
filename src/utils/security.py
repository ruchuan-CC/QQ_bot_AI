from __future__ import annotations


def redact_secrets(text: str, secrets: list[str] | tuple[str, ...]) -> str:
    redacted = text
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "***")
    return redacted
