from __future__ import annotations

from openai import AsyncOpenAI


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        api_style: str = "responses",
        temperature: float = 0.7,
        max_tokens: int = 1200,
        timeout: float = 60,
    ) -> None:
        self.model = model
        self.api_style = api_style
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = AsyncOpenAI(api_key=api_key or "missing-key", base_url=base_url, timeout=timeout)

    async def complete(self, prompt: str) -> str:
        if self.api_style == "responses":
            response = await self.client.responses.create(
                model=self.model,
                input=prompt,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            return self._extract_responses_text(response)
        if self.api_style != "chat_completions":
            raise ValueError("AI_API_STYLE must be responses or chat_completions")

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        return content or "我现在暂时无法生成回复。"

    @staticmethod
    def _extract_responses_text(response) -> str:
        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text)
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if text:
                    return str(text)
        return "我现在暂时无法生成回复。"
