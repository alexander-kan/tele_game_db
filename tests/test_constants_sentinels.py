"""Tests for domain sentinel constants in game_db.constants."""

from __future__ import annotations

from game_db.constants import (
    DB_DATE_NOT_SET,
    EXCEL_DATE_NOT_SET,
    EXCEL_NONE_VALUE,
)


def test_excel_sentinel_values_are_stable() -> None:
    """Excel sentinel values must keep their literal forms.

    These values are persisted in existing Excel files, so changing them
    without a migration would silently break behaviour.
    """

    assert EXCEL_NONE_VALUE == "none"
    assert EXCEL_DATE_NOT_SET == "December 12, 4712"


def test_db_sentinel_date_is_stable() -> None:
    """DB sentinel date must keep its literal form.

    It is stored in existing SQLite data and is used as a marker for
    "no date set" in message formatting logic.
    """

    assert DB_DATE_NOT_SET == "4712-12-12"
