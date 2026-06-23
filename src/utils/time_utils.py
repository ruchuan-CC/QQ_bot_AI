from __future__ import annotations

from datetime import time


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(hour=int(hour), minute=int(minute))


def in_quiet_hours(start: str, end: str, current: str) -> bool:
    start_time = parse_hhmm(start)
    end_time = parse_hhmm(end)
    current_time = parse_hhmm(current)

    if start_time <= end_time:
        return start_time <= current_time < end_time
    return current_time >= start_time or current_time < end_time
