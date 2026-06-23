from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    C2C_MESSAGE_CREATE = "C2C_MESSAGE_CREATE"
    FRIEND_ADD = "FRIEND_ADD"
    FRIEND_DEL = "FRIEND_DEL"
    FRIEND_ALLOW = "FRIEND_ALLOW"
    FRIEND_REJECT = "FRIEND_REJECT"
    UNKNOWN = "UNKNOWN"


C2C_EVENT_NAMES = {
    "C2C_MESSAGE_CREATE",
    "FRIEND_ADD",
    "FRIEND_DEL",
    "FRIEND_ALLOW",
    "FRIEND_REJECT",
    "C2C_MSG_RECEIVE",
}

OUT_OF_SCOPE_PREFIXES = ("GROUP_", "GUILD_", "CHANNEL_", "DIRECT_MESSAGE_", "AT_MESSAGE_")


@dataclass(slots=True)
class ParsedEvent:
    type: EventType
    raw_type: str
    event_id: str | None
    openid: str | None = None
    content: str = ""
    msg_id: str | None = None
    attachments: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    out_of_scope: bool = False

    @property
    def is_c2c(self) -> bool:
        return not self.out_of_scope and self.raw_type in C2C_EVENT_NAMES


def _extract_openid(data: dict[str, Any]) -> str | None:
    author = data.get("author") or {}
    user = data.get("user") or {}
    return (
        data.get("openid")
        or data.get("user_openid")
        or author.get("user_openid")
        or author.get("openid")
        or user.get("openid")
        or user.get("user_openid")
    )


def parse_event(payload: dict[str, Any]) -> ParsedEvent:
    raw_type = str(payload.get("t") or payload.get("type") or "UNKNOWN")
    data = payload.get("d") or payload.get("data") or {}
    out_of_scope = raw_type.startswith(OUT_OF_SCOPE_PREFIXES) or "GROUP" in raw_type

    try:
        event_type = EventType(raw_type)
    except ValueError:
        event_type = EventType.UNKNOWN

    return ParsedEvent(
        type=event_type,
        raw_type=raw_type,
        event_id=payload.get("id") or data.get("event_id"),
        openid=_extract_openid(data),
        content=str(data.get("content") or ""),
        msg_id=data.get("id") or data.get("msg_id"),
        attachments=list(data.get("attachments") or []),
        raw=payload,
        out_of_scope=out_of_scope,
    )
