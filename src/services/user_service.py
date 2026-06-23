from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class User:
    qq_openid: str
    active: bool = True
    allow_proactive: bool = False
    qq_allows_proactive: bool = True
    settings: dict[str, str] = field(default_factory=dict)


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def get_or_create(self, qq_openid: str) -> User:
        if qq_openid not in self.users:
            self.users[qq_openid] = User(qq_openid=qq_openid)
        return self.users[qq_openid]


class UserService:
    def __init__(self, repository: InMemoryUserRepository) -> None:
        self.repository = repository

    async def get_or_create(self, qq_openid: str) -> User:
        return await self.repository.get_or_create(qq_openid)

    async def set_proactive(self, qq_openid: str, enabled: bool) -> None:
        user = await self.get_or_create(qq_openid)
        user.allow_proactive = enabled

    async def set_setting(self, qq_openid: str, key: str, value: str) -> None:
        user = await self.get_or_create(qq_openid)
        user.settings[key] = value

    async def delete_setting(self, qq_openid: str, key: str) -> None:
        user = await self.get_or_create(qq_openid)
        user.settings.pop(key, None)

    async def get_setting(self, qq_openid: str, key: str) -> str | None:
        user = await self.get_or_create(qq_openid)
        return user.settings.get(key)
