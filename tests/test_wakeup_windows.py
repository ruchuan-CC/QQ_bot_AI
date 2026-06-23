from datetime import UTC, datetime

from src.services.proactive_service import compute_wakeup_windows
from src.utils.time_utils import in_quiet_hours


def test_compute_wakeup_windows_from_anchor_time():
    anchor = datetime(2026, 6, 23, 10, 0, tzinfo=UTC)
    windows = compute_wakeup_windows(anchor)

    assert [window.window_type for window in windows] == [
        "same_day",
        "day_1_3",
        "day_3_7",
        "day_7_30",
    ]
    assert windows[0].window_start == anchor
    assert windows[-1].window_end.day == 23


def test_quiet_hours_wraps_midnight():
    assert in_quiet_hours("23:30", "08:30", "00:15") is True
    assert in_quiet_hours("23:30", "08:30", "12:00") is False
