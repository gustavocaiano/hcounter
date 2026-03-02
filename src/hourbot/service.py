"""Domain logic helpers for parsing, aggregation, and formatting."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import re

from .db import aggregate_month_total

_NUMERIC_PATTERN = re.compile(r"^\d+(?:\.\d+)?$")
_GETMM_PATTERN = re.compile(r"^get(0[1-9]|1[0-2])$")


def parse_hours(raw_text: str) -> Decimal:
    """Parse a strict non-negative decimal number from text."""
    normalized = raw_text.strip()
    if not _NUMERIC_PATTERN.fullmatch(normalized):
        raise ValueError("Hours must be a non-negative decimal number")

    parsed = Decimal(normalized)
    if parsed < 0:
        raise ValueError("Hours must be >= 0")
    return parsed


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
    """Format hours deterministically without scientific notation."""
    normalized = hours.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


def format_subtotals(day_total: Decimal, month_total: Decimal) -> str:
    """Format day and month subtotals in a deterministic way."""
    return (
        f"Day subtotal: {format_hours_total(day_total)}h\n"
        f"Month subtotal: {format_hours_total(month_total)}h"
    )
