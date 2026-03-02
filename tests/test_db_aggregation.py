from decimal import Decimal

import pytest

from hourbot.db import aggregate_month_total, init_db, insert_entry


def test_aggregate_month_total_sums_only_selected_month(tmp_path) -> None:
    db_path = str(tmp_path / "entries.sqlite3")
    init_db(db_path)

    insert_entry(
        db_path,
        user_id=1,
        chat_id=10,
        entry_date="2026-02-01",
        hours=Decimal("1.5"),
        raw_text="1.5",
    )
    insert_entry(
        db_path,
        user_id=1,
        chat_id=10,
        entry_date="2026-02-15",
        hours=Decimal("2"),
        raw_text="2",
    )
    insert_entry(
        db_path,
        user_id=1,
        chat_id=10,
        entry_date="2026-03-01",
        hours=Decimal("9"),
        raw_text="9",
    )

    total = aggregate_month_total(db_path, user_id=1, chat_id=10, year=2026, month=2)

    assert total == Decimal("3.5")


def test_aggregate_month_total_is_scoped_by_user_and_chat(tmp_path) -> None:
    db_path = str(tmp_path / "entries.sqlite3")
    init_db(db_path)

    insert_entry(
        db_path,
        user_id=1,
        chat_id=10,
        entry_date="2026-02-01",
        hours=Decimal("1"),
        raw_text="1",
    )
    insert_entry(
        db_path,
        user_id=2,
        chat_id=10,
        entry_date="2026-02-01",
        hours=Decimal("5"),
        raw_text="5",
    )
    insert_entry(
        db_path,
        user_id=1,
        chat_id=99,
        entry_date="2026-02-01",
        hours=Decimal("7"),
        raw_text="7",
    )

    total = aggregate_month_total(db_path, user_id=1, chat_id=10, year=2026, month=2)

    assert total == Decimal("1")


def test_aggregate_month_total_returns_zero_when_no_entries(tmp_path) -> None:
    db_path = str(tmp_path / "entries.sqlite3")
    init_db(db_path)

    total = aggregate_month_total(db_path, user_id=1, chat_id=10, year=2026, month=2)

    assert total == Decimal("0")


@pytest.mark.parametrize("month", [0, 13])
def test_aggregate_month_total_rejects_invalid_month(month: int, tmp_path) -> None:
    db_path = str(tmp_path / "entries.sqlite3")
    init_db(db_path)

    with pytest.raises(ValueError):
        aggregate_month_total(db_path, user_id=1, chat_id=10, year=2026, month=month)
