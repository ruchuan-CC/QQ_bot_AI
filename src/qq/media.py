from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UploadedMedia:
    file_info: str
    file_uuid: str | None = None
