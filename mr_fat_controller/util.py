"""Generic utility functions."""

from datetime import datetime, timezone


def is_recently_active(dt: datetime) -> bool:
    """Check whether the datetime is within the last five minutes."""
    now = datetime.now(tz=timezone.utc).replace(tzinfo=None)  # noqa:UP017
    diff = now - dt
    return diff.seconds <= 300  # noqa:PLR2004
