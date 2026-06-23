from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.models import EmotionStateModel


@dataclass(slots=True)
class EmotionState:
    mood: str
    valence: float
    arousal: float
    need: str
    reason: str
    should_followup: bool
    followup_after_hours: int


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def parse_emotion_json(raw: str) -> EmotionState:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    return EmotionState(
        mood=str(payload.get("mood") or "unknown"),
        valence=_clamp(float(payload.get("valence") or 0)),
        arousal=_clamp(float(payload.get("arousal") or 0)),
        need=str(payload.get("need") or "none"),
        reason=str(payload.get("reason") or ""),
        should_followup=bool(payload.get("should_followup") or False),
        followup_after_hours=int(payload.get("followup_after_hours") or 0),
    )


class SQLEmotionRepository:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory

    async def get(self, qq_openid: str) -> EmotionState | None:
        async with self.session_factory() as session:
            row = await session.scalar(select(EmotionStateModel).where(EmotionStateModel.qq_openid == qq_openid))
        if row is None:
            return None
        return EmotionState(
            mood=row.mood,
            valence=row.valence,
            arousal=row.arousal,
            need=row.need,
            reason=row.reason,
            should_followup=row.should_followup,
            followup_after_hours=row.followup_after_hours,
        )

    async def upsert(self, qq_openid: str, state: EmotionState) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                row = await session.scalar(select(EmotionStateModel).where(EmotionStateModel.qq_openid == qq_openid))
                if row is None:
                    row = EmotionStateModel(
                        qq_openid=qq_openid,
                        mood=state.mood,
                        valence=state.valence,
                        arousal=state.arousal,
                        need=state.need,
                        reason=state.reason,
                        should_followup=state.should_followup,
                        followup_after_hours=state.followup_after_hours,
                    )
                    session.add(row)
                else:
                    row.mood = state.mood
                    row.valence = state.valence
                    row.arousal = state.arousal
                    row.need = state.need
                    row.reason = state.reason
                    row.should_followup = state.should_followup
                    row.followup_after_hours = state.followup_after_hours
                    row.updated_at = datetime.now(UTC)


class EmotionService:
    def __init__(self, repository: SQLEmotionRepository) -> None:
        self.repository = repository

    async def get(self, qq_openid: str) -> EmotionState | None:
        return await self.repository.get(qq_openid)

    async def as_prompt_dict(self, qq_openid: str) -> dict[str, str | float | bool | int]:
        state = await self.get(qq_openid)
        if state is None:
            return {}
        return {
            "mood": state.mood,
            "valence": state.valence,
            "arousal": state.arousal,
            "need": state.need,
            "reason": state.reason,
            "should_followup": state.should_followup,
            "followup_after_hours": state.followup_after_hours,
        }

    async def save(self, qq_openid: str, state: EmotionState) -> None:
        await self.repository.upsert(qq_openid, state)
