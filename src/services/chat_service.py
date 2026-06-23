from __future__ import annotations

import json
from dataclasses import dataclass

from loguru import logger

from src.ai.provider import AIProvider
from src.prompts.chat_prompt import ChatPromptBuilder
from src.prompts.emotion_prompt import EMOTION_RECOGNITION_PROMPT
from src.prompts.memory_prompt import MEMORY_EXTRACTION_PROMPT
from src.qq.events import ParsedEvent
from src.services.emotion_service import EmotionService, parse_emotion_json
from src.services.memory_service import MemoryService, parse_memory_json
from src.services.message_service import SQLMessageRepository
from src.services.user_service import UserService


class DuplicateMessageError(Exception):
    pass


@dataclass(slots=True)
class ChatReply:
    content: str
    msg_seq: int


class ChatService:
    def __init__(
        self,
        *,
        ai_provider: AIProvider,
        user_service: UserService,
        message_repository: SQLMessageRepository,
        memory_service: MemoryService,
        emotion_service: EmotionService,
        prompt_builder: ChatPromptBuilder,
        persona: str,
        max_history_messages: int,
        max_memory_items: int,
        max_reply_chars: int,
        memory_enabled: bool = True,
        memory_extract_enabled: bool = True,
        memory_min_importance: int = 3,
        emotion_enabled: bool = True,
    ) -> None:
        self.ai_provider = ai_provider
        self.user_service = user_service
        self.message_repository = message_repository
        self.memory_service = memory_service
        self.emotion_service = emotion_service
        self.prompt_builder = prompt_builder
        self.persona = persona
        self.max_history_messages = max_history_messages
        self.max_memory_items = max_memory_items
        self.max_reply_chars = max_reply_chars
        self.memory_enabled = memory_enabled
        self.memory_extract_enabled = memory_extract_enabled
        self.memory_min_importance = memory_min_importance
        self.emotion_enabled = emotion_enabled

    async def prepare_reply(self, event: ParsedEvent) -> ChatReply:
        if not event.openid:
            raise ValueError("C2C event missing openid")
        if await self.message_repository.has_user_message(event.openid, event.msg_id):
            raise DuplicateMessageError

        await self.user_service.get_or_create(event.openid)
        history = await self.message_repository.recent_history(event.openid, limit=self.max_history_messages)
        user_message = await self.message_repository.add_user_message(
            qq_openid=event.openid,
            content=event.content,
            qq_msg_id=event.msg_id,
            qq_event_id=event.event_id,
            raw_event_json=json.dumps(event.raw, ensure_ascii=False),
        )
        await self._save_attachment_memories(event)

        memories = []
        if self.memory_enabled:
            memories = [
                f"[{item.memory_type}] {item.content}"
                for item in await self.memory_service.list_for_prompt(event.openid, limit=self.max_memory_items)
            ]
        emotion = await self.emotion_service.as_prompt_dict(event.openid) if self.emotion_enabled else {}
        style = await self.user_service.get_setting(event.openid, "style")
        prompt = self.prompt_builder.build(
            persona=self.persona,
            memories=memories,
            emotion=emotion,
            style=style,
            history=history,
            current_message=event.content,
        )
        try:
            reply_text = await self.ai_provider.complete(prompt)
        except Exception:
            logger.exception("AI provider failed while preparing C2C reply")
            reply_text = "我现在暂时无法生成回复。"
        reply_text = self._trim_reply(reply_text)

        await self._extract_long_term_data(event=event, assistant_reply=reply_text, source_message_id=user_message.id)
        msg_seq = await self.message_repository.next_sequence(event.openid)
        return ChatReply(content=reply_text, msg_seq=msg_seq)

    async def record_assistant_reply(
        self,
        *,
        qq_openid: str,
        content: str,
        msg_seq: int,
        qq_message_id_sent: str | None,
    ) -> None:
        await self.message_repository.add_assistant_message(
            qq_openid=qq_openid,
            content=content,
            msg_seq=msg_seq,
            qq_message_id_sent=qq_message_id_sent,
        )

    async def _save_attachment_memories(self, event: ParsedEvent) -> None:
        if not self.memory_enabled or not event.openid or not event.attachments:
            return
        for attachment in event.attachments:
            content = json.dumps(attachment, ensure_ascii=False)
            await self.memory_service.save(
                event.openid,
                "material",
                f"用户发送过素材：{content}",
                ["material", "attachment"],
                1.0,
                5,
            )

    async def _extract_long_term_data(
        self,
        *,
        event: ParsedEvent,
        assistant_reply: str,
        source_message_id: int,
    ) -> None:
        if not event.openid:
            return
        if self.memory_enabled and self.memory_extract_enabled:
            try:
                raw = await self.ai_provider.complete(
                    self._build_memory_prompt(
                        user_message=event.content,
                        assistant_reply=assistant_reply,
                    )
                )
                for item in parse_memory_json(raw, min_importance=self.memory_min_importance):
                    await self.memory_service.save(
                        event.openid,
                        item.memory_type,
                        item.content,
                        item.tags,
                        item.confidence,
                        item.importance,
                    )
            except Exception:
                logger.exception("Failed to extract long-term memory from message {}", source_message_id)

        if self.emotion_enabled:
            try:
                raw = await self.ai_provider.complete(
                    self._build_emotion_prompt(
                        user_message=event.content,
                        assistant_reply=assistant_reply,
                    )
                )
                state = parse_emotion_json(raw)
                await self.emotion_service.save(event.openid, state)
                if self.memory_enabled and state.should_followup:
                    await self.memory_service.save(
                        event.openid,
                        "proactive",
                        f"用户可能需要在 {state.followup_after_hours} 小时后被主动关心：{state.reason or state.need}",
                        ["proactive", "emotion", state.need],
                        0.8,
                        4,
                    )
            except Exception:
                logger.exception("Failed to extract emotion from message {}", source_message_id)

    def _trim_reply(self, text: str) -> str:
        stripped = text.strip()
        if len(stripped) <= self.max_reply_chars:
            return stripped
        return stripped[: self.max_reply_chars].rstrip()

    @staticmethod
    def _build_memory_prompt(*, user_message: str, assistant_reply: str) -> str:
        return "\n\n".join(
            [
                MEMORY_EXTRACTION_PROMPT,
                "# 用户消息",
                user_message,
                "# 机器人回复",
                assistant_reply,
            ]
        )

    @staticmethod
    def _build_emotion_prompt(*, user_message: str, assistant_reply: str) -> str:
        return "\n\n".join(
            [
                EMOTION_RECOGNITION_PROMPT,
                "# 用户消息",
                user_message,
                "# 机器人回复",
                assistant_reply,
            ]
        )
