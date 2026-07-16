from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def days_ago(days: int) -> datetime:
    return utcnow() - timedelta(days=days)


def parse_iso_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def is_recent(dt: datetime | None, max_days: int = 30) -> bool:
    if dt is None:
        return False
    return utcnow() - dt < timedelta(days=max_days)


def format_date(dt: datetime | None) -> str:
    if dt is None:
        return "unknown"
    return dt.strftime("%Y-%m-%d")
