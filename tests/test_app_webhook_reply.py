from fastapi.testclient import TestClient

from src.app import create_app
from src.config import Settings


class FakeAIProvider:
    async def complete(self, prompt: str) -> str:
        assert "hello" in prompt
        return "AI reply"


class FakeQQClient:
    def __init__(self):
        self.sent = []

    async def send_text_message(self, **kwargs):
        self.sent.append(kwargs)
        return {"id": "sent-message-id"}


def test_c2c_webhook_calls_ai_and_sends_passive_reply():
    settings = Settings(_env_file=None, qq_bot_secret="")
    qq_client = FakeQQClient()
    app = create_app(settings=settings, ai_provider=FakeAIProvider(), qq_client=qq_client)
    client = TestClient(app)

    response = client.post(
        "/qq/callback",
        json={
            "id": "event-1",
            "t": "C2C_MESSAGE_CREATE",
            "d": {
                "author": {"user_openid": "openid-1"},
                "content": "hello",
                "id": "msg-1",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "replied"
    assert qq_client.sent == [
        {
            "openid": "openid-1",
            "content": "AI reply",
            "msg_seq": 1,
            "msg_id": "msg-1",
            "event_id": None,
        }
    ]
