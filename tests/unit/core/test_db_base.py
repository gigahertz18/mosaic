"""Unit tests for app.db.base."""

from __future__ import annotations

from datetime import UTC, datetime

from app.db.base import utc_now


def test_utc_now_returns_timezone_aware_utc_datetime() -> None:
    result = utc_now()

    assert isinstance(result, datetime)
    assert result.tzinfo == UTC
