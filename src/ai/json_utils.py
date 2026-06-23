from __future__ import annotations

import json
from typing import Any


def safe_json_loads(raw: str, default: Any) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default
