"""Unit tests for callback_handlers module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db.callback_handlers import (
    _safe_answer_callback_query,
    _send_menu_at_bottom,
    handle_callback_query,
)
from game_db.config import SettingsConfig, UsersConfig
from game_db.security import Security
import telebot
from telebot.apihelper import ApiTelegramException


@pytest.fixture
def mock_bot() -> Mock:
    """Create mock Telegram bot."""
    bot = Mock()
    bot.send_message = Mock()
    bot.answer_callback_query = Mock()
    bot.edit_message_text = Mock()
    bot.edit_message_reply_markup = Mock()
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
    from game_db.config import DBFilesConfig, Paths
    from pathlib import Path
    
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


def test_safe_answer_callback_query_success(mock_bot: Mock) -> None:
    """Test successful callback query answer."""
    _safe_answer_callback_query(mock_bot, "callback123", "Test message")
    
    mock_bot.answer_callback_query.assert_called_once_with(
        "callback123", text="Test message", show_alert=False
    )


def test_safe_answer_callback_query_expired(mock_bot: Mock) -> None:
    """Test handling expired callback query."""
    error = ApiTelegramException(
        "Bad Request: query is too old and response timeout expired",
        result=False,
        result_json={"ok": False, "error_code": 400, "description": "query is too old"}
    )
    mock_bot.answer_callback_query.side_effect = error
    
    # Should not raise exception
    _safe_answer_callback_query(mock_bot, "callback123", "Test message")
    
    mock_bot.answer_callback_query.assert_called_once()


def test_safe_answer_callback_query_invalid_id(mock_bot: Mock) -> None:
    """Test handling invalid callback query ID."""
    error = ApiTelegramException(
        "Bad Request: query ID is invalid",
        result=False,
        result_json={"ok": False, "error_code": 400, "description": "query ID is invalid"}
    )
    mock_bot.answer_callback_query.side_effect = error
    
    # Should not raise exception
    _safe_answer_callback_query(mock_bot, "callback123", "Test message")
    
    mock_bot.answer_callback_query.assert_called_once()


def test_safe_answer_callback_query_other_error(mock_bot: Mock) -> None:
    """Test handling other API errors."""
    error = ApiTelegramException(
        "Bad Request: some other error",
        result=False,
        result_json={"ok": False, "error_code": 400, "description": "some other error"}
    )
    mock_bot.answer_callback_query.side_effect = error
    
    # Should not raise exception, but should log warning
    _safe_answer_callback_query(mock_bot, "callback123", "Test message")
    
    mock_bot.answer_callback_query.assert_called_once()


def test_send_menu_at_bottom_with_text(mock_bot: Mock) -> None:
    """Test sending menu with custom text."""
    from game_db.inline_menu import InlineMenu
    from game_db.config import UsersConfig
    from game_db.security import Security
    
    security = Security(UsersConfig(users=["12345"], admins=["12345"]))
    menu = InlineMenu.main_menu(security, 12345)
    
    _send_menu_at_bottom(mock_bot, 12345, menu, "Custom text")
    
    mock_bot.send_message.assert_called_once_with(
        12345, "Custom text", reply_markup=menu
    )


def test_send_menu_at_bottom_without_text(mock_bot: Mock) -> None:
    """Test sending menu without custom text."""
    from game_db.inline_menu import InlineMenu
    from game_db.config import UsersConfig
    from game_db.security import Security
    
    security = Security(UsersConfig(users=["12345"], admins=["12345"]))
    menu = InlineMenu.main_menu(security, 12345)
    
    _send_menu_at_bottom(mock_bot, 12345, menu)
    
    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args
    assert call_args[0][0] == 12345  # chat_id
    assert call_args[1]["reply_markup"] == menu


def test_handle_callback_query_unauthorized_user(
    mock_bot: Mock, mock_callback_query: Mock, user_security: Security, test_settings: SettingsConfig
) -> None:
    """Test handling callback from unauthorized user."""
    # Make user unauthorized
    unauthorized_user = Mock()
    unauthorized_user.id = 99999
    mock_callback_query.from_user = unauthorized_user
    
    handle_callback_query(mock_callback_query, mock_bot, user_security, test_settings)
    
    # Should answer with private bot text
    mock_bot.answer_callback_query.assert_called_once()


def test_handle_callback_query_invalid_data(
    mock_bot: Mock, mock_callback_query: Mock, user_security: Security, test_settings: SettingsConfig
) -> None:
    """Test handling callback with invalid data."""
    mock_callback_query.data = "invalid_data"
    
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        mock_parse.side_effect = ValueError("Invalid callback data")
        
        # Should handle error gracefully
        handle_callback_query(mock_callback_query, mock_bot, user_security, test_settings)
        
        # Should answer callback query
        mock_bot.answer_callback_query.assert_called()


@patch("game_db.callback_handlers._handle_main_menu")
def test_handle_callback_query_main_menu(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling MAIN_MENU callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        from game_db.menu_callbacks import CallbackAction
        mock_parse.return_value = (CallbackAction.MAIN_MENU, [])
        
        handle_callback_query(mock_callback_query, mock_bot, user_security, test_settings)
        
        mock_handle.assert_called_once()


@patch("game_db.callback_handlers._handle_my_games")
def test_handle_callback_query_my_games(
    mock_handle: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test handling MY_GAMES callback."""
    with patch("game_db.callback_handlers.parse_callback_data") as mock_parse:
        from game_db.menu_callbacks import CallbackAction
        mock_parse.return_value = (CallbackAction.MY_GAMES, [])
        
        handle_callback_query(mock_callback_query, mock_bot, user_security, test_settings)
        
        mock_handle.assert_called_once()
