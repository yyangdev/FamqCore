"""Time helpers used by persistence and presentation code.

SQLite stores ISO-8601 UTC values. Keeping conversion in one place prevents
naive/aware datetime arithmetic from producing environment-dependent results.
"""

from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    return (value or utcnow()).astimezone(timezone.utc).isoformat()


def seconds_since(value: str, now: datetime | None = None) -> int:
    return max(0, int(((now or utcnow()) - parse_utc(value)).total_seconds()))
