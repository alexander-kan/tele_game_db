"""Additional unit tests for callback_handlers module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db.callback_handlers import handle_callback_query
from game_db.config import SettingsConfig, UsersConfig
from game_db.menu_callbacks import CallbackAction
from game_db.security import Security


@pytest.fixture
def admin_security() -> Security:
    """Create Security instance for admin user."""
    users_cfg = UsersConfig(users=["12345"], admins=["12345"])
    return Security(users_cfg)


@pytest.fixture
def user_security() -> Security:
    """Create Security instance for regular user."""
    users_cfg = UsersConfig(users=["12345"], admins=[])
    return Security(users_cfg)


@pytest.fixture
def test_settings() -> SettingsConfig:
    """Create test settings."""
    from pathlib import Path

    from game_db.config import DBFilesConfig, Paths

    paths = Paths(
        backup_dir=Path("/tmp"),
        update_db_dir=Path("/tmp"),
        files_dir=Path("/tmp"),
        sql_root=Path("/tmp"),
        sqlite_db_file=Path("/tmp/test.db"),
        games_excel_file=Path("/tmp/test.xlsx"),
    )
    db_files = DBFilesConfig(
        sql_games=Path("/tmp/sql_games.sql"),
        sql_games_on_platforms=Path("/tmp/sql_games_on_platforms.sql"),
        sql_dictionaries=Path("/tmp/sql_dictionaries.sql"),
        sql_drop_tables=Path("/tmp/sql_drop_tables.sql"),
        sql_create_tables=Path("/tmp/sql_create_tables.sql"),
        sqlite_db_file=Path("/tmp/test.db"),
    )
    return SettingsConfig(paths=paths, db_files=db_files, owner_name="TestOwner")


@pytest.fixture
def mock_bot() -> Mock:
    """Create mock Telegram bot."""
    bot = Mock()
    bot.send_message = Mock()
    bot.edit_message_text = Mock()
    bot.edit_message_reply_markup = Mock()
    bot.answer_callback_query = Mock()
    return bot


@pytest.fixture
def mock_callback_query() -> Mock:
    """Create mock callback query."""
    call = Mock()
    call.id = "callback123"
    call.data = "action:main_menu"
    call.from_user = Mock()
    call.from_user.id = 12345
    call.message = Mock()
    call.message.chat.id = 12345
    call.message.message_id = 1
    return call


@patch("game_db.callback_handlers._handle_steam_games")
def test_handle_callback_query_steam_games(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling STEAM_GAMES callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.STEAM_GAMES, [])

        handle_callback_query(
            mock_callback_query, mock_bot, user_security, test_settings
        )

        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_switch_games")
def test_handle_callback_query_switch_games(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling SWITCH_GAMES callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.SWITCH_GAMES, [])

        handle_callback_query(
            mock_callback_query, mock_bot, user_security, test_settings
        )

        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_games_list")
def test_handle_callback_query_games_list(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling GAMES_LIST callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.GAMES_LIST, ["Steam", "1", "10"])

        handle_callback_query(
            mock_callback_query, mock_bot, user_security, test_settings
        )

        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_statistics")
def test_handle_callback_query_statistics(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling STATISTICS callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.STATISTICS, [])

        handle_callback_query(
            mock_callback_query, mock_bot, user_security, test_settings
        )

        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_commands")
def test_handle_callback_query_commands(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling COMMANDS callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.COMMANDS, [])

        handle_callback_query(
            mock_callback_query, mock_bot, user_security, test_settings
        )

        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_admin_panel")
def test_handle_callback_query_admin_panel(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling ADMIN_PANEL callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.ADMIN_PANEL, [])

        handle_callback_query(
            mock_callback_query, mock_bot, admin_security, test_settings
        )

        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_file_management")
def test_handle_callback_query_file_management(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling FILE_MANAGEMENT callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.FILE_MANAGEMENT, [])

        handle_callback_query(
            mock_callback_query, mock_bot, admin_security, test_settings
        )

        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_sync_menu")
def test_handle_callback_query_sync_menu(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling SYNC_MENU callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.return_value = (CallbackAction.SYNC_MENU, [])

        handle_callback_query(
            mock_callback_query, mock_bot, user_security, test_settings
        )

        mock_handle.assert_called_once()
