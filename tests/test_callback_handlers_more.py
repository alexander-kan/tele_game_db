"""More unit tests for callback_handlers module to increase coverage."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db.callback_handlers import (
    _handle_count_completed,
    _handle_count_time,
    _handle_games_list,
    _handle_stats_completed,
    _handle_stats_time,
)
from game_db.config import SettingsConfig, UsersConfig
from game_db.security import Security
from game_db.menu_callbacks import CallbackAction
from game_db.exceptions import DatabaseError


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
    call.data = "action:test"
    call.from_user = Mock()
    call.from_user.id = 12345
    call.message = Mock()
    call.message.chat.id = 12345
    call.message.message_id = 1
    return call


@patch("game_db.callback_handlers.game_service")
@patch("game_db.callback_handlers.MessageFormatter")
@patch("game_db.callback_handlers.InlineMenu")
@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_games_list_success(
    mock_safe_answer: Mock,
    mock_inline_menu: Mock,
    mock_formatter: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test _handle_games_list with successful retrieval."""
    from game_db.types import GameListItem
    
    mock_callback_query.data = "action:games_list:Steam:1:10"
    args = ["Steam", "1", "10"]
    
    mock_games = [
        GameListItem(
            game_name="Game 1",
            press_score="8.5",
            average_time_beat=None,
            trailer_url=None,
        )
    ]
    mock_game_service.get_next_game_list.return_value = mock_games
    # MessageFormatter.format_next_game_message is a static method
    with patch("game_db.callback_handlers.MessageFormatter.format_next_game_message") as mock_format:
        mock_format.return_value = "Game list text"
    mock_menu = Mock()
    mock_inline_menu.platform_menu_with_pagination.return_value = mock_menu
    
    _handle_games_list(mock_callback_query, mock_bot, user_security, args)
    
    mock_game_service.get_next_game_list.assert_called_once_with(0, 10, "Steam")
    mock_bot.edit_message_text.assert_called_once()
    mock_safe_answer.assert_called_once()


