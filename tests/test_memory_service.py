import pytest

from src.services.memory_service import InMemoryMemoryRepository, MemoryService, parse_memory_json


def test_parse_memory_json_filters_low_importance_items():
    result = parse_memory_json(
        '{"should_save": true, "memories": ['
        '{"memory_type": "preference", "content": "用户喜欢赛博朋克", '
        '"tags": ["审美"], "confidence": 0.9, "importance": 4},'
        '{"memory_type": "temporary", "content": "哈哈", '
        '"tags": [], "confidence": 0.4, "importance": 1}]}',
        min_importance=3,
    )

    assert len(result) == 1
    assert result[0].content == "用户喜欢赛博朋克"


@pytest.mark.asyncio
async def test_memory_service_deletes_memories_by_keyword():
    service = MemoryService(InMemoryMemoryRepository())
    await service.save("openid-1", "preference", "用户喜欢赛博朋克风格图片", ["图片"], 0.9, 4)

    deleted = await service.forget("openid-1", "赛博朋克")

    assert deleted == 1
    assert await service.list("openid-1") == []
