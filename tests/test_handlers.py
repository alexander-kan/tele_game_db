"""Integration tests for handlers with mocked Telegram bot."""

# pylint: disable=redefined-outer-name

from __future__ import annotations

import pathlib
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from game_db import handlers
from game_db.config import SettingsConfig, UsersConfig
from game_db.security import Security

# Ensure project root is on sys.path when running tests directly
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Fixtures are now imported from conftest.py
# mock_bot, mock_message, test_config (as mock_settings), admin_security, user_security


@patch("game_db.handlers.game_service")
def test_handle_text_clear_menu(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
    admin_security: Security,
) -> None:
    """Test handle_text with clear menu command."""
    mock_message.text = "Clear Menu"

    handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

    mock_bot.send_message.assert_called_once()
    # Check that menu cleared message was sent
    call_args = mock_bot.send_message.call_args
    if len(call_args[0]) > 1:
        text_sent = call_args[0][1]
    else:
        text_sent = call_args[1].get("text", "")
    assert "Menu cleared" in str(text_sent)


@patch("game_db.commands.game_commands.game_service")
def test_handle_text_getgame(
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
    admin_security: Security,
) -> None:
    """Test handle_text with getgame command."""
    mock_message.text = "getgame Test Game"
    mock_game_service.query_game.return_value = [
        (
            "Test Game",
            "Completed",
            "Steam",
            "8",
            "10.5",
            "7.5",
            "8",
            "https://metacritic.com",
            "https://youtube.com",
            "12.0",
            "2024-01-01",
        )
    ]

    handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

    mock_game_service.query_game.assert_called_once_with("getgame Test Game")
    mock_bot.send_message.assert_called_once()


@patch("game_db.handlers.game_service")
def test_handle_text_unauthorized_user(
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
) -> None:
    """Test handle_text rejects unauthorized users."""
    users_cfg = UsersConfig(users=["99999"], admins=["99999"])
    security = Security(users_cfg)
    mock_message.text = "getgame Test"

    handlers.handle_text(mock_message, mock_bot, security, test_config)

    # Should send private bot message
    mock_bot.send_message.assert_called()
    mock_game_service.query_game.assert_not_called()


@patch("game_db.commands.game_commands.game_service")
def test_handle_text_count_games(
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
    admin_security: Security,
) -> None:
    """Test handle_text with count games command."""
    mock_message.text = "How many games Alexander completed"
    # Mock get_platforms to return test platforms
    mock_game_service.get_platforms.return_value = [
        "Steam",
        "Switch",
        "PS4",
        "PS5",
    ]
    mock_game_service.count_complete_games.return_value = 5

    handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

    # Should call count_complete_games for each platform
    assert mock_game_service.count_complete_games.call_count > 0
    mock_bot.send_message.assert_called_once()


@patch("game_db.handlers.game_service")
def test_handle_text_routing_table(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
    admin_security: Security,
) -> None:
    """Test that routing table works for exact matches."""
    test_cases = [
        "Back to Main Menu",
        "File Management Menu",
        "Game Lists",
        "Show Available Commands",
    ]

    for text in test_cases:
        mock_message.text = text
        mock_bot.reset_mock()

        handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

        # Should send a message for each command
        assert mock_bot.send_message.called, f"Failed for command: {text}"


@patch("game_db.handlers.game_service")
def test_handle_start_help(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
) -> None:
    """Test handle_start_help command."""
    handlers.handle_start_help(mock_message, mock_bot, admin_security)

    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args
    assert call_args[0][0] == mock_message.chat.id


@patch("game_db.handlers.game_service")
def test_handle_start_help_unauthorized(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
) -> None:
    """Test handle_start_help rejects unauthorized users."""
    users_cfg = UsersConfig(users=["99999"], admins=["99999"])
    security = Security(users_cfg)

    handlers.handle_start_help(mock_message, mock_bot, security)

    mock_bot.send_message.assert_called_once()
    # Should send private bot message
    call_args = mock_bot.send_message.call_args
    assert call_args[0][0] == mock_message.chat.id


@patch("game_db.handlers.game_service")
def test_get_platforms_database_error_returns_default(
    mock_game_service: Mock,
) -> None:
    """_get_platforms falls back to DEFAULT_PLATFORMS on DatabaseError."""
    from game_db.config import DEFAULT_PLATFORMS
    from game_db.exceptions import DatabaseError

    mock_game_service.get_platforms.side_effect = DatabaseError("DB error")

    platforms = handlers._get_platforms()
    assert platforms == DEFAULT_PLATFORMS


def test_game_list_success(mock_message: Mock) -> None:
    """game_list returns formatted list and updates message text."""
    mock_message.text = "Steam,0,10"

    with patch("game_db.handlers.game_service") as mock_game_service:
        mock_game_service.get_next_game_list.return_value = [
            ("Game 1", None, None, None),
            ("Game 2", None, None, None),
        ]

        updated_message, game_list_text = handlers.game_list(mock_message, "Steam")

    assert "Game" in game_list_text
    # Offset should be incremented by 10
    assert updated_message.text.startswith("Steam,10,10")