@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_games_list_invalid_args(
    mock_safe_answer: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test _handle_games_list with invalid args."""
    args = ["Steam"]  # Missing offset and limit
    
    _handle_games_list(mock_callback_query, mock_bot, user_security, args)
    
    mock_safe_answer.assert_called_once()
    # Should not call game_service
    assert not hasattr(mock_bot, 'edit_message_text') or not mock_bot.edit_message_text.called


@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_games_list_invalid_pagination(
    mock_safe_answer: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test _handle_games_list with invalid pagination parameters."""
    args = ["Steam", "invalid", "10"]  # Invalid offset
    
    _handle_games_list(mock_callback_query, mock_bot, user_security, args)
    
    mock_safe_answer.assert_called_once()


@patch("game_db.callback_handlers.game_service")
@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_games_list_database_error(
    mock_safe_answer: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test _handle_games_list with database error."""
    args = ["Steam", "1", "10"]
    mock_game_service.get_next_game_list.side_effect = DatabaseError("DB error")
    
    _handle_games_list(mock_callback_query, mock_bot, user_security, args)
    
    mock_safe_answer.assert_called_once()
    call_args = mock_safe_answer.call_args
    assert call_args[1]["show_alert"] is True


@patch("game_db.callback_handlers.game_service")
@patch("game_db.callback_handlers.InlineMenu")
@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_count_completed_success(
    mock_safe_answer: Mock,
    mock_inline_menu: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test _handle_count_completed with successful count."""
    args = ["Steam"]
    mock_game_service.count_complete_games.return_value = 42
    mock_menu = Mock()
    mock_inline_menu.platform_menu.return_value = mock_menu
    
    _handle_count_completed(mock_callback_query, mock_bot, user_security, args)
    
    mock_game_service.count_complete_games.assert_called_once_with("Steam")
    mock_bot.edit_message_text.assert_called_once()
    mock_safe_answer.assert_called_once()


@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_count_completed_no_args(
    mock_safe_answer: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test _handle_count_completed with no args."""
    args = []
    
    _handle_count_completed(mock_callback_query, mock_bot, user_security, args)
    
    mock_safe_answer.assert_called_once()


@patch("game_db.callback_handlers.game_service")
@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_count_completed_database_error(
    mock_safe_answer: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test _handle_count_completed with database error."""
    args = ["Steam"]
    mock_game_service.count_complete_games.side_effect = DatabaseError("DB error")
    
    _handle_count_completed(mock_callback_query, mock_bot, user_security, args)
    
    mock_safe_answer.assert_called_once()
    call_args = mock_safe_answer.call_args
    assert call_args[1]["show_alert"] is True


@patch("game_db.callback_handlers.game_service")
@patch("game_db.callback_handlers.MessageFormatter")
@patch("game_db.callback_handlers.InlineMenu")
@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_count_time_success(
    mock_safe_answer: Mock,
    mock_inline_menu: Mock,
    mock_formatter: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test _handle_count_time with successful time count."""
    args = ["Steam"]
    # count_spend_time returns (expected_time, real_time) tuple
    mock_game_service.count_spend_time.return_value = (100.0, 120.0)
    mock_formatter_instance = Mock()
    mock_formatter_instance.format_time_stats.return_value = "Time stats"
    mock_formatter.return_value = mock_formatter_instance
    mock_menu = Mock()
    mock_inline_menu.platform_menu.return_value = mock_menu
    
    _handle_count_time(mock_callback_query, mock_bot, user_security, args, test_settings)
    
    mock_game_service.count_spend_time.assert_called_once_with("Steam", mode=1)
    mock_bot.edit_message_text.assert_called_once()
    mock_safe_answer.assert_called_once()


@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_count_time_no_args(
    mock_safe_answer: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test _handle_count_time with no args."""
    args = []
    
    _handle_count_time(mock_callback_query, mock_bot, user_security, args, test_settings)
    
    mock_safe_answer.assert_called_once()


@patch("game_db.callback_handlers.game_service")
@patch("game_db.callback_handlers.MessageFormatter")
@patch("game_db.callback_handlers.InlineMenu")
@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_stats_completed_success(
    mock_safe_answer: Mock,
    mock_inline_menu: Mock,
    mock_formatter: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test _handle_stats_completed with successful stats."""
    mock_game_service.count_complete_games.return_value = 42
    mock_formatter_instance = Mock()
    mock_formatter_instance.format_completed_games_stats.return_value = "Stats text"
    mock_formatter.return_value = mock_formatter_instance
    mock_menu = Mock()
    mock_inline_menu.statistics_menu.return_value = mock_menu
    
    _handle_stats_completed(mock_callback_query, mock_bot, user_security, test_settings)
    
    mock_bot.edit_message_text.assert_called_once()
    mock_safe_answer.assert_called_once()


@patch("game_db.callback_handlers.game_service")
@patch("game_db.callback_handlers.MessageFormatter")
@patch("game_db.callback_handlers.InlineMenu")
@patch("game_db.callback_handlers._safe_answer_callback_query")
def test_handle_stats_time_success(
    mock_safe_answer: Mock,
    mock_inline_menu: Mock,
    mock_formatter: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test _handle_stats_time with successful time stats."""
    mock_game_service.get_time_stats.return_value = (
        {"Steam": (100.0, 120.0), "Switch": (50.0, 45.0)},
        594000.0,
    )
    mock_formatter_instance = Mock()
    mock_formatter_instance.format_time_stats.return_value = "Time stats"
    mock_formatter.return_value = mock_formatter_instance
    mock_menu = Mock()
    mock_inline_menu.statistics_menu.return_value = mock_menu
    
    _handle_stats_time(mock_callback_query, mock_bot, user_security, test_settings)
    
    mock_bot.edit_message_text.assert_called_once()
    mock_safe_answer.assert_called_once()
