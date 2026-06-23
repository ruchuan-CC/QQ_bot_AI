from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.models import UserModel, UserSettingModel


@dataclass(slots=True)
class User:
    qq_openid: str
    active: bool = True
    allow_proactive: bool = False
    qq_allows_proactive: bool = True
    settings: dict[str, str] = field(default_factory=dict)


class SQLUserRepository:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory

    async def get_or_create(self, qq_openid: str) -> User:
        async with self.session_factory() as session:
            async with session.begin():
                row = await session.scalar(select(UserModel).where(UserModel.qq_openid == qq_openid))
                if row is None:
                    row = UserModel(qq_openid=qq_openid)
                    session.add(row)
                    await session.flush()
                else:
                    row.last_seen_at = datetime.now(UTC)
                settings = (
                    await session.scalars(select(UserSettingModel).where(UserSettingModel.qq_openid == qq_openid))
                ).all()
                return User(
                    qq_openid=row.qq_openid,
                    active=row.active,
                    allow_proactive=row.allow_proactive,
                    qq_allows_proactive=row.qq_allows_proactive,
                    settings={item.key: item.value for item in settings},
                )

    async def set_proactive(self, qq_openid: str, enabled: bool) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                row = await session.scalar(select(UserModel).where(UserModel.qq_openid == qq_openid))
                if row is None:
                    row = UserModel(qq_openid=qq_openid)
                    session.add(row)
                    await session.flush()
                row.allow_proactive = enabled
                row.updated_at = datetime.now(UTC)

    async def set_setting(self, qq_openid: str, key: str, value: str) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                await self._ensure_user(session, qq_openid)
                row = await session.scalar(
                    select(UserSettingModel).where(
                        UserSettingModel.qq_openid == qq_openid,
                        UserSettingModel.key == key,
                    )
                )
                if row is None:
                    row = UserSettingModel(qq_openid=qq_openid, key=key, value=value)
                    session.add(row)
                else:
                    row.value = value
                    row.updated_at = datetime.now(UTC)

    async def delete_setting(self, qq_openid: str, key: str) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                row = await session.scalar(
                    select(UserSettingModel).where(
                        UserSettingModel.qq_openid == qq_openid,
                        UserSettingModel.key == key,
                    )
                )
                if row is not None:
                    await session.delete(row)

    async def get_setting(self, qq_openid: str, key: str) -> str | None:
        async with self.session_factory() as session:
            row = await session.scalar(
                select(UserSettingModel).where(
                    UserSettingModel.qq_openid == qq_openid,
                    UserSettingModel.key == key,
                )
            )
        return row.value if row is not None else None

    @staticmethod
    async def _ensure_user(session, qq_openid: str) -> None:
        row = await session.scalar(select(UserModel).where(UserModel.qq_openid == qq_openid))
        if row is None:
            session.add(UserModel(qq_openid=qq_openid))
            await session.flush()


class UserService:
    def __init__(self, repository: SQLUserRepository) -> None:
        self.repository = repository

    async def get_or_create(self, qq_openid: str) -> User:
        return await self.repository.get_or_create(qq_openid)

    async def set_proactive(self, qq_openid: str, enabled: bool) -> None:
        await self.repository.set_proactive(qq_openid, enabled)

    async def set_setting(self, qq_openid: str, key: str, value: str) -> None:
        await self.repository.set_setting(qq_openid, key, value)

    async def delete_setting(self, qq_openid: str, key: str) -> None:
        await self.repository.delete_setting(qq_openid, key)

    async def get_setting(self, qq_openid: str, key: str) -> str | None:
        return await self.repository.get_setting(qq_openid, key)
