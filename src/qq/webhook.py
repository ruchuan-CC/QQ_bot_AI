from __future__ import annotations

from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey


class WebhookSignatureVerifier:
    def __init__(self, bot_secret: str) -> None:
        self.bot_secret = bot_secret.strip()

    def verify(self, *, timestamp: str, body: bytes, signature: str) -> bool:
        if not self.bot_secret:
            raise ValueError("QQ_BOT_SECRET is required for webhook signature verification")
        try:
            verify_key = VerifyKey(bytes.fromhex(self.bot_secret))
            verify_key.verify(timestamp.encode("utf-8") + body, bytes.fromhex(signature))
            return True
        except (BadSignatureError, ValueError):
            return False


def build_callback_validation_response(plain_token: str, event_ts: str, bot_secret: str) -> dict[str, str]:
    if not bot_secret:
        raise ValueError("QQ_BOT_SECRET is required for callback validation")
    seed = bot_secret.encode("utf-8")
    while len(seed) < 32:
        seed = seed + seed
    signing_key = SigningKey(seed[:32])
    signature = signing_key.sign((event_ts + plain_token).encode("utf-8")).signature.hex()
    return {"plain_token": plain_token, "signature": signature}
