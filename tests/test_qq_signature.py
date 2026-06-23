import pytest
from nacl.signing import SigningKey

from src.qq.webhook import WebhookSignatureVerifier


def test_webhook_signature_verifier_accepts_valid_ed25519_signature():
    signing_key = SigningKey.generate()
    verify_key_hex = signing_key.verify_key.encode().hex()
    timestamp = "1710000000"
    body = b'{"op":0,"t":"C2C_MESSAGE_CREATE"}'
    signature = signing_key.sign(timestamp.encode() + body).signature.hex()

    verifier = WebhookSignatureVerifier(bot_secret=verify_key_hex)

    assert verifier.verify(timestamp=timestamp, body=body, signature=signature) is True


def test_webhook_signature_verifier_rejects_bad_signature():
    signing_key = SigningKey.generate()
    verify_key_hex = signing_key.verify_key.encode().hex()
    verifier = WebhookSignatureVerifier(bot_secret=verify_key_hex)

    assert verifier.verify(timestamp="1", body=b"{}", signature="00" * 64) is False


def test_webhook_signature_verifier_requires_secret():
    verifier = WebhookSignatureVerifier(bot_secret="")

    with pytest.raises(ValueError):
        verifier.verify(timestamp="1", body=b"{}", signature="00" * 64)
