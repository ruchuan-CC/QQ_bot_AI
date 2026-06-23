from __future__ import annotations

import random
from pathlib import Path

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp3", ".wav", ".mp4"}


class AssetService:
    def __init__(self, assets_dir: str | Path) -> None:
        self.assets_dir = Path(assets_dir)

    def _files_for(self, category: str) -> list[Path]:
        path = self.assets_dir / category
        if not path.exists():
            return []
        return sorted(file for file in path.iterdir() if file.is_file() and file.suffix.lower() in SUPPORTED_SUFFIXES)

    def count_by_category(self) -> dict[str, int]:
        if not self.assets_dir.exists():
            return {}
        counts: dict[str, int] = {}
        for category in sorted(path for path in self.assets_dir.iterdir() if path.is_dir()):
            count = len(self._files_for(category.name))
            if count:
                counts[category.name] = count
        return counts

    def choose(self, category: str) -> Path:
        files = self._files_for(category)
        if not files:
            raise FileNotFoundError(f"No supported assets found for category: {category}")
        return random.choice(files)
