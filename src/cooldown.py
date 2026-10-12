import math
from email.utils import parsedate_to_datetime

def retry_deadline(value, now):
    delay = 3600
    try:
        text = str(value).strip()
        if text.isascii() and text.isdigit():
            delay = float(text)
        else:
            date = parsedate_to_datetime(text)
            if date.tzinfo is None:
                raise ValueError("Missing timezone")
            delay = date.timestamp() - now
        if not math.isfinite(delay):
            raise ValueError("Invalid delay")
    except (ValueError, TypeError, OverflowError):
        delay = 3600
    return now + max(60, delay)

def initialize(db):
    with db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS cooldowns "
            "(scope TEXT PRIMARY KEY, next_allowed_at REAL NOT NULL)"
        )

def defer(db, scope, deadline):
    with db:
        db.execute(
            "INSERT INTO cooldowns VALUES (?,?) "
            "ON CONFLICT(scope) DO UPDATE SET next_allowed_at="
            "MAX(cooldowns.next_allowed_at,excluded.next_allowed_at)",
            (scope, deadline)
        )

def remaining(db, scope, now):
    row = db.execute(
        "SELECT next_allowed_at FROM cooldowns WHERE scope=?", (scope,)
    ).fetchone()
    return max(0, row[0] - now) if row else 0
