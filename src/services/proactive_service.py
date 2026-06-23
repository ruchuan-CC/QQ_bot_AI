from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class WakeupWindow:
    window_type: str
    window_start: datetime
    window_end: datetime
    used: bool = False


def compute_wakeup_windows(anchor_time: datetime) -> list[WakeupWindow]:
    return [
        WakeupWindow("same_day", anchor_time, anchor_time.replace(hour=23, minute=59, second=59)),
        WakeupWindow("day_1_3", anchor_time + timedelta(days=1), anchor_time + timedelta(days=3)),
        WakeupWindow("day_3_7", anchor_time + timedelta(days=3), anchor_time + timedelta(days=7)),
        WakeupWindow("day_7_30", anchor_time + timedelta(days=7), anchor_time + timedelta(days=30)),
    ]


class ProactivePolicy:
    def __init__(self, *, enabled: bool, require_user_opt_in: bool = True) -> None:
        self.enabled = enabled
        self.require_user_opt_in = require_user_opt_in

    def can_send(self, *, allow_proactive: bool, qq_allows_proactive: bool, in_quiet_hours: bool) -> bool:
        if not self.enabled:
            return False
        if self.require_user_opt_in and not allow_proactive:
            return False
        if not qq_allows_proactive or in_quiet_hours:
            return False
        return True
