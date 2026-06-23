from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GatewaySession:
    url: str
    session_id: str | None = None
    sequence: int | None = None
