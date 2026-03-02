import pytest

from hourbot.service import parse_getmm


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        ("get01", 1),
        ("get02", 2),
        ("get12", 12),
        (" get09 ", 9),
    ],
)
def test_parse_getmm_accepts_valid_inputs(raw_text: str, expected: int) -> None:
    assert parse_getmm(raw_text) == expected


@pytest.mark.parametrize(
    "raw_text",
    [
        "",
        "get00",
        "get13",
        "get1",
        "GET02",
        "month02",
        "getab",
    ],
)
def test_parse_getmm_rejects_invalid_inputs(raw_text: str) -> None:
    with pytest.raises(ValueError):
        parse_getmm(raw_text)
