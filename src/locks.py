from __future__ import annotations

import asyncio
from collections import defaultdict


class OpenIDLockPool:
    def __init__(self) -> None:
        self._locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    def get(self, qq_openid: str) -> asyncio.Lock:
        return self._locks[qq_openid]
