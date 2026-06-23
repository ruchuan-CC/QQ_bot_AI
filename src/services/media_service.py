from __future__ import annotations

import base64
from pathlib import Path


def file_to_base64(path: str | Path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("ascii")
