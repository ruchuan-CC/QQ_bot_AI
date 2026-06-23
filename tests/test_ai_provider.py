from types import SimpleNamespace

import pytest

from src.ai.openai_compatible_client import OpenAICompatibleProvider


class FakeResponses:
    def __init__(self) -> None:
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="response text")


class FakeChatCompletions:
    def __init__(self) -> None:
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="chat text"))])


@pytest.mark.asyncio
async def test_provider_uses_responses_api_by_default():
    provider = OpenAICompatibleProvider(api_key="key", base_url="https://api.x.ai/v1", model="grok-4.3")
    fake_responses = FakeResponses()
    provider.client = SimpleNamespace(responses=fake_responses)

    result = await provider.complete("hello")

    assert result == "response text"
    assert fake_responses.calls == [
        {
            "model": "grok-4.3",
            "input": "hello",
            "temperature": 0.7,
            "max_output_tokens": 1200,
        }
    ]


@pytest.mark.asyncio
async def test_provider_can_use_chat_completions_for_compatible_models():
    provider = OpenAICompatibleProvider(
        api_key="key",
        base_url="https://example.com/v1",
        model="compatible-model",
        api_style="chat_completions",
    )
    fake_completions = FakeChatCompletions()
    provider.client = SimpleNamespace(chat=SimpleNamespace(completions=fake_completions))

    result = await provider.complete("hello")

    assert result == "chat text"
    assert fake_completions.calls[0]["model"] == "compatible-model"
    assert fake_completions.calls[0]["messages"] == [{"role": "user", "content": "hello"}]
