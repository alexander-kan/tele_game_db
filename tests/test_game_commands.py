"""Tests for game-related bot commands."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db.commands import (
    CountGamesCommand,
    CountTimeCommand,
    GetGameCommand,
    SteamGameListCommand,
    SwitchGameListCommand,
)
from game_db.config import SettingsConfig
from game_db.security import Security


@pytest.fixture
def game_commands_settings(test_config: SettingsConfig) -> SettingsConfig:
    """Reuse generic test_config for game commands."""
    return test_config


def test_get_game_command_database_error(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """GetGameCommand should handle DatabaseError and send error message."""
    from game_db import texts

    mock_message.text = "getgame Test Game"

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        from game_db.exceptions import DatabaseError

        mock_service.query_game.side_effect = DatabaseError("DB error")

        command = GetGameCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    mock_bot.send_message.assert_called()
    # Should send generic GAME_QUERY_ERROR
    args, kwargs = mock_bot.send_message.call_args
    assert texts.GAME_QUERY_ERROR in args or texts.GAME_QUERY_ERROR in str(
        kwargs
    )


def test_get_game_command_multiple_results(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """GetGameCommand formats multiple games when many results."""
    mock_message.text = "getgame Test"

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        mock_service.query_game.return_value = [
            ("Game 1",),
            ("Game 2",),
        ]

        command = GetGameCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    mock_bot.send_message.assert_called_once()


def test_get_game_command_not_found(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """GetGameCommand returns GAME_NOT_FOUND when no rows."""
    from game_db import texts

    mock_message.text = "getgame Missing"

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        mock_service.query_game.return_value = []

        command = GetGameCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    args, kwargs = mock_bot.send_message.call_args
    assert texts.GAME_NOT_FOUND in args or texts.GAME_NOT_FOUND in str(kwargs)


def test_get_game_command_hash_selector(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """GetGameCommand selects specific game when name ends with #."""
    mock_message.text = "getgame Game 1 #"

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        mock_service.query_game.return_value = [
            ("Game 1",),
            ("Game 2",),
        ]

        command = GetGameCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    mock_bot.send_message.assert_called_once()


def test_steam_game_list_command(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """SteamGameListCommand delegates to handlers.game_list."""
    mock_message.from_user.id = mock_message.chat.id
    mock_message.text = "Steam,0,10"

    # game_list lives in game_db.handlers and is imported locally
    with patch("game_db.handlers.game_list") as mock_game_list:
        mock_game_list.return_value = (mock_message, "Games list")

        command = SteamGameListCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    mock_game_list.assert_called_once()
    mock_bot.send_message.assert_called_once()


def test_switch_game_list_command(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """SwitchGameListCommand delegates to handlers.game_list with Switch."""
    mock_message.from_user.id = mock_message.chat.id
    mock_message.text = "Switch,0,10"

    with patch("game_db.handlers.game_list") as mock_game_list:
        mock_game_list.return_value = (mock_message, "Games list")

        command = SwitchGameListCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    mock_game_list.assert_called_once()
    mock_bot.send_message.assert_called_once()


def test_count_games_command_success(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """CountGamesCommand aggregates counts for all platforms."""
    mock_message.from_user.id = mock_message.chat.id

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        mock_service.get_platforms.return_value = ["Steam", "Switch"]
        mock_service.count_complete_games.return_value = 5

        command = CountGamesCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    assert mock_service.count_complete_games.call_count == 2
    mock_bot.send_message.assert_called_once()


def test_count_games_command_with_errors(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """CountGamesCommand handles DatabaseError per-platform."""
    mock_message.from_user.id = mock_message.chat.id

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        from game_db.exceptions import DatabaseError

        mock_service.get_platforms.return_value = ["Steam", "Switch"]
        mock_service.count_complete_games.side_effect = [
            DatabaseError("failed"),
            3,
        ]

        command = CountGamesCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    mock_bot.send_message.assert_called_once()


def test_count_time_command_success(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """CountTimeCommand aggregates per-platform and total times."""
    mock_message.from_user.id = mock_message.chat.id

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        mock_service.get_platforms.return_value = [
            "Steam",
            "PC GOG",
            "Switch",
        ]
        # New logic: only calls with mode=0, then sums real_time
        mock_service.count_spend_time.side_effect = [
            (1.0, 2.0),  # Steam
            (3.0, 4.0),  # PC GOG
            (None, None),  # Switch
        ]

        command = CountTimeCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    # Should be called once per platform with mode=0
    assert mock_service.count_spend_time.call_count == 3
    mock_bot.send_message.assert_called_once()


def test_count_time_command_with_errors(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    game_commands_settings: SettingsConfig,
) -> None:
    """CountTimeCommand handles DatabaseError gracefully."""
    mock_message.from_user.id = mock_message.chat.id

    with patch("game_db.commands.game_commands.game_service") as mock_service:
        from game_db.exceptions import DatabaseError

        mock_service.get_platforms.return_value = ["Steam"]
        mock_service.count_spend_time.side_effect = DatabaseError("failed")

        command = CountTimeCommand()
        command.execute(
            mock_message, mock_bot, admin_security, game_commands_settings
        )

    mock_bot.send_message.assert_called_once()

