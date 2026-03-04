from decimal import Decimal

import pytest

from hourbot.service import format_hours_total, format_subtotals


@pytest.mark.parametrize(
    ("hours", "expected"),
    [
        (Decimal("0"), "0h 0m"),
        (Decimal("2"), "2h 0m"),
        (Decimal("2.5"), "2h 30m"),
        (Decimal("12.75"), "12h 45m"),
        (Decimal("-0.5"), "-0h 30m"),
    ],
)
def test_format_hours_total_renders_hours_and_minutes(hours: Decimal, expected: str) -> None:
    assert format_hours_total(hours) == expected


def test_format_subtotals_renders_hours_and_minutes() -> None:
    assert format_subtotals(Decimal("2.5"), Decimal("12.75")) == (
        "Day subtotal: 2h 30m\n"
        "Month subtotal: 12h 45m"
    )
