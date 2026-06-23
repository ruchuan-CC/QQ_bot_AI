from datetime import UTC, datetime, timedelta

from src.services.rate_limit_service import MonthlyRateLimiter


def test_monthly_rate_limiter_blocks_after_limit():
    limiter = MonthlyRateLimiter(max_per_month=2)
    now = datetime(2026, 6, 23, tzinfo=UTC)

    assert limiter.allow(["openid"], now=now) is True
    assert limiter.allow(["openid", "openid"], now=now) is False
    assert limiter.allow(["openid", "other"], now=now) is True


def test_monthly_rate_limiter_ignores_previous_month():
    limiter = MonthlyRateLimiter(max_per_month=1)
    now = datetime(2026, 6, 23, tzinfo=UTC)
    last_month = now - timedelta(days=40)

    assert limiter.allow(["openid"], now=now, sent_times=[last_month]) is True
