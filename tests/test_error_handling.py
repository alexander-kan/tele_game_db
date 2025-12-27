"""Tests for error handling across the application."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from game_db.exceptions import (
    DatabaseConnectionError,
    DatabaseError,
    DatabaseQueryError,
    SQLFileNotFoundError,
)
from game_db.repositories.game_repository import GameRepository
from game_db.services import game_service

pytestmark = pytest.mark.error_handling


class TestDatabaseErrorHandling:
    """Test database error handling."""

    def test_repository_connection_error(self, tmp_path: Path) -> None:
        """Test GameRepository handles connection errors."""
        # SQLite creates files automatically, so test with a read-only directory
        # or test that query fails on empty database
        invalid_db = tmp_path / "empty.db"
        invalid_db.touch()

        repo = GameRepository(invalid_db)

        # Try to execute a query - should raise DatabaseQueryError
        # because table doesn't exist (connection succeeds,
        # but query fails)
        with pytest.raises(DatabaseQueryError):
            repo.query_game("test")

    def test_repository_query_error(self, temp_db: Path) -> None:
        """Test GameRepository handles query errors."""
        repo = GameRepository(temp_db)

        # Try to execute invalid SQL
        with pytest.raises(DatabaseQueryError):
            repo._execute_query("INVALID SQL SYNTAX !!!")

    def test_repository_missing_sql_file(self, tmp_path: Path) -> None:
        """Test GameRepository raises error for missing SQL files."""
        # Create a database but don't create SQL files
        db_path = tmp_path / "test.db"
        db_path.touch()

        # Mock PROJECT_ROOT to point to directory without SQL files
        with patch("game_db.repositories.game_repository.PROJECT_ROOT", tmp_path):
            with pytest.raises(SQLFileNotFoundError):
                GameRepository(db_path)

    def test_game_service_database_error_propagation(self, temp_db: Path) -> None:
        """Test that game_service propagates database errors."""
        repo = GameRepository(temp_db)

        # Mock repository to raise DatabaseError
        with patch.object(repo, "query_game") as mock_query:
            mock_query.side_effect = DatabaseError("Test error")

            with patch("game_db.services.game_service._repository", repo):
                with pytest.raises(DatabaseError):
                    game_service.query_game("test game")

    def test_get_platforms_database_error(self, temp_db: Path) -> None:
        """Test get_platforms handles database errors."""
        repo = GameRepository(temp_db)

        # Mock repository to raise DatabaseError
        with patch.object(repo, "get_platforms") as mock_get:
            mock_get.side_effect = DatabaseError("Connection failed")

            with patch("game_db.services.game_service._repository", repo):
                with pytest.raises(DatabaseError):
                    game_service.get_platforms()


class TestMissingDataHandling:
    """Test handling of missing data."""

    def test_query_game_empty_result(self, temp_db: Path) -> None:
        """Test query_game handles empty results."""
        repo = GameRepository(temp_db)

        # Query for non-existent game
        results = repo.query_game("NonExistentGame12345")

        assert results == []

    def test_count_complete_games_empty_platform(self, temp_db: Path) -> None:
        """Test count_complete_games handles empty platform."""
        repo = GameRepository(temp_db)

        # Count for platform with no games
        count = repo.count_complete_games("NonExistentPlatform")

        assert count == 0

    def test_get_platforms_empty_database(self, empty_db: Path) -> None:
        """Test get_platforms handles empty database."""
        repo = GameRepository(empty_db)

        platforms = repo.get_platforms()

        assert platforms == []

    def test_count_spend_time_no_data(self, temp_db: Path) -> None:
        """Test count_spend_time handles missing time data."""
        repo = GameRepository(temp_db)

        # Count time for platform with no time data
        expected, real = repo.count_spend_time("NonExistentPlatform", mode=0)

        # Should return None or 0, not raise error
        assert expected is None or expected == 0
        assert real is None or real == 0


class TestInvalidInputHandling:
    """Test handling of invalid input data."""

    def test_query_game_empty_string(self, temp_db: Path) -> None:
        """Test query_game handles empty string."""
        repo = GameRepository(temp_db)

        # Empty string should not crash
        results = repo.query_game("")

        assert isinstance(results, list)

    def test_query_game_special_characters(self, temp_db: Path) -> None:
        """Test query_game handles special characters."""
        repo = GameRepository(temp_db)

        # SQL injection attempt
        results = repo.query_game("'; DROP TABLE games; --")

        # Should not crash, may return empty results
        assert isinstance(results, list)

    def test_count_complete_games_invalid_platform(self, temp_db: Path) -> None:
        """Test count_complete_games handles invalid platform name."""
        repo = GameRepository(temp_db)

        # Invalid platform with special characters
        count = repo.count_complete_games("Invalid/Platform\\Name")

        # Should not crash
        assert isinstance(count, int)

    def test_get_next_game_list_negative_values(self, temp_db: Path) -> None:
        """Test get_next_game_list handles negative values."""
        repo = GameRepository(temp_db)

        # Negative from_row and how_much_row
        results = repo.get_next_game_list(-1, -10, "Steam")

        # Should handle gracefully
        assert isinstance(results, list)

    def test_get_next_game_list_zero_values(self, temp_db: Path) -> None:
        """Test get_next_game_list handles zero values."""
        repo = GameRepository(temp_db)

        # Zero how_much_row
        results = repo.get_next_game_list(0, 0, "Steam")

        # Should handle gracefully
        assert isinstance(results, list)


class TestExternalAPIErrorHandling:
    """Test handling of external API errors."""

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_steam_api_timeout(self, mock_load_tokens: Mock, mock_get: Mock) -> None:
        """Test SteamAPI handles timeout errors."""
        import requests

        from game_db.steam_api import SteamAPI

        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_get.side_effect = requests.Timeout("Request timeout")

        api = SteamAPI()
        result = api.get_all_games()

        assert result == []

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_steam_api_connection_error(
        self, mock_load_tokens: Mock, mock_get: Mock
    ) -> None:
        """Test SteamAPI handles connection errors."""
        import requests

        from game_db.steam_api import SteamAPI

        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_get.side_effect = requests.ConnectionError("Connection failed")

        api = SteamAPI()
        result = api.get_all_games()

        assert result == []


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_query_game_very_long_name(self, temp_db: Path) -> None:
        """Test query_game handles very long game names."""
        repo = GameRepository(temp_db)

        # Very long game name
        long_name = "A" * 1000
        results = repo.query_game(long_name)

        assert isinstance(results, list)

    def test_get_next_game_list_large_values(self, temp_db: Path) -> None:
        """Test get_next_game_list handles very large values."""
        repo = GameRepository(temp_db)

        # Very large from_row and how_much_row
        results = repo.get_next_game_list(1000000, 1000000, "Steam")

        # Should handle gracefully
        assert isinstance(results, list)

    def test_count_spend_time_very_large_mode(self, temp_db: Path) -> None:
        """Test count_spend_time handles invalid mode values."""
        repo = GameRepository(temp_db)

        # Invalid mode value
        expected, real = repo.count_spend_time("Steam", mode=999)

        # Should handle gracefully
        assert expected is None or isinstance(expected, (int, float))
        assert real is None or isinstance(real, (int, float))

    def test_repository_with_nonexistent_db_path(self, tmp_path: Path) -> None:
        """Test GameRepository with non-existent database path."""
        nonexistent_db = tmp_path / "nonexistent" / "db" / "games.db"

        # Should not raise error on initialization
        repo = GameRepository(nonexistent_db)

        # But should raise error when trying to query
        with pytest.raises(DatabaseConnectionError):
            repo.query_game("test")

    def test_get_platforms_with_sql_injection_attempt(self, temp_db: Path) -> None:
        """Test get_platforms is safe from SQL injection."""
        repo = GameRepository(temp_db)

        # The method doesn't take user input, but test that it works correctly
        platforms = repo.get_platforms()

        # Should return list of platform names
        assert isinstance(platforms, list)
        assert all(isinstance(p, str) for p in platforms)

    def test_query_game_with_unicode(self, temp_db: Path) -> None:
        """Test query_game handles unicode characters."""
        repo = GameRepository(temp_db)

        # Unicode game name
        results = repo.query_game("Test 🎮 游戏")

        assert isinstance(results, list)

    def test_count_complete_games_unicode_platform(self, temp_db: Path) -> None:
        """Test count_complete_games handles unicode platform names."""
        repo = GameRepository(temp_db)

        # Unicode platform name
        count = repo.count_complete_games("Platform🎮")

        assert isinstance(count, int)

    def test_repository_sql_file_validation_on_init(self, tmp_path: Path) -> None:
        """Test that repository validates SQL files on initialization."""
        db_path = tmp_path / "test.db"
        db_path.touch()

        # Create queries directory but without required files
        queries_dir = tmp_path / "sql_querry" / "queries"
        queries_dir.mkdir(parents=True)

        with patch("game_db.repositories.game_repository.PROJECT_ROOT", tmp_path):
            with pytest.raises(SQLFileNotFoundError):
                GameRepository(db_path)


class TestServiceLayerErrorHandling:
    """Test error handling in service layer."""

    def test_query_game_wraps_generic_exceptions(self) -> None:
        """Test that game_service wraps generic exceptions."""
        from game_db.services import game_service as gs_module

        original_repo = gs_module._repository
        try:
            with patch.object(original_repo, "query_game") as mock_query:
                mock_query.side_effect = ValueError("Unexpected error")

                with pytest.raises(DatabaseError) as exc_info:
                    game_service.query_game("test")

                # Check that error message indicates wrapping
                assert "Unexpected error" in str(exc_info.value)
                # original_error should be set via 'from e'
                assert exc_info.value.__cause__ is not None
                assert isinstance(exc_info.value.__cause__, ValueError)
        finally:
            gs_module._repository = original_repo

    def test_count_complete_games_wraps_exceptions(self) -> None:
        """Test that count_complete_games wraps exceptions."""
        from game_db.services import game_service as gs_module

        original_repo = gs_module._repository
        try:
            with patch.object(original_repo, "count_complete_games") as mock_count:
                mock_count.side_effect = RuntimeError("Unexpected error")

                with pytest.raises(DatabaseError) as exc_info:
                    game_service.count_complete_games("Steam")

                # Check that error message indicates wrapping
                assert "Unexpected error" in str(exc_info.value)
                # original_error should be set via 'from e'
                assert exc_info.value.__cause__ is not None
                assert isinstance(exc_info.value.__cause__, RuntimeError)
        finally:
            gs_module._repository = original_repo

    def test_get_platforms_handles_exceptions(self) -> None:
        """Test that get_platforms handles exceptions."""
        from game_db.services import game_service as gs_module

        original_repo = gs_module._repository
        try:
            with patch.object(original_repo, "get_platforms") as mock_get:
                mock_get.side_effect = DatabaseError("DB error")

                with pytest.raises(DatabaseError):
                    game_service.get_platforms()
        finally:
            gs_module._repository = original_repo

    def test_count_spend_time_handles_exceptions(self) -> None:
        """Test that count_spend_time handles exceptions."""
        from game_db.services import game_service as gs_module

        original_repo = gs_module._repository
        try:
            with patch.object(original_repo, "count_spend_time") as mock_count:
                mock_count.side_effect = DatabaseQueryError(
                    "Query failed", sql="SELECT ..."
                )

                with pytest.raises(DatabaseQueryError):
                    game_service.count_spend_time("Steam", mode=0)
        finally:
            gs_module._repository = original_repo
