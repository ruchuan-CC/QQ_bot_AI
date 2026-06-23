from __future__ import annotations


class MessageDeduplicator:
    def __init__(self) -> None:
        self.seen: set[str] = set()

    def remember(self, msg_id: str | None) -> bool:
        if not msg_id:
            return False
        if msg_id in self.seen:
            return False
        self.seen.add(msg_id)
        return True


class MessageSequence:
    def __init__(self) -> None:
        self._by_openid: dict[str, int] = {}

    def next(self, qq_openid: str) -> int:
        value = self._by_openid.get(qq_openid, 0) + 1
        self._by_openid[qq_openid] = value
        return value
