from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class QQWebhookPayload(BaseModel):
    id: str | None = None
    t: str | None = None
    d: dict = {}
