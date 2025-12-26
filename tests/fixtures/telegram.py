"""Telegram bot fixtures for testing."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from game_db.config import (
    DBFilesConfig,
    Paths,
    SettingsConfig,
    TokensConfig,
    UsersConfig,
)
from game_db.security import Security


@pytest.fixture
def mock_bot() -> Mock:
    """Create a mock Telegram bot.

    Returns:
        Mock Telegram bot with common methods
    """
    bot = Mock()
    bot.send_message = Mock()
    bot.send_document = Mock()
    bot.delete_message = Mock()
    bot.get_file = Mock()
    bot.download_file = Mock()
    bot.polling = Mock()
    bot.stop_polling = Mock()
    return bot


@pytest.fixture
def mock_message() -> Mock:
    """Create a mock Telegram message.

    Returns:
        Mock Telegram message with common attributes
    """
    message = Mock()
    message.chat.id = 12345
    message.from_user.id = 12345
    message.text = "test"
    message.message_id = 1
    message.document = None
    return message


@pytest.fixture
def mock_message_with_document() -> Mock:
    """Create a mock Telegram message with document.

    Returns:
        Mock Telegram message with document attached
    """
    message = Mock()
    message.chat.id = 12345
    message.from_user.id = 12345
    message.text = "test"
    message.message_id = 1
    message.document = Mock()
    message.document.file_name = "test.xlsx"
    message.document.file_id = "file123"
    return message


@pytest.fixture
def admin_security() -> Security:
    """Create Security instance for admin user.

    Returns:
        Security instance with admin user
    """
    users_cfg = UsersConfig(users=["12345"], admins=["12345"])
    return Security(users_cfg)


@pytest.fixture
def user_security() -> Security:
    """Create Security instance for regular user.

    Returns:
        Security instance with regular user (non-admin)
    """
    users_cfg = UsersConfig(users=["12345"], admins=[])
    return Security(users_cfg)


@pytest.fixture
def test_config() -> SettingsConfig:
    """Create test SettingsConfig.

    Returns:
        SettingsConfig with test paths
    """
    paths = Paths(
        backup_dir=Path("/tmp/backup"),
        update_db_dir=Path("/tmp/update_db"),
        files_dir=Path("/tmp/files"),
        sql_root=Path("/tmp/sql"),
        sqlite_db_file=Path("/tmp/games.db"),
        games_excel_file=Path("/tmp/games.xlsx"),
    )
    db_files = DBFilesConfig(
        sql_games=Path("/tmp/sql/dml_games.sql"),
        sql_games_on_platforms=Path("/tmp/sql/dml_games_on_platforms.sql"),
        sql_dictionaries=Path("/tmp/sql/dml_dictionaries.sql"),
        sql_drop_tables=Path("/tmp/sql/drop_tables.sql"),
        sql_create_tables=Path("/tmp/sql/create_tables.sql"),
        sqlite_db_file=Path("/tmp/games.db"),
    )
    return SettingsConfig(paths=paths, db_files=db_files, owner_name="Alexander")


@pytest.fixture
def test_tokens() -> TokensConfig:
    """Create test TokensConfig.

    Returns:
        TokensConfig with test tokens
    """
    return TokensConfig(
        telegram_token="test_token",
        steam_key="test_steam_key",
        steam_id="test_steam_id",
    )


@pytest.fixture
def test_users() -> UsersConfig:
    """Create test UsersConfig.

    Returns:
        UsersConfig with test users
    """
    return UsersConfig(users=["12345", "67890"], admins=["12345"])


@pytest.fixture
def mock_steam_api() -> Mock:
    """Create a mock SteamAPI client.

    Returns:
        Mock SteamAPI with common methods and default test games
    """
    from game_db.types import SteamGame

    mock_api = Mock()
    # Default test games
    mock_games = [
        SteamGame(
            appid=12345,
            name="Test Game",
            playtime_forever=120,  # 2 hours in minutes
            img_icon_url="",
            img_logo_url="",
            has_community_visible_stats=None,
            playtime_windows_forever=None,
            playtime_mac_forever=None,
            playtime_linux_forever=None,
            rtime_last_played=1704067200,  # Jan 1, 2024
        )
    ]
    mock_api.get_all_games.return_value = mock_games
    return mock_api


@pytest.fixture
def bot_app(
    test_config: SettingsConfig,
    test_tokens: TokensConfig,
    test_users: UsersConfig,
) -> "BotApplication":
    """Create a BotApplication instance for testing.

    Returns:
        BotApplication instance with mocked Telegram bot
    """
    from unittest.mock import patch

    from game_db.bot import BotApplication

    with patch("game_db.bot.telebot.TeleBot"):
        app = BotApplication(test_config, test_tokens, test_users)
        return app
