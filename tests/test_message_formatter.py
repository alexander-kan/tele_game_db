"""Tests for message formatting helpers."""

from __future__ import annotations

from game_db.constants import DB_DATE_NOT_SET, EXCEL_NONE_VALUE
from game_db.services.message_formatter import MessageFormatter


class TestMessageFormatter:
    """Tests for MessageFormatter methods."""

    def test_format_game_info_basic(self) -> None:
        """Test format_game_info with typical data."""
        game_row = (
            "Test Game",
            "Пройдена",
            "Steam",
            "8.0",
            "50.0",
            "7.5",
            "9.0",
            "https://metacritic.com",
            "https://youtube.com",
            "10.0",
            "2024-01-01",
        )

        result = MessageFormatter.format_game_info(game_row)

        assert "Test Game" in result
        assert "Пройдена" in result
        assert "Steam" in result
        assert "8.0" in result
        assert "50" in result  # float_to_time converts "50.0" to "50 часов 0 минут"
        assert "7.5" in result
        assert "9.0" in result
        assert "https://metacritic.com" in result
        assert "https://youtube.com" in result

    def test_format_game_info_missing_time(self) -> None:
        """Test format_game_info with missing time data."""
        game_row = (
            "Test Game",
            "Не начата",
            "Steam",
            "8.0",
            "50.0",
            "7.5",
            None,
            "https://metacritic.com",
            "https://youtube.com",
            EXCEL_NONE_VALUE,
            DB_DATE_NOT_SET,
        )

        result = MessageFormatter.format_game_info(game_row)

        assert "Test Game" in result
        assert (
            "отсутствует" in result or "не запускалась" in result
        )

    # rest of tests unchanged...
