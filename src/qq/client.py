from __future__ import annotations

from typing import Any

import httpx

from src.qq.auth import AccessTokenManager
from src.qq.errors import QQAPIError
from src.qq.message_types import C2CMessagePayloadBuilder


class QQOfficialClient:
    def __init__(
        self,
        *,
        api_base_url: str,
        token_manager: AccessTokenManager,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.token_manager = token_manager
        self.http = http_client or httpx.AsyncClient(timeout=30)

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        token = await self.token_manager.get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"QQBot {token}"
        url = f"{self.api_base_url}{path}"
        response = await self.http.request(method, url, headers=headers, **kwargs)
        if response.status_code >= 400:
            try:
                data = response.json()
            except ValueError:
                data = {"message": response.text}
            raise QQAPIError(
                str(data.get("message") or data),
                status_code=response.status_code,
                error_code=str(data.get("code") or ""),
            )
        if not response.content:
            return {}
        return response.json()

    async def send_text_message(
        self,
        *,
        openid: str,
        content: str,
        msg_seq: int,
        msg_id: str | None = None,
        event_id: str | None = None,
        is_wakeup: bool = False,
    ) -> dict[str, Any]:
        payload = C2CMessagePayloadBuilder.text(
            content=content,
            msg_seq=msg_seq,
            msg_id=msg_id,
            event_id=event_id,
            is_wakeup=is_wakeup,
        )
        return await self._request("POST", f"/v2/users/{openid}/messages", json=payload)

    async def upload_c2c_file(
        self,
        *,
        openid: str,
        file_type: int,
        url: str | None = None,
        file_data: str | None = None,
        srv_send_msg: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"file_type": file_type, "srv_send_msg": srv_send_msg}
        if url:
            payload["url"] = url
        if file_data:
            payload["file_data"] = file_data
        return await self._request("POST", f"/v2/users/{openid}/files", json=payload)

    async def recall_c2c_message(self, *, openid: str, message_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v2/users/{openid}/messages/{message_id}")

    async def generate_share_url(self, *, callback_data: str = "") -> dict[str, Any]:
        return await self._request("POST", "/v2/generate_url_link", json={"callback_data": callback_data})
