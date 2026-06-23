from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qq_openid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(128))
    source_scene: Mapped[str | None] = mapped_column(String(128))
    source_scene_param: Mapped[str | None] = mapped_column(String(256))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_proactive: Mapped[bool] = mapped_column(Boolean, default=False)
    qq_allows_proactive: Mapped[bool] = mapped_column(Boolean, default=True)
    quiet_hours_start: Mapped[str] = mapped_column(String(5), default="23:30")
    quiet_hours_end: Mapped[str] = mapped_column(String(5), default="08:30")
    profile_summary: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ConversationModel(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qq_openid: Mapped[str] = mapped_column(String(128), index=True)
    scene_type: Mapped[str] = mapped_column(String(16), default="c2c")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversations.id"))
    qq_openid: Mapped[str] = mapped_column(String(128), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text, default="")
    qq_msg_id: Mapped[str | None] = mapped_column(String(128), index=True)
    qq_event_id: Mapped[str | None] = mapped_column(String(128))
    qq_message_id_sent: Mapped[str | None] = mapped_column(String(128))
    msg_seq: Mapped[int | None] = mapped_column(Integer)
    raw_event_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MemoryModel(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qq_openid: Mapped[str] = mapped_column(String(128), index=True)
    memory_type: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(Text, default="[]")
    confidence: Mapped[float] = mapped_column(Float, default=0)
    importance: Mapped[int] = mapped_column(Integer, default=0)
    source_message_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EmotionStateModel(Base):
    __tablename__ = "emotion_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qq_openid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    mood: Mapped[str] = mapped_column(String(64), default="unknown")
    valence: Mapped[float] = mapped_column(Float, default=0)
    arousal: Mapped[float] = mapped_column(Float, default=0)
    need: Mapped[str] = mapped_column(String(64), default="none")
    reason: Mapped[str] = mapped_column(Text, default="")
    should_followup: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_after_hours: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProactiveLogModel(Base):
    __tablename__ = "proactive_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qq_openid: Mapped[str] = mapped_column(String(128), index=True)
    message: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    asset_tag: Mapped[str | None] = mapped_column(String(64))
    is_wakeup: Mapped[bool] = mapped_column(Boolean, default=True)
    official_window_type: Mapped[str | None] = mapped_column(String(32))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(32), default="pending")
    error: Mapped[str | None] = mapped_column(Text)


class WakeupWindowModel(Base):
    __tablename__ = "wakeup_windows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qq_openid: Mapped[str] = mapped_column(String(128), index=True)
    anchor_user_message_id: Mapped[int | None] = mapped_column(Integer)
    anchor_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_type: Mapped[str] = mapped_column(String(32))
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserSettingModel(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qq_openid: Mapped[str] = mapped_column(String(128), index=True)
    key: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class APICallLogModel(Base):
    __tablename__ = "api_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(64))
    endpoint: Mapped[str] = mapped_column(String(256))
    status_code: Mapped[int | None] = mapped_column(Integer)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
