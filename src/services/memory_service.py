from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class MemoryItem:
    qq_openid: str
    memory_type: str
    content: str
    tags: list[str]
    confidence: float
    importance: int
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    deleted_at: datetime | None = None


def parse_memory_json(raw: str, *, min_importance: int = 3) -> list[MemoryItem]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not payload.get("should_save"):
        return []

    items: list[MemoryItem] = []
    for item in payload.get("memories") or []:
        importance = int(item.get("importance") or 0)
        content = str(item.get("content") or "").strip()
        if importance < min_importance or not content:
            continue
        items.append(
            MemoryItem(
                qq_openid="",
                memory_type=str(item.get("memory_type") or "note"),
                content=content,
                tags=list(item.get("tags") or []),
                confidence=float(item.get("confidence") or 0),
                importance=importance,
            )
        )
    return items


class InMemoryMemoryRepository:
    def __init__(self) -> None:
        self.items: list[MemoryItem] = []

    async def add(self, item: MemoryItem) -> None:
        self.items.append(item)

    async def list(self, qq_openid: str) -> list[MemoryItem]:
        return [item for item in self.items if item.qq_openid == qq_openid and item.deleted_at is None]


class MemoryService:
    def __init__(self, repository: InMemoryMemoryRepository) -> None:
        self.repository = repository

    async def save(
        self,
        qq_openid: str,
        memory_type: str,
        content: str,
        tags: list[str],
        confidence: float,
        importance: int,
    ) -> MemoryItem:
        item = MemoryItem(
            qq_openid=qq_openid,
            memory_type=memory_type,
            content=content,
            tags=tags,
            confidence=confidence,
            importance=importance,
        )
        await self.repository.add(item)
        return item

    async def list(self, qq_openid: str) -> list[MemoryItem]:
        return await self.repository.list(qq_openid)

    async def forget(self, qq_openid: str, keyword: str) -> int:
        deleted = 0
        for item in await self.repository.list(qq_openid):
            if keyword in item.content or keyword in " ".join(item.tags):
                item.deleted_at = datetime.now(UTC)
                deleted += 1
        return deleted

    async def summary(self, qq_openid: str) -> str:
        items = await self.list(qq_openid)
        if not items:
            return "当前没有长期记忆。"
        return "\n".join(f"- {item.content}" for item in items)
