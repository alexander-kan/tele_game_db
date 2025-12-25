"""Tests for steam_api module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db.steam_api import SteamAPI
from game_db.types import SteamGame


class TestSteamAPI:
    """Test SteamAPI class."""

    @pytest.fixture
    def steam_api(self) -> SteamAPI:
        """Create SteamAPI instance."""
        return SteamAPI()

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_get_all_games_success(
        self,
        mock_load_tokens: Mock,
        mock_get: Mock,
        steam_api: SteamAPI,
    ) -> None:
        """Test get_all_games with successful API response."""
        # Mock config
        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        # Mock API response
        mock_response = Mock()
        mock_response.text = '{"response": {"games": [{"appid": 123, "name": "Test Game", "playtime_forever": 100}]}}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = steam_api.get_all_games()

        assert len(result) == 1
        assert isinstance(result[0], SteamGame)
        assert result[0].appid == 123
        assert result[0].name == "Test Game"
        assert result[0].playtime_forever == 100

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_get_all_games_with_steamid(
        self,
        mock_load_tokens: Mock,
        mock_get: Mock,
        steam_api: SteamAPI,
    ) -> None:
        """Test get_all_games with custom steamid parameter."""
        mock_config = Mock()
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_response = Mock()
        mock_response.text = '{"response": {"games": []}}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        steam_api.get_all_games("987654321")

        # Verify that custom steamid was used in URL
        call_args = mock_get.call_args
        assert "987654321" in call_args[0][0] or "steamid=987654321" in str(call_args)

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_get_all_games_empty_response(
        self,
        mock_load_tokens: Mock,
        mock_get: Mock,
        steam_api: SteamAPI,
    ) -> None:
        """Test get_all_games with empty games list."""
        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_response = Mock()
        mock_response.text = '{"response": {"games": []}}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = steam_api.get_all_games()

        assert result == []

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_get_all_games_http_error(
        self,
        mock_load_tokens: Mock,
        mock_get: Mock,
        steam_api: SteamAPI,
    ) -> None:
        """Test get_all_games handles HTTP errors."""
        import requests

        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_get.side_effect = requests.RequestException("HTTP Error")

        result = steam_api.get_all_games()

        assert result == []

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_get_all_games_invalid_json(
        self,
        mock_load_tokens: Mock,
        mock_get: Mock,
        steam_api: SteamAPI,
    ) -> None:
        """Test get_all_games handles invalid JSON response."""
        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_response = Mock()
        mock_response.text = "invalid json"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = steam_api.get_all_games()

        assert result == []

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_get_all_games_missing_response_key(
        self,
        mock_load_tokens: Mock,
        mock_get: Mock,
        steam_api: SteamAPI,
    ) -> None:
        """Test get_all_games handles missing response key."""
        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_response = Mock()
        mock_response.text = '{"invalid": "structure"}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = steam_api.get_all_games()

        assert result == []

    @patch("game_db.steam_api.requests.get")
    @patch("game_db.steam_api.load_tokens_config")
    def test_get_all_games_multiple_games(
        self,
        mock_load_tokens: Mock,
        mock_get: Mock,
        steam_api: SteamAPI,
    ) -> None:
        """Test get_all_games with multiple games."""
        mock_config = Mock()
        mock_config.steam_id = "123456789"
        mock_config.steam_key = "test_key"
        mock_load_tokens.return_value = mock_config

        mock_response = Mock()
        mock_response.text = (
            '{"response": {"games": ['
            '{"appid": 1, "name": "Game 1", "playtime_forever": 10},'
            '{"appid": 2, "name": "Game 2", "playtime_forever": 20},'
            '{"appid": 3, "name": "Game 3", "playtime_forever": 30}'
            "]}}"
        )
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = steam_api.get_all_games()

        assert len(result) == 3
        assert result[0].name == "Game 1"
        assert result[1].name == "Game 2"
        assert result[2].name == "Game 3"