def test_game_list_invalid_input_returns_empty(mock_message: Mock) -> None:
    """game_list handles invalid input format gracefully."""
    mock_message.text = "Steam"  # Not enough comma‑separated parts

    updated_message, game_list_text = handlers.game_list(mock_message, "Steam")

    assert updated_message is mock_message
    assert game_list_text == ""


def test_update_db_recreate_success(
    mock_bot: Mock,
    mock_message_with_document: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
    tmp_path: Path,
) -> None:
    """update_db recreates DB and moves uploaded file on success."""
    # Ensure update_db_dir and backup_dir exist and contain the file
    update_dir = test_config.paths.update_db_dir
    backup_dir = test_config.paths.backup_dir
    update_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)

    uploaded_path = update_dir / mock_message_with_document.document.file_name
    uploaded_path.write_text("dummy")

    with patch("game_db.handlers.db_module.ChangeDB") as mock_change_db:
        instance = mock_change_db.return_value
        instance.recreate_db.return_value = True

        handlers.update_db(
            mock_message_with_document,
            mode="recreate",
            bot=mock_bot,
            sec=admin_security,
            settings=test_config,
        )

    # File should be moved to backup_dir/games.xlsx
    backup_file = backup_dir / "games.xlsx"
    assert backup_file.exists()
    mock_bot.send_message.assert_called()


def test_update_db_non_admin_rejected(
    mock_bot: Mock,
    mock_message_with_document: Mock,
    user_security: Security,
    test_config: SettingsConfig,
) -> None:
    """update_db rejects non‑admin users."""
    handlers.update_db(
        mock_message_with_document,
        mode="recreate",
        bot=mock_bot,
        sec=user_security,
        settings=test_config,
    )

    mock_bot.send_message.assert_called_once()


def test_handle_sync_steam_file_not_found(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
) -> None:
    """_handle_sync_steam reports missing Excel file."""
    # Ensure the expected games_excel_file does not exist
    if test_config.paths.games_excel_file.exists():
        test_config.paths.games_excel_file.unlink()

    handlers._handle_sync_steam(mock_message, mock_bot, admin_security, test_config)

    mock_bot.send_message.assert_called_once()


def test_handle_sync_steam_success(
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
) -> None:
    """_handle_sync_steam calls ChangeDB.synchronize_steam_games."""
    # Create dummy Excel file
    games_excel = test_config.paths.games_excel_file
    games_excel.parent.mkdir(parents=True, exist_ok=True)
    games_excel.write_text("dummy")

    with patch("game_db.handlers.db_module.ChangeDB") as mock_change_db:
        instance = mock_change_db.return_value
        instance.synchronize_steam_games.return_value = (True, [])

        handlers._handle_sync_steam(mock_message, mock_bot, admin_security, test_config)

    instance.synchronize_steam_games.assert_called_once()
    mock_bot.send_message.assert_called()


@patch("game_db.handlers.game_service")
def test_handle_file_upload_admin(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message_with_document: Mock,
    test_config: SettingsConfig,
    admin_security: Security,
) -> None:
    """Test handle_file_upload for admin user."""
    mock_bot.get_file.return_value = Mock(file_path="test.xlsx")
    mock_bot.download_file.return_value = b"test content"

    handlers.handle_file_upload(
        mock_message_with_document, mock_bot, admin_security, test_config
    )

    # Should attempt to download file
    mock_bot.get_file.assert_called_once()


@patch("game_db.handlers.game_service")
def test_handle_file_upload_non_admin(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message_with_document: Mock,
    test_config: SettingsConfig,
    user_security: Security,
) -> None:
    """Test handle_file_upload rejects non-admin users."""
    handlers.handle_file_upload(
        mock_message_with_document, mock_bot, user_security, test_config
    )

    # Should send permission denied message
    mock_bot.send_message.assert_called_once()
    mock_bot.get_file.assert_not_called()


@patch("game_db.handlers.game_service")
def test_handle_file_upload_no_document(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
    admin_security: Security,
) -> None:
    """Test handle_file_upload handles missing document."""
    mock_message.document = None

    handlers.handle_file_upload(mock_message, mock_bot, admin_security, test_config)

    # Should send error message
    mock_bot.send_message.assert_called_once()
    mock_bot.get_file.assert_not_called()


@patch("game_db.handlers.game_service")
def test_handle_file_upload_invalid_filename(
    _mock_game_service: Mock,
    mock_bot: Mock,
    mock_message_with_document: Mock,
    test_config: SettingsConfig,
    admin_security: Security,
) -> None:
    """Test handle_file_upload rejects invalid file names."""
    mock_message_with_document.document.file_name = "../../etc/passwd"

    handlers.handle_file_upload(
        mock_message_with_document, mock_bot, admin_security, test_config
    )

    # Should send error message
    mock_bot.send_message.assert_called_once()
    mock_bot.get_file.assert_not_called()
