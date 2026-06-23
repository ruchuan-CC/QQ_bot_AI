from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


def create_engine(database_url: str) -> AsyncEngine:
    kwargs = {}
    if database_url.endswith(":memory:"):
        kwargs["poolclass"] = StaticPool
    return create_async_engine(database_url, future=True, **kwargs)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def session_scope(session_factory: async_sessionmaker) -> AsyncIterator:
    async with session_factory() as session:
        async with session.begin():
            yield session
