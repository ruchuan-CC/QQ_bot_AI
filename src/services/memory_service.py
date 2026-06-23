from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.models import MemoryModel


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


class SQLMemoryRepository:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory

    async def add(self, item: MemoryItem) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                session.add(
                    MemoryModel(
                        qq_openid=item.qq_openid,
                        memory_type=item.memory_type,
                        content=item.content,
                        tags=json.dumps(item.tags, ensure_ascii=False),
                        confidence=item.confidence,
                        importance=item.importance,
                    )
                )

    async def list(self, qq_openid: str, *, limit: int | None = None) -> list[MemoryItem]:
        stmt = (
            select(MemoryModel)
            .where(MemoryModel.qq_openid == qq_openid, MemoryModel.deleted_at.is_(None))
            .order_by(MemoryModel.importance.desc(), MemoryModel.updated_at.desc(), MemoryModel.id.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        async with self.session_factory() as session:
            rows = (await session.scalars(stmt)).all()
        return [self._to_item(row) for row in rows]

    @staticmethod
    def _to_item(row: MemoryModel) -> MemoryItem:
        try:
            tags = json.loads(row.tags or "[]")
        except json.JSONDecodeError:
            tags = []
        if not isinstance(tags, list):
            tags = []
        return MemoryItem(
            qq_openid=row.qq_openid,
            memory_type=row.memory_type,
            content=row.content,
            tags=[str(tag) for tag in tags],
            confidence=row.confidence,
            importance=row.importance,
            created_at=row.created_at,
            deleted_at=row.deleted_at,
        )

    async def forget(self, qq_openid: str, keyword: str) -> int:
        deleted = 0
        async with self.session_factory() as session:
            async with session.begin():
                rows = (
                    await session.scalars(
                        select(MemoryModel).where(
                            MemoryModel.qq_openid == qq_openid,
                            MemoryModel.deleted_at.is_(None),
                        )
                    )
                ).all()
                now = datetime.now(UTC)
                for row in rows:
                    if keyword in row.content or keyword in row.tags:
                        row.deleted_at = now
                        deleted += 1
        return deleted


class MemoryService:
    def __init__(self, repository: InMemoryMemoryRepository | SQLMemoryRepository) -> None:
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

    async def list_for_prompt(self, qq_openid: str, *, limit: int) -> list[MemoryItem]:
        try:
            return await self.repository.list(qq_openid, limit=limit)
        except TypeError:
            return (await self.repository.list(qq_openid))[:limit]

    async def forget(self, qq_openid: str, keyword: str) -> int:
        if hasattr(self.repository, "forget"):
            return await self.repository.forget(qq_openid, keyword)
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
