from __future__ import annotations

import json
from dataclasses import dataclass


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
