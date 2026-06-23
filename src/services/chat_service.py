from __future__ import annotations

from src.ai.provider import AIProvider
from src.prompts.chat_prompt import ChatPromptBuilder
from src.services.command_service import CommandService


class ChatService:
    def __init__(
        self,
        *,
        ai_provider: AIProvider,
        command_service: CommandService,
        prompt_builder: ChatPromptBuilder,
        persona: str,
    ) -> None:
        self.ai_provider = ai_provider
        self.command_service = command_service
        self.prompt_builder = prompt_builder
        self.persona = persona

    async def reply(self, qq_openid: str, content: str) -> str:
        command_reply = await self.command_service.handle(qq_openid, content)
        if command_reply is not None:
            return command_reply
        prompt = self.prompt_builder.build(
            persona=self.persona,
            memories=[],
            emotion={},
            style=None,
            history=[],
            current_message=content,
        )
        return await self.ai_provider.complete(prompt)
