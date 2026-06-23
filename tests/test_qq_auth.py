import pytest

from src.qq.auth import AccessTokenManager


class FakeTokenTransport:
    def __init__(self):
        self.calls = 0

    async def post(self, url, json, timeout):
        self.calls += 1

        class Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {"access_token": f"token-{json['appId']}", "expires_in": 7200}

        return Response()


@pytest.mark.asyncio
async def test_access_token_is_cached_until_refresh_window():
    transport = FakeTokenTransport()
    manager = AccessTokenManager(
        app_id="app-1",
        client_secret="secret",
        token_url="https://bots.qq.com/app/getAppAccessToken",
        transport=transport,
    )

    first = await manager.get_token()
    second = await manager.get_token()

    assert first == "token-app-1"
    assert second == first
    assert transport.calls == 1
