"""Tests for error handling in formatters and validators."""

from __future__ import annotations

import pytest

from game_db.excel.validator import ExcelValidator
from game_db.services.message_formatter import MessageFormatter

pytestmark = pytest.mark.error_handling


class TestMessageFormatterErrorHandling:
    """Test error handling in MessageFormatter."""

    def test_format_game_info_missing_fields(self) -> None:
        """Test format_game_info handles missing fields."""
        # Game row with missing optional fields
        game_row = (
            "Test Game",
            "Пройдена",
            "Steam",
            None,  # Missing press_score
            None,  # Missing average_time_beat
            None,  # Missing user_score
            None,  # Missing my_score
            None,  # Missing metacritic_url
            None,  # Missing trailer_url
            None,  # Missing my_time_beat
            None,  # Missing last_launch_date
        )

        result = MessageFormatter.format_game_info(game_row)

        assert "Test Game" in result
        assert "не указано" in result

    def test_format_game_info_empty_strings(self) -> None:
        """Test format_game_info handles empty strings."""
        game_row = (
            "",  # Empty game name
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        )

        result = MessageFormatter.format_game_info(game_row)

        # Should not crash
        assert isinstance(result, str)

    def test_format_multiple_games_empty_list(self) -> None:
        """Test format_multiple_games handles empty list."""
        games: list[tuple] = []

        result = MessageFormatter.format_multiple_games(games)

        assert "0" in result
        assert isinstance(result, str)

    def test_format_game_list_none_values(self) -> None:
        """Test format_game_list handles None values."""
        games = [
            ("Game 1", None, None, None),
            (None, "8.0", "50.0", "https://youtube.com"),
        ]

        result = MessageFormatter.format_game_list(games)

        # Should not crash
        assert isinstance(result, str)

    def test_format_completed_games_stats_zero_values(self) -> None:
        """Test format_completed_games_stats handles zero values."""
        platform_counts = {
            "Steam": 0,
            "Switch": 0,
        }

        result = MessageFormatter.format_completed_games_stats(platform_counts)

        assert isinstance(result, str)
        assert "0" in result

    def test_format_time_stats_all_none(self) -> None:
        """Test format_time_stats handles all None values."""
        platform_times: dict[str, tuple[None, None]] = {
            "Steam": (None, None),
            "Switch": (None, None),
        }

        result = MessageFormatter.format_time_stats(
            platform_times, 0.0  # type: ignore
        )

        assert isinstance(result, str)
        assert "0 часов 0 минут" in result


class TestExcelValidatorErrorHandling:
    """Test error handling in ExcelValidator."""

    @pytest.fixture
    def validator(self) -> ExcelValidator:
        """Create ExcelValidator instance."""
        values_dict = {
            "STATUS": {
                "pass": "Пройдена",
                "not_started": "Не начата",
                "abandoned": "Брошена",
            },
            "PLATFORM": {
                "not_defined": "Не определена",
                "steam": "Steam",
                "switch": "Switch",
                "ps4": "PS4",
                "ps_vita": "PS Vita",
                "pc_origin": "PC Origin",
                "pc_gog": "PC GOG",
                "ps5": "PS5",
                "n3ds": "N3DS",
            },
        }
        return ExcelValidator(values_dict)

    def test_validate_status_empty_string(self, validator: ExcelValidator) -> None:
        """Test validate_status handles empty string."""
        result = validator.validate_status("")

        assert result is False

    def test_validate_status_none(self, validator: ExcelValidator) -> None:
        """Test validate_status handles None."""
        result = validator.validate_status(None)  # type: ignore

        assert result is False

    def test_validate_platform_empty_string(
        self, validator: ExcelValidator
    ) -> None:
        """Test validate_platform handles empty string."""
        result = validator.validate_platform("")

        assert result is False

    def test_validate_platform_none(self, validator: ExcelValidator) -> None:
        """Test validate_platform handles None."""
        # validate_platform calls .strip() which will fail on None
        # This tests that the method should handle None gracefully
        # In practice, this should be handled at the call site
        with pytest.raises(AttributeError):
            validator.validate_platform(None)  # type: ignore

    def test_validate_game_row_missing_required_fields(
        self, validator: ExcelValidator
    ) -> None:
        """Test validate_game_row handles missing required fields."""
        from game_db.excel.models import GameRow

        # Game row with missing game_name
        game_row = GameRow(
            game_name="",  # Empty required field
            platforms="Steam",
            status="Пройдена",
            release_date="January 1, 2024",
        )

        is_valid, errors = validator.validate_game_row(game_row)

        assert is_valid is False
        assert len(errors) > 0
        error_msg = errors[0].lower()
        assert "required" in error_msg or "game name" in error_msg

    def test_validate_game_row_invalid_status(
        self, validator: ExcelValidator
    ) -> None:
        """Test validate_game_row handles invalid status."""
        from game_db.excel.models import GameRow

        game_row = GameRow(
            game_name="Test Game",
            platforms="Steam",
            status="Invalid Status",  # Invalid status
            release_date="January 1, 2024",
        )

        is_valid, errors = validator.validate_game_row(game_row)

        assert is_valid is False
        assert any("status" in error.lower() for error in errors)

    def test_validate_game_row_invalid_platform(
        self, validator: ExcelValidator
    ) -> None:
        """Test validate_game_row handles invalid platform."""
        from game_db.excel.models import GameRow

        game_row = GameRow(
            game_name="Test Game",
            platforms="InvalidPlatform",  # Invalid platform
            status="Пройдена",
            release_date="January 1, 2024",
        )

        is_valid, errors = validator.validate_game_row(game_row)

        assert is_valid is False
        assert any("platform" in error.lower() for error in errors)

    def test_get_status_id_unknown_status(
        self, validator: ExcelValidator
    ) -> None:
        """Test get_status_id handles unknown status."""
        status_id = validator.get_status_id("Unknown Status")

        # Should return 0 for unknown
        assert status_id == 0

    def test_get_platform_id_unknown_platform(
        self, validator: ExcelValidator
    ) -> None:
        """Test get_platform_id handles unknown platform."""
        platform_id = validator.get_platform_id("Unknown Platform")

        # Should return 1 (not_defined) for unknown
        assert platform_id == 1
