import pytest

from src.services.command_service import CommandService
from src.services.memory_service import InMemoryMemoryRepository, MemoryService
from src.services.user_service import InMemoryUserRepository, UserService


@pytest.mark.asyncio
async def test_command_service_handles_ping_help_and_style():
    users = UserService(InMemoryUserRepository())
    memories = MemoryService(InMemoryMemoryRepository())
    service = CommandService(user_service=users, memory_service=memories)

    assert await service.handle("openid-1", "/ping") == "pong"
    assert "/status" in await service.handle("openid-1", "/help")
    assert "简洁直接" in await service.handle("openid-1", "/style 简洁直接")
    assert await users.get_setting("openid-1", "style") == "简洁直接"


@pytest.mark.asyncio
async def test_command_service_turns_proactive_on_and_off():
    users = UserService(InMemoryUserRepository())
    service = CommandService(
        user_service=users,
        memory_service=MemoryService(InMemoryMemoryRepository()),
    )

    await service.handle("openid-1", "/proactive on")
    assert (await users.get_or_create("openid-1")).allow_proactive is True

    await service.handle("openid-1", "/proactive off")
    assert (await users.get_or_create("openid-1")).allow_proactive is False
