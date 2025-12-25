"""Tests for genres module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db.genres import extract_genre_from_metacritic


class TestExtractGenreFromMetacritic:
    """Test extract_genre_from_metacritic function."""

    @patch("game_db.genres.MetaCriticScraper")
    def test_extract_genre_success_with_genre_block(
        self, mock_scraper_class: Mock
    ) -> None:
        """Test extract_genre_from_metacritic with successful extraction."""
        # Mock MetaCriticScraper instance
        mock_scraper = Mock()
        mock_scraper.game = {"genre": "Action, Adventure"}
        mock_scraper_class.return_value = mock_scraper

        result = extract_genre_from_metacritic("https://metacritic.com/game/test")

        assert result == "Action, Adventure"
        mock_scraper_class.assert_called_once_with("https://metacritic.com/game/test")

    @patch("game_db.genres.MetaCriticScraper")
    def test_extract_genre_success_with_alt_section(
        self, mock_scraper_class: Mock
    ) -> None:
        """Test extract_genre_from_metacritic with alternative section."""
        # Mock MetaCriticScraper instance
        mock_scraper = Mock()
        mock_scraper.game = {"genre": "RPG, Strategy"}
        mock_scraper_class.return_value = mock_scraper

        result = extract_genre_from_metacritic("https://metacritic.com/game/test")

        assert result == "RPG, Strategy"

    @patch("game_db.genres.MetaCriticScraper")
    def test_extract_genre_not_found(self, mock_scraper_class: Mock) -> None:
        """Test extract_genre_from_metacritic when genre not found."""
        # Mock MetaCriticScraper instance with empty genre
        mock_scraper = Mock()
        mock_scraper.game = {"genre": ""}
        mock_scraper_class.return_value = mock_scraper

        result = extract_genre_from_metacritic("https://metacritic.com/game/test")

        assert result is None

    @patch("game_db.genres.MetaCriticScraper")
    def test_extract_genre_http_error(self, mock_scraper_class: Mock) -> None:
        """Test extract_genre_from_metacritic handles HTTP errors."""
        # Mock MetaCriticScraper to raise exception
        mock_scraper_class.side_effect = Exception("Connection error")

        result = extract_genre_from_metacritic("https://metacritic.com/game/test")

        assert result is None

    @patch("game_db.genres.MetaCriticScraper")
    def test_extract_genre_non_200_status(
        self, mock_scraper_class: Mock
    ) -> None:
        """Test extract_genre_from_metacritic handles errors gracefully."""
        # Mock MetaCriticScraper instance with no genre key
        mock_scraper = Mock()
        mock_scraper.game = {}
        mock_scraper_class.return_value = mock_scraper

        result = extract_genre_from_metacritic("https://metacritic.com/game/test")

        assert result is None

    @patch("game_db.genres.MetaCriticScraper")
    def test_extract_genre_case_insensitive(
        self, mock_scraper_class: Mock
    ) -> None:
        """Test extract_genre_from_metacritic extracts genre correctly."""
        # Mock MetaCriticScraper instance
        mock_scraper = Mock()
        mock_scraper.game = {"genre": "Action, RPG"}
        mock_scraper_class.return_value = mock_scraper

        result = extract_genre_from_metacritic("https://metacritic.com/game/test")

        # The function should extract the genre
        assert result is not None
        assert "Action" in result
        assert "RPG" in result

    @patch("game_db.genres.MetaCriticScraper")
    def test_extract_genre_with_whitespace(
        self, mock_scraper_class: Mock
    ) -> None:
        """Test extract_genre_from_metacritic handles whitespace correctly."""
        # Mock MetaCriticScraper instance with whitespace
        mock_scraper = Mock()
        mock_scraper.game = {"genre": "   Action  ,  Adventure  "}
        mock_scraper_class.return_value = mock_scraper

        result = extract_genre_from_metacritic("https://metacritic.com/game/test")

        # Should extract and strip whitespace
        assert result == "Action  ,  Adventure"  # Stripped, but commas remain
        assert "Action" in result
        assert "Adventure" in result
