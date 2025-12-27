"""Unit tests for BotApplication class with Dependency Injection."""

from __future__ import annotations

import pathlib
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from game_db.bot import BotApplication
from game_db.config import SettingsConfig, TokensConfig, UsersConfig

# Ensure project root is on sys.path when running tests directly
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Fixtures are now imported from conftest.py
# test_config (as test_config), test_tokens, test_users


def test_bot_application_initialization(
    test_config: SettingsConfig,
    test_tokens: TokensConfig,
    test_users: UsersConfig,
) -> None:
    """Test that BotApplication initializes correctly with dependencies."""
    with patch("game_db.bot.telebot.TeleBot") as mock_telebot:
        app = BotApplication(test_config, test_tokens, test_users)

        assert app.settings == test_config
        assert app.tokens == test_tokens
        assert app.users == test_users
        assert app.security.users_cfg == test_users
        mock_telebot.assert_called_once_with("test_token", threaded=False)


def test_bot_application_security_initialization(
    test_config: SettingsConfig,
    test_tokens: TokensConfig,
    test_users: UsersConfig,
) -> None:
    """Test that Security is initialized with UsersConfig."""
    with patch("game_db.bot.telebot.TeleBot"):
        app = BotApplication(test_config, test_tokens, test_users)

        assert app.security.user_check("12345") is True
        assert app.security.user_check("99999") is False
        assert app.security.admin_check("12345") is True
        assert app.security.admin_check("67890") is False


def test_sendall(bot_app: BotApplication) -> None:
    """Test sendall method sends messages to all users."""
    bot_app.bot.send_message = Mock()

    bot_app.sendall("Test message")

    assert bot_app.bot.send_message.call_count == 2
    bot_app.bot.send_message.assert_any_call("12345", "Test message")
    bot_app.bot.send_message.assert_any_call("67890", "Test message")


def test_sendall_handles_os_error(bot_app: BotApplication) -> None:
    """Test sendall handles OSError gracefully."""
    bot_app.bot.send_message = Mock(side_effect=OSError("Network error"))

    # Should not raise exception
    bot_app.sendall("Test message")

    assert bot_app.bot.send_message.call_count == 2


def test_sendall_empty_users(bot_app: BotApplication) -> None:
    """Test sendall with empty users list."""
    bot_app.users = UsersConfig(users=[], admins=[])
    bot_app.bot.send_message = Mock()

    bot_app.sendall("Test message")

    bot_app.bot.send_message.assert_not_called()


def test_setup_handlers(bot_app: BotApplication) -> None:
    """Test that setup_handlers registers message handlers."""
    bot_app.bot.message_handler = Mock(return_value=lambda f: f)

    bot_app.setup_handlers()

    # Verify message_handler was called for each handler type
    assert bot_app.bot.message_handler.call_count == 3


def test_prepare_directories_creates_directories(
    bot_app: BotApplication,
) -> None:
    """Test that prepare_directories creates required directories."""
    with patch("pathlib.Path.mkdir") as mock_mkdir, patch(
        "pathlib.Path.exists", return_value=True
    ), patch("pathlib.Path.iterdir", return_value=[]):

        bot_app.prepare_directories()

        # Should create update_db_dir and files_dir
        assert mock_mkdir.call_count >= 2


def test_prepare_directories_cleans_update_db_dir(
    bot_app: BotApplication,
) -> None:
    """Test that prepare_directories cleans update_db_dir."""
    mock_file = Mock()
    mock_file.is_file.return_value = True
    mock_file.unlink = Mock()

    with patch("pathlib.Path.mkdir"), patch(
        "pathlib.Path.exists", return_value=True
    ), patch("pathlib.Path.is_dir", return_value=True), patch(
        "pathlib.Path.iterdir", return_value=[mock_file]
    ), patch(
        "game_db.utils.safe_delete_file"
    ) as mock_safe_delete, patch(
        "game_db.utils.is_path_safe", return_value=True
    ):

        bot_app.prepare_directories()

        # Verify that safe_delete_file was called (through clean_directory_safely)
        assert mock_safe_delete.called


def test_prepare_directories_validates_excel_file(
    bot_app: BotApplication,
) -> None:
    """Test that prepare_directories validates Excel file exists."""
    with patch("pathlib.Path.mkdir"), patch(
        "pathlib.Path.exists", return_value=False
    ), patch("pathlib.Path.iterdir", return_value=[]):

        with pytest.raises(ValueError, match="You don't have file for DB creation"):
            bot_app.prepare_directories()


def test_run_calls_polling(bot_app: BotApplication) -> None:
    """Test that run starts bot polling."""
    bot_app.bot.polling = Mock()

    with patch.object(bot_app, "prepare_directories"):
        bot_app.run()

        bot_app.bot.polling.assert_called_once()


def test_run_handles_os_error(bot_app: BotApplication) -> None:
    """Test that run handles OSError and restarts polling."""
    bot_app.bot.polling = Mock(side_effect=[OSError("Network error"), None])
    bot_app.bot.stop_polling = Mock()

    with patch.object(bot_app, "prepare_directories"), patch("time.sleep"):

        bot_app.run()

        assert bot_app.bot.polling.call_count == 2
        bot_app.bot.stop_polling.assert_called_once()


def test_main_creates_and_runs_app() -> None:
    """Test that main function creates and runs BotApplication."""
    with patch("game_db.bot.configure_logging"), patch(
        "game_db.bot.load_settings_config"
    ) as mock_load_settings, patch(
        "game_db.bot.load_tokens_config"
    ) as mock_load_tokens, patch(
        "game_db.bot.load_users_config"
    ) as mock_load_users, patch(
        "game_db.bot.BotApplication"
    ) as mock_app_class:

        test_config = Mock()
        test_tokens = Mock()
        test_users = Mock()
        mock_load_settings.return_value = test_config
        mock_load_tokens.return_value = test_tokens
        mock_load_users.return_value = test_users

        mock_app = Mock()
        mock_app_class.return_value = mock_app

        from game_db.bot import main

        main()

        mock_app_class.assert_called_once_with(test_config, test_tokens, test_users)
        mock_app.setup_handlers.assert_called_once()
        mock_app.run.assert_called_once()
