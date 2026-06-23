from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import Settings


def main() -> None:
    settings = Settings()
    missing = [
        name
        for name in ("qq_app_id", "qq_client_secret", "qq_bot_secret", "ai_api_key")
        if not getattr(settings, name)
    ]
    if missing:
        print("Missing required settings: " + ", ".join(missing))
        raise SystemExit(1)
    print("Configuration looks usable.")


if __name__ == "__main__":
    main()
