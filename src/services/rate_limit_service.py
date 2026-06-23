from __future__ import annotations

from collections import Counter
from datetime import datetime


class MonthlyRateLimiter:
    def __init__(self, max_per_month: int) -> None:
        self.max_per_month = max_per_month

    def allow(
        self,
        monthly_keys: list[str],
        *,
        now: datetime,
        sent_times: list[datetime] | None = None,
    ) -> bool:
        if sent_times is not None:
            count = sum(1 for sent_at in sent_times if sent_at.year == now.year and sent_at.month == now.month)
            return count < self.max_per_month
        if not monthly_keys:
            return True
        return max(Counter(monthly_keys).values()) < self.max_per_month
