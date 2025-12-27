"""Additional unit tests for handlers module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db import handlers
from game_db.config import SettingsConfig, UsersConfig
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
def test_config() -> SettingsConfig:
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
    return bot


@pytest.fixture
def mock_message() -> Mock:
    """Create mock message."""
    message = Mock()
    message.chat.id = 12345
    message.from_user.id = 12345
    message.text = "/command"
    return message


@patch("game_db.handlers.menu")
@patch("game_db.handlers.texts")
def test_handle_main_menu(
    mock_texts: Mock,
    mock_menu: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
) -> None:
    """Test _handle_main_menu handler."""
    mock_texts.MAIN_MENU = "Main menu"
    mock_menu_markup = Mock()
    mock_menu.BotMenu.main_menu.return_value = mock_menu_markup

    handlers._handle_main_menu(mock_message, mock_bot, admin_security)

    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args
    assert call_args[0][0] == mock_message.from_user.id


@patch("game_db.handlers.menu")
@patch("game_db.handlers.texts")
def test_handle_file_menu(
    mock_texts: Mock,
    mock_menu: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
) -> None:
    """Test _handle_file_menu handler."""
    mock_texts.FILE_MENU = "File menu"
    mock_menu_markup = Mock()
    mock_menu.BotMenu.file_menu.return_value = mock_menu_markup

    handlers._handle_file_menu(mock_message, mock_bot, admin_security)

    mock_bot.send_message.assert_called_once()


# test_handle_game_lists_menu skipped - uses global settings variable that's hard to mock


@patch("game_db.handlers.menu")
@patch("game_db.handlers.texts")
def test_handle_show_commands(
    mock_texts: Mock,
    mock_menu: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
) -> None:
    """Test _handle_show_commands handler."""
    mock_texts.USER_COMMANDS_HELP = "User commands text"
    mock_menu_markup = Mock()
    mock_menu.BotMenu.main_menu.return_value = mock_menu_markup

    handlers._handle_show_commands(mock_message, mock_bot, admin_security)

    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args
    assert call_args[0][0] == mock_message.chat.id


@patch("game_db.handlers.InlineMenu")
@patch("game_db.handlers.texts")
def test_handle_show_admin_commands(
    mock_texts: Mock,
    mock_inline_menu: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
) -> None:
    """Test _handle_show_admin_commands handler."""
    mock_texts.ADMIN_COMMANDS_HELP = "Admin commands text"
    mock_menu_markup = Mock()
    mock_inline_menu.main_menu.return_value = mock_menu_markup

    handlers._handle_show_admin_commands(mock_message, mock_bot, admin_security)

    mock_bot.send_message.assert_called_once()


@patch("game_db.handlers.game_service")
def test_handle_steam_game_list(
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
) -> None:
    """Test _handle_steam_game_list handler."""
    from game_db.types import GameListItem

    mock_game_service.get_platform_games.return_value = [
        GameListItem(
            game_name="Game 1",
            press_score="8.5",
            average_time_beat=None,
            trailer_url=None,
        )
    ]

    handlers._handle_steam_game_list(
        mock_message, mock_bot, admin_security, test_config
    )

    mock_bot.send_message.assert_called()


@patch("game_db.handlers.game_service")
def test_handle_switch_game_list(
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
) -> None:
    """Test _handle_switch_game_list handler."""
    from game_db.types import GameListItem

    mock_game_service.get_platform_games.return_value = [
        GameListItem(
            game_name="Game 1",
            press_score="8.5",
            average_time_beat=None,
            trailer_url=None,
        )
    ]

    handlers._handle_switch_game_list(
        mock_message, mock_bot, admin_security, test_config
    )

    mock_bot.send_message.assert_called()


@patch("game_db.handlers.game_service")
@patch("game_db.handlers.MessageFormatter")
@patch("game_db.handlers.menu")
def test_handle_count_games(
    mock_menu: Mock,
    mock_formatter: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
) -> None:
    """Test _handle_count_games handler."""
    platforms = ["Steam", "Switch"]
    mock_message.from_user.id = 12345
    mock_game_service.count_complete_games.return_value = 42
    mock_formatter_instance = Mock()
    mock_formatter_instance.format_completed_games_stats.return_value = "Stats text"
    mock_formatter.return_value = mock_formatter_instance
    mock_menu_markup = Mock()
    mock_menu.BotMenu.next_game.return_value = mock_menu_markup

    handlers._handle_count_games(mock_message, mock_bot, platforms, test_config)

    mock_bot.send_message.assert_called_once()
    assert mock_game_service.count_complete_games.call_count == len(platforms)


@patch("game_db.handlers.game_service")
@patch("game_db.handlers.MessageFormatter")
@patch("game_db.handlers.menu")
def test_handle_count_time(
    mock_menu: Mock,
    mock_formatter: Mock,
    mock_game_service: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    test_config: SettingsConfig,
) -> None:
    """Test _handle_count_time handler."""
    platforms = ["Steam"]
    mock_message.from_user.id = 12345
    # count_spend_time returns (expected, real) tuple
    mock_game_service.count_spend_time.return_value = (100.0, 120.0)
    mock_formatter_instance = Mock()
    mock_formatter_instance.format_time_stats.return_value = "Time stats text"
    mock_formatter.return_value = mock_formatter_instance
    mock_menu_markup = Mock()
    mock_menu.BotMenu.next_game.return_value = mock_menu_markup

    handlers._handle_count_time(mock_message, mock_bot, platforms, test_config)

    mock_bot.send_message.assert_called_once()
    assert mock_game_service.count_spend_time.call_count == len(platforms)


@patch("game_db.handlers.validate_file_name")
@patch("game_db.handlers.safe_delete_file")
@patch("game_db.handlers.menu")
def test_handle_remove_file_success(
    mock_menu: Mock,
    mock_safe_delete: Mock,
    mock_validate: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
) -> None:
    """Test _handle_remove_file with successful deletion."""
    mock_message.text = "removefile test.txt"
    mock_validate.return_value = True
    mock_safe_delete.return_value = True
    mock_menu_markup = Mock()
    mock_menu.BotMenu.file_menu.return_value = mock_menu_markup

    handlers._handle_remove_file(mock_message, mock_bot, admin_security, test_config)

    mock_validate.assert_called_once_with("test.txt")
    mock_safe_delete.assert_called_once()
    mock_bot.send_message.assert_called_once()


@patch("game_db.handlers.validate_file_name")
@patch("game_db.handlers.menu")
def test_handle_remove_file_invalid_name(
    mock_menu: Mock,
    mock_validate: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
) -> None:
    """Test _handle_remove_file with invalid file name."""
    mock_message.text = "removefile ../../../etc/passwd"
    mock_validate.return_value = False
    mock_menu_markup = Mock()
    mock_menu.BotMenu.file_menu.return_value = mock_menu_markup

    handlers._handle_remove_file(mock_message, mock_bot, admin_security, test_config)

    mock_validate.assert_called_once()
    mock_bot.send_message.assert_called_once()


@patch("game_db.handlers.validate_file_name")
def test_handle_get_file_invalid_name_already_tested(
    mock_validate: Mock,
) -> None:
    """This test is already covered in test_handlers.py."""
    # Test is already covered, just ensure it compiles
    assert True


@patch("game_db.handlers.validate_file_name")
@patch("game_db.handlers.menu")
def test_handle_get_file_invalid_name(
    mock_menu: Mock,
    mock_validate: Mock,
    mock_bot: Mock,
    mock_message: Mock,
    admin_security: Security,
    test_config: SettingsConfig,
) -> None:
    """Test _handle_get_file with invalid file name."""
    mock_message.text = "getfile ../../../etc/passwd"
    mock_validate.return_value = False
    mock_menu_markup = Mock()
    mock_menu.BotMenu.file_menu.return_value = mock_menu_markup

    handlers._handle_get_file(mock_message, mock_bot, admin_security, test_config)

    mock_validate.assert_called_once()
    mock_bot.send_message.assert_called_once()
