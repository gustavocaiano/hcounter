from decimal import Decimal

import pytest

from hourbot.service import parse_hours


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        ("0", Decimal("0")),
        ("1", Decimal("1")),
        ("0.5", Decimal("0.5")),
        ("12.75", Decimal("12.75")),
        (" 2 ", Decimal("2")),
    ],
)
def test_parse_hours_accepts_valid_numeric_inputs(raw_text: str, expected: Decimal) -> None:
    assert parse_hours(raw_text) == expected


@pytest.mark.parametrize(
    "raw_text",
    [
        "",
        "   ",
        "-1",
        "abc",
        "1,5",
        ".5",
        "1.",
        "+2",
    ],
)
def test_parse_hours_rejects_invalid_numeric_inputs(raw_text: str) -> None:
    with pytest.raises(ValueError):
        parse_hours(raw_text)
