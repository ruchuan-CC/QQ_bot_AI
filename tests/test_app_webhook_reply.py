from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from src.app import create_app
from src.config import Settings


class FakeAIProvider:
    async def complete(self, prompt: str) -> str:
        assert "hello" in prompt
        if "长期记忆抽取器" in prompt:
            return (
                '{"should_save": true, "memories": ['
                '{"memory_type": "persona", "content": "用户喜欢赛博朋克素材", '
                '"tags": ["persona", "material"], "confidence": 0.9, "importance": 4}'
                "]}"
            )
        if "识别用户当前情绪" in prompt:
            return (
                '{"mood": "低落", "valence": -0.4, "arousal": 0.2, '
                '"need": "comfort", "reason": "用户说 hello 时语气偏弱", '
                '"should_followup": true, "followup_after_hours": 6}'
            )
        return "AI reply"


class FakeQQClient:
    def __init__(self):
        self.sent = []

    async def send_text_message(self, **kwargs):
        self.sent.append(kwargs)
        return {"id": "sent-message-id"}


def test_c2c_webhook_calls_ai_sends_reply_and_persists_user_data(tmp_path):
    database_path = tmp_path / "bot.db"
    settings = Settings(
        _env_file=None,
        qq_bot_secret="",
        database_url=f"sqlite+aiosqlite:///{database_path}",
    )
    qq_client = FakeQQClient()
    app = create_app(settings=settings, ai_provider=FakeAIProvider(), qq_client=qq_client)

    payload = {
        "id": "event-1",
        "t": "C2C_MESSAGE_CREATE",
        "d": {
            "author": {"user_openid": "openid-1"},
            "content": "hello",
            "id": "msg-1",
        },
    }

    with TestClient(app) as client:
        response = client.post(
            "/qq/callback",
            json=payload,
        )
        duplicate_response = client.post("/qq/callback", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "replied"
    assert duplicate_response.status_code == 200
    assert duplicate_response.json()["status"] == "duplicate"
    assert qq_client.sent == [
        {
            "openid": "openid-1",
            "content": "AI reply",
            "msg_seq": 1,
            "msg_id": "msg-1",
            "event_id": None,
        }
    ]

    engine = create_engine(f"sqlite:///{database_path}")
    with engine.connect() as conn:
        assert conn.execute(text("select count(*) from users where qq_openid = 'openid-1'")).scalar_one() == 1
        assert conn.execute(text("select count(*) from messages where qq_openid = 'openid-1'")).scalar_one() == 2
        memories = conn.execute(text("select memory_type from memories order by id")).scalars().all()
        assert memories == ["persona", "proactive"]
        mood = conn.execute(text("select mood from emotion_states where qq_openid = 'openid-1'")).scalar_one()
        assert mood == "低落"


def test_c2c_webhook_requires_signature_when_bot_secret_is_configured(tmp_path):
    settings = Settings(
        _env_file=None,
        qq_bot_secret="bot-secret",
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'bot.db'}",
    )
    app = create_app(settings=settings, ai_provider=FakeAIProvider(), qq_client=FakeQQClient())

    with TestClient(app) as client:
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

    assert response.status_code == 401
    assert response.json()["error"] == "missing signature"


def test_callback_validation_does_not_require_signature_headers(tmp_path):
    settings = Settings(
        _env_file=None,
        qq_bot_secret="bot-secret",
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'bot.db'}",
    )
    app = create_app(settings=settings, ai_provider=FakeAIProvider(), qq_client=FakeQQClient())

    with TestClient(app) as client:
        response = client.post(
            "/qq/callback",
            json={"op": 13, "id": "event-verify", "d": {"plain_token": "plain", "event_ts": "1710000000"}},
        )

    assert response.status_code == 200
    assert response.json()["plain_token"] == "plain"
    assert response.json()["signature"]
