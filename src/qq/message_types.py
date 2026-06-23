from __future__ import annotations

from typing import Any


class C2CMessagePayloadBuilder:
    TEXT_MSG_TYPE = 0
    MARKDOWN_MSG_TYPE = 2
    ARK_MSG_TYPE = 3
    EMBED_MSG_TYPE = 4
    MEDIA_MSG_TYPE = 7

    @staticmethod
    def _base(
        *,
        msg_seq: int,
        msg_id: str | None = None,
        event_id: str | None = None,
        is_wakeup: bool = False,
    ) -> dict[str, Any]:
        if is_wakeup and (msg_id or event_id):
            raise ValueError("is_wakeup payload cannot include msg_id or event_id")
        payload: dict[str, Any] = {"msg_seq": msg_seq}
        if msg_id:
            payload["msg_id"] = msg_id
        if event_id:
            payload["event_id"] = event_id
        if is_wakeup:
            payload["is_wakeup"] = True
        return payload

    @classmethod
    def text(
        cls,
        *,
        content: str,
        msg_seq: int,
        msg_id: str | None = None,
        event_id: str | None = None,
        is_wakeup: bool = False,
    ) -> dict[str, Any]:
        payload = cls._base(
            msg_seq=msg_seq,
            msg_id=msg_id,
            event_id=event_id,
            is_wakeup=is_wakeup,
        )
        payload.update({"msg_type": cls.TEXT_MSG_TYPE, "content": content})
        return payload

    @classmethod
    def media(
        cls,
        *,
        file_info: str,
        msg_seq: int,
        msg_id: str | None = None,
        event_id: str | None = None,
        is_wakeup: bool = False,
    ) -> dict[str, Any]:
        payload = cls._base(
            msg_seq=msg_seq,
            msg_id=msg_id,
            event_id=event_id,
            is_wakeup=is_wakeup,
        )
        payload.update({"msg_type": cls.MEDIA_MSG_TYPE, "media": {"file_info": file_info}})
        return payload
