"""Unit tests for Metacritic search functionality."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests
from bs4 import BeautifulSoup

from game_db.metacritic_search import search_metacritic_game_url


class TestSearchMetacriticGameUrl:
    """Test search_metacritic_game_url function."""

    @patch("game_db.metacritic_search.requests.Session")
    def test_search_success_with_result_list(self, mock_session_class: Mock) -> None:
        """Test successful search when results are in <li class="result">."""
        # Mock HTML response with search results
        html_content = """
        <html>
            <body>
                <ul>
                    <li class="result">
                        <a href="/game/pc/test-game">Test Game</a>
                    </li>
                </ul>
            </body>
        </html>
        """

        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode()
        mock_response.url = "https://www.metacritic.com/search/game/test-game/results"
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        result = search_metacritic_game_url("Test Game")

        assert result == "https://www.metacritic.com/game/pc/test-game"
        mock_session.get.assert_called_once()

    @patch("game_db.metacritic_search.requests.Session")
    def test_search_success_with_direct_links(self, mock_session_class: Mock) -> None:
        """Test successful search when results are direct game links."""
        # Mock HTML response with direct game links
        html_content = """
        <html>
            <body>
                <a href="/game/pc/test-game">Test Game</a>
                <a href="/game/switch/another-game">Another Game</a>
            </body>
        </html>
        """

        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode()
        mock_response.url = "https://www.metacritic.com/search/game/test-game/results"
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        result = search_metacritic_game_url("Test Game")

        # Should return first valid game URL found
        assert result is not None
        assert "metacritic.com/game/" in result
        assert result.startswith("https://")
        mock_session.get.assert_called_once()

    @patch("game_db.metacritic_search.requests.Session")
    def test_search_not_found(self, mock_session_class: Mock) -> None:
        """Test search when no results are found."""
        # Mock HTML response without game links
        html_content = """
        <html>
            <body>
                <div>No results found</div>
            </body>
        </html>
        """

        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode()
        mock_response.url = "https://www.metacritic.com/search/game/test-game/results"
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        result = search_metacritic_game_url("Test Game")

        assert result is None

    @patch("game_db.metacritic_search.requests.Session")
    def test_search_http_error(self, mock_session_class: Mock) -> None:
        """Test search handles HTTP errors."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        result = search_metacritic_game_url("Test Game")

        assert result is None

    @patch("game_db.metacritic_search.requests.Session")
    def test_search_connection_error(self, mock_session_class: Mock) -> None:
        """Test search handles connection errors."""
        mock_session = Mock()
        mock_session.get.side_effect = requests.ConnectionError("Connection failed")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        result = search_metacritic_game_url("Test Game")

        assert result is None

    @patch("game_db.metacritic_search.requests.Session")
    def test_search_url_formatting(self, mock_session_class: Mock) -> None:
        """Test that search URL is formatted correctly with hyphens."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body></body></html>"
        mock_response.url = "https://www.metacritic.com/search/game/test-game/results"
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        search_metacritic_game_url("Test Game")

        # Verify URL was formatted with hyphens
        call_args = mock_session.get.call_args
        assert call_args is not None
        url = call_args[0][0]
        assert "test-game" in url or "Test-Game" in url.lower()
        assert " " not in url  # No spaces in URL

    @patch("game_db.metacritic_search.requests.Session")
    def test_search_special_characters(self, mock_session_class: Mock) -> None:
        """Test search handles special characters in game names."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body></body></html>"
        mock_response.url = "https://www.metacritic.com/search/game/test-game-2/results"
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        search_metacritic_game_url("Test: Game 2!")

        # Verify special characters are removed from search term
        call_args = mock_session.get.call_args
        assert call_args is not None
        url = call_args[0][0]
        # Extract search term from URL (part after /search/game/)
        search_term = url.split("/search/game/")[1].split("/")[0]
        assert ":" not in search_term
        assert "!" not in search_term
        assert "test-game-2" in search_term.lower()
