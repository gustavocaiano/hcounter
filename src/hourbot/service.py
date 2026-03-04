"""Domain logic helpers for parsing, aggregation, and formatting."""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
import re

from .db import aggregate_month_total

_NUMERIC_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?$")
_DURATION_PATTERN = re.compile(
    r"^(?:(?P<hours>\d+(?:\.\d+)?)h(?:\s*(?:and\s*)?(?P<minutes>\d+)m)?|(?P<minutes_only>\d+)m)$"
)
_GETMM_PATTERN = re.compile(r"^get(0[1-9]|1[0-2])$")


def parse_hours(raw_text: str) -> Decimal:
    """Parse hour input as decimal hours.

    Accepted forms:
    - Decimal hours: 2.5, -1, 0.5
    - Hours/minutes: 2h, 2h 30m, 30m
    """
    normalized = raw_text.strip()
    if not _NUMERIC_PATTERN.fullmatch(normalized):
        sign = Decimal("1")
        duration_text = normalized
        if duration_text.startswith("-"):
            sign = Decimal("-1")
            duration_text = duration_text[1:].strip()

        duration_match = _DURATION_PATTERN.fullmatch(duration_text)
        if duration_match is None:
            raise ValueError("Hours must be a decimal number or use h/m format")

        if duration_match.group("minutes_only") is not None:
            minutes = Decimal(duration_match.group("minutes_only"))
            return sign * (minutes / Decimal("60"))

        total = Decimal(duration_match.group("hours"))
        minutes_part = duration_match.group("minutes")
        if minutes_part is not None:
            total += Decimal(minutes_part) / Decimal("60")
        return sign * total

    return Decimal(normalized)


def parse_getmm(raw_text: str) -> int:
    """Parse getMM command text and return the month number."""
    normalized = raw_text.strip()
    match = _GETMM_PATTERN.fullmatch(normalized)
    if match is None:
        raise ValueError("Command must follow getMM format with MM from 01 to 12")
    return int(match.group(1))


def get_current_month_total(
    db_path: str,
    *,
    user_id: int,
    chat_id: int,
    today: date | None = None,
) -> Decimal:
    """Return current month total using the persistence layer."""
    reference = today or date.today()
    return aggregate_month_total(
        db_path,
        user_id=user_id,
        chat_id=chat_id,
        year=reference.year,
        month=reference.month,
    )


def get_selected_month_total(
    db_path: str,
    *,
    user_id: int,
    chat_id: int,
    month: int,
    today: date | None = None,
) -> Decimal:
    """Return selected month total for the current year."""
    reference = today or date.today()
    return aggregate_month_total(
        db_path,
        user_id=user_id,
        chat_id=chat_id,
        year=reference.year,
        month=month,
    )


def format_hours_total(hours: Decimal) -> str:
    """Format decimal hours as '{h}h {m}m'."""
    total_minutes = (hours * Decimal("60")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    total_minutes_int = int(total_minutes)
    sign = "-" if total_minutes_int < 0 else ""
    abs_minutes = abs(total_minutes_int)
    whole_hours, minute_remainder = divmod(abs_minutes, 60)
    return f"{sign}{whole_hours}h {minute_remainder}m"


def format_subtotals(day_total: Decimal, month_total: Decimal) -> str:
    """Format day and month subtotals in a deterministic way."""
    return (
        f"Day subtotal: {format_hours_total(day_total)}\n"
        f"Month subtotal: {format_hours_total(month_total)}"
    )
