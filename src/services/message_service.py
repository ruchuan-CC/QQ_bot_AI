from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.models import ConversationModel, MessageModel


@dataclass(slots=True)
class StoredMessage:
    id: int
    qq_openid: str
    role: str
    content: str
    qq_msg_id: str | None = None
    qq_event_id: str | None = None
    qq_message_id_sent: str | None = None
    msg_seq: int | None = None
    created_at: datetime | None = None


class SQLMessageRepository:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory

    async def has_user_message(self, qq_openid: str, qq_msg_id: str | None) -> bool:
        if not qq_msg_id:
            return False
        async with self.session_factory() as session:
            message_id = await session.scalar(
                select(MessageModel.id).where(
                    MessageModel.qq_openid == qq_openid,
                    MessageModel.qq_msg_id == qq_msg_id,
                    MessageModel.role == "user",
                )
            )
        return message_id is not None

    async def add_user_message(
        self,
        *,
        qq_openid: str,
        content: str,
        qq_msg_id: str | None,
        qq_event_id: str | None,
        raw_event_json: str,
    ) -> StoredMessage:
        async with self.session_factory() as session:
            async with session.begin():
                conversation = await self._get_or_create_conversation(session, qq_openid)
                row = MessageModel(
                    conversation_id=conversation.id,
                    qq_openid=qq_openid,
                    role="user",
                    content=content,
                    qq_msg_id=qq_msg_id,
                    qq_event_id=qq_event_id,
                    raw_event_json=raw_event_json,
                )
                session.add(row)
                await session.flush()
                return self._to_message(row)

    async def add_assistant_message(
        self,
        *,
        qq_openid: str,
        content: str,
        msg_seq: int,
        qq_message_id_sent: str | None,
    ) -> StoredMessage:
        async with self.session_factory() as session:
            async with session.begin():
                conversation = await self._get_or_create_conversation(session, qq_openid)
                row = MessageModel(
                    conversation_id=conversation.id,
                    qq_openid=qq_openid,
                    role="assistant",
                    content=content,
                    qq_message_id_sent=qq_message_id_sent,
                    msg_seq=msg_seq,
                )
                session.add(row)
                await session.flush()
                return self._to_message(row)

    async def next_sequence(self, qq_openid: str) -> int:
        async with self.session_factory() as session:
            max_seq = await session.scalar(
                select(func.max(MessageModel.msg_seq)).where(
                    MessageModel.qq_openid == qq_openid,
                    MessageModel.role == "assistant",
                )
            )
        return int(max_seq or 0) + 1

    async def recent_history(self, qq_openid: str, *, limit: int) -> list[dict[str, str]]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.qq_openid == qq_openid)
            .order_by(MessageModel.id.desc())
            .limit(limit)
        )
        async with self.session_factory() as session:
            rows = (await session.scalars(stmt)).all()
        return [{"role": row.role, "content": row.content} for row in reversed(rows)]

    @staticmethod
    async def _get_or_create_conversation(session, qq_openid: str) -> ConversationModel:
        row = await session.scalar(
            select(ConversationModel)
            .where(ConversationModel.qq_openid == qq_openid, ConversationModel.scene_type == "c2c")
            .order_by(ConversationModel.id.asc())
        )
        if row is None:
            row = ConversationModel(qq_openid=qq_openid, scene_type="c2c")
            session.add(row)
            await session.flush()
        return row

    @staticmethod
    def _to_message(row: MessageModel) -> StoredMessage:
        return StoredMessage(
            id=row.id,
            qq_openid=row.qq_openid,
            role=row.role,
            content=row.content,
            qq_msg_id=row.qq_msg_id,
            qq_event_id=row.qq_event_id,
            qq_message_id_sent=row.qq_message_id_sent,
            msg_seq=row.msg_seq,
            created_at=row.created_at,
        )
