"""SQLite persistence helpers for hour entries."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import sqlite3


def init_db(db_path: str) -> None:
    """Create required tables and indexes if they do not exist."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                entry_date TEXT NOT NULL,
                hours TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_entries_user_date
            ON entries (user_id, entry_date)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_entries_chat_date
            ON entries (chat_id, entry_date)
            """
        )


def insert_entry(
    db_path: str,
    *,
    user_id: int,
    chat_id: int,
    entry_date: str,
    hours: Decimal,
    raw_text: str,
    created_at: str | None = None,
) -> int:
    """Insert one hour entry and return the created row id."""
    created_ts = created_at or datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO entries (user_id, chat_id, entry_date, hours, raw_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, chat_id, entry_date, str(hours), raw_text, created_ts),
        )
        return int(cursor.lastrowid)


def aggregate_month_total(
    db_path: str,
    *,
    user_id: int,
    chat_id: int,
    year: int,
    month: int,
) -> Decimal:
    """Return the total hours for one user/chat month."""
    if month < 1 or month > 12:
        raise ValueError("month must be in range 1..12")

    month_prefix = f"{year:04d}-{month:02d}-"
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT hours
            FROM entries
            WHERE user_id = ?
              AND chat_id = ?
              AND entry_date LIKE ?
            """,
            (user_id, chat_id, f"{month_prefix}%"),
        )
        total = Decimal("0")
        for (hours_value,) in rows:
            total += Decimal(hours_value)
        return total
