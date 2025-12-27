"""Tests for custom exception classes in game_db.exceptions."""

from __future__ import annotations

from game_db.exceptions import (DatabaseError, DatabaseQueryError,
                                GameNotFoundError, PlatformNotFoundError,
                                SQLFileNotFoundError)


def test_database_error_stores_message_and_original() -> None:
    original = ValueError("boom")
    err = DatabaseError("db failed", original_error=original)

    assert err.message == "db failed"
    assert err.original_error is original


def test_database_query_error_stores_sql_and_params() -> None:
    original = RuntimeError("sql")
    err = DatabaseQueryError(
        "query failed",
        sql="SELECT * FROM games",
        params=("param",),
        original_error=original,
    )

    assert err.sql == "SELECT * FROM games"
    assert err.params == ("param",)
    assert err.original_error is original


def test_game_not_found_error_message_and_attr() -> None:
    err = GameNotFoundError("Test Game")

    assert "Test Game" in str(err)
    assert err.game_name == "Test Game"


def test_platform_not_found_error_message_and_attr() -> None:
    err = PlatformNotFoundError("SteamDeck")

    assert "SteamDeck" in str(err)
    assert err.platform_name == "SteamDeck"


def test_sql_file_not_found_error_message_and_attr() -> None:
    err = SQLFileNotFoundError("missing.sql")

    assert "missing.sql" in str(err)
    assert err.sql_file == "missing.sql"
