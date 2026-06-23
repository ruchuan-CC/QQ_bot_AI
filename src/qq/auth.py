from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

import httpx


class TokenTransport(Protocol):
    async def post(self, url: str, json: dict[str, str], timeout: float) -> Any:
        ...


@dataclass(slots=True)
class AccessToken:
    value: str
    expires_at: datetime

    def valid_for(self, seconds: int) -> bool:
        return self.expires_at - datetime.now(UTC) > timedelta(seconds=seconds)


class AccessTokenManager:
    def __init__(
        self,
        *,
        app_id: str,
        client_secret: str,
        token_url: str,
        transport: TokenTransport | None = None,
        refresh_margin_seconds: int = 300,
    ) -> None:
        self.app_id = app_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.transport = transport or httpx.AsyncClient()
        self.refresh_margin_seconds = refresh_margin_seconds
        self._cached: AccessToken | None = None

    async def get_token(self) -> str:
        if self._cached and self._cached.valid_for(self.refresh_margin_seconds):
            return self._cached.value

        response = await self.transport.post(
            self.token_url,
            json={"appId": self.app_id, "clientSecret": self.client_secret},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        expires_in = int(data.get("expires_in") or data.get("expiresIn") or 7200)
        self._cached = AccessToken(
            value=str(data["access_token"]),
            expires_at=datetime.now(UTC) + timedelta(seconds=expires_in),
        )
        return self._cached.value
