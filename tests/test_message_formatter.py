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
            "Completed",
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
        assert "Completed" in result
        assert "Steam" in result
        assert "8.0" in result
        assert "50" in result  # float_to_time converts "50.0" to "50 hours 0 minutes"
        assert "7.5" in result
        assert "9.0" in result
        assert "https://metacritic.com" in result
        assert "https://youtube.com" in result

    def test_format_game_info_missing_time(self) -> None:
        """Test format_game_info with missing time data."""
        game_row = (
            "Test Game",
            "Not Started",
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
        # Check for English text indicating missing time data
        assert "not specified" in result or "never played" in result

    def test_format_completed_games_stats_with_owner_name(self) -> None:
        """Test format_completed_games_stats with custom owner name."""
        platform_counts = {"Steam": 45, "Switch": 12, "PS4": 8}
        owner_name = "Alexander"

        result = MessageFormatter.format_completed_games_stats(
            platform_counts, owner_name
        )

        assert f"How many games {owner_name} completed" in result
        assert "Steam: 45" in result
        assert "Switch: 12" in result
        assert "PS4: 8" in result

    def test_format_time_stats_with_owner_name(self) -> None:
        """Test format_time_stats with custom owner name."""
        platform_times = {
            "Steam": (100.0, 120.5),
            "Switch": (50.0, 45.0),
        }
        owner_name = "Alexander"
        total_real_seconds = (120.5 + 45.0) * 3600

        result = MessageFormatter.format_time_stats(
            platform_times, total_real_seconds, owner_name, show_total=True
        )

        assert f"How much time {owner_name} spent on games" in result
        assert "Steam:" in result
        assert "Switch:" in result
        assert "Total time spent:" in result

    def test_format_time_stats_with_different_owner_name(self) -> None:
        """Test format_time_stats with different owner name."""
        platform_times = {"Steam": (100.0, 120.5)}
        owner_name = "John"
        total_real_seconds = 120.5 * 3600

        result = MessageFormatter.format_time_stats(
            platform_times, total_real_seconds, owner_name, show_total=False
        )

        assert f"How much time {owner_name} spent on games" in result
        assert "Steam:" in result
        assert "Total time spent:" not in result  # show_total=False

    def test_format_next_game_message_empty(self) -> None:
        """Test format_next_game_message with empty list."""
        result = MessageFormatter.format_next_game_message([])
        assert result == "Game list is empty."

    def test_format_next_game_message_with_games(self) -> None:
        """Test format_next_game_message with games."""
        from game_db.types import GameListItem

        games = [
            GameListItem(
                game_name="Test Game 1",
                press_score="8.5",
                average_time_beat=None,
                trailer_url=None,
            ),
            GameListItem(
                game_name="Test Game 2",
                press_score=None,
                average_time_beat=None,
                trailer_url=None,
            ),
        ]

        result = MessageFormatter.format_next_game_message(games)

        assert "Test Game 1" in result
        assert "Test Game 2" in result
        assert "8.5" in result  # press_score
        assert "not specified" in result

    def test_format_steam_sync_missing_games_empty(self) -> None:
        """Test format_steam_sync_missing_games with empty list."""
        result = MessageFormatter.format_steam_sync_missing_games([])
        assert result == ""

    def test_format_steam_sync_missing_games_with_matches(self) -> None:
        """Test format_steam_sync_missing_games with matches."""
        from game_db.similarity_search import SimilarityMatch

        matches = [
            SimilarityMatch(
                original="Game 1",
                closest_match="Game 1 Match",
                distance=1,
                score=0.95,
            ),
            SimilarityMatch(
                original="Game 2",
                closest_match=None,
                distance=5,
                score=0.3,
            ),
        ]

        result = MessageFormatter.format_steam_sync_missing_games(matches)

        assert "Game 1" in result
        assert "Game 1 Match" in result
        assert "Game 2" in result
        assert "closestMatch: null" in result
        assert "distance: 1" in result
        assert "score: 0.95" in result

    def test_format_steam_sync_missing_games_no_matches(self) -> None:
        """Test format_steam_sync_missing_games with no matches."""
        from game_db.similarity_search import SimilarityMatch

        matches = [
            SimilarityMatch(
                original="Game 1",
                closest_match=None,
                distance=10,
                score=0.1,
            ),
            SimilarityMatch(
                original="Game 2",
                closest_match=None,
                distance=8,
                score=0.2,
            ),
        ]

        result = MessageFormatter.format_steam_sync_missing_games(matches)

        assert "Game 1" in result
        assert "Game 2" in result
        assert "closestMatch: null" in result
