"""Additional tests for file management and sync menu callbacks."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from game_db.callback_handlers import (
    _handle_add_steam_games,
    _handle_check_steam,
    _handle_download_template,
    _handle_file_management,
    _handle_list_files,
    _handle_sync_menu,
    _handle_sync_steam_execute,
    _handle_sync_steam_menu,
)
from game_db.config import SettingsConfig, UsersConfig
from game_db.security import Security


@pytest.fixture
def admin_security() -> Security:
    """Create admin security instance."""
    users_config = UsersConfig(users=["12345"], admins=["12345"])
    return Security(users_config)


@pytest.fixture
def user_security() -> Security:
    """Create user security instance."""
    users_config = UsersConfig(users=["12345"], admins=[])
    return Security(users_config)


@pytest.fixture
def test_settings() -> SettingsConfig:
    """Create test settings."""
    from game_db.config import DBFilesConfig, Paths

    paths = Paths(
        backup_dir=Path("/tmp/backup"),
        update_db_dir=Path("/tmp/update_db"),
        files_dir=Path("/tmp/files"),
        sql_root=Path("/tmp/sql"),
        sqlite_db_file=Path("/tmp/test.db"),
        games_excel_file=Path("/tmp/test.xlsx"),
    )
    db_files = DBFilesConfig(
        sql_games=Path("/tmp/sql/sql_games.sql"),
        sql_games_on_platforms=Path("/tmp/sql/sql_games_on_platforms.sql"),
        sql_dictionaries=Path("/tmp/sql/sql_dictionaries.sql"),
        sql_drop_tables=Path("/tmp/sql/sql_drop_tables.sql"),
        sql_create_tables=Path("/tmp/sql/sql_create_tables.sql"),
        sqlite_db_file=Path("/tmp/test.db"),
    )
    return SettingsConfig(
        paths=paths, db_files=db_files, owner_name="TestOwner"
    )


@pytest.fixture
def mock_bot() -> Mock:
    """Create mock Telegram bot."""
    bot = Mock()
    bot.send_message = Mock()
    bot.edit_message_text = Mock()
    bot.answer_callback_query = Mock()
    bot.send_document = Mock()
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


def test_handle_file_management(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
) -> None:
    """Test file management menu callback."""
    _handle_file_management(
        mock_callback_query, mock_bot, admin_security
    )

    mock_bot.edit_message_text.assert_called_once()
    mock_bot.answer_callback_query.assert_called_once()


def test_handle_file_management_unauthorized(
    mock_bot: Mock,
    mock_callback_query: Mock,
    user_security: Security,
) -> None:
    """Test file management menu callback for non-admin user."""
    _handle_file_management(
        mock_callback_query, mock_bot, user_security
    )

    mock_bot.answer_callback_query.assert_called_once()


def test_handle_sync_menu(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
) -> None:
    """Test sync menu callback."""
    _handle_sync_menu(
        mock_callback_query, mock_bot, admin_security
    )

    mock_bot.edit_message_text.assert_called_once()
    mock_bot.answer_callback_query.assert_called_once()


def test_handle_list_files(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test list files callback."""
    # Create test files directory
    test_settings.paths.files_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_settings.paths.files_dir / "test.txt"
    test_file.write_text("test")

    _handle_list_files(
        mock_callback_query, mock_bot, admin_security, test_settings
    )

    mock_bot.edit_message_text.assert_called_once()
    mock_bot.answer_callback_query.assert_called_once()

    # Cleanup
    test_file.unlink()


def test_handle_list_files_empty(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test list files callback with empty directory."""
    # Ensure directory exists but is empty
    test_settings.paths.files_dir.mkdir(parents=True, exist_ok=True)

    _handle_list_files(
        mock_callback_query, mock_bot, admin_security, test_settings
    )

    mock_bot.edit_message_text.assert_called_once()
    mock_bot.answer_callback_query.assert_called_once()


def test_handle_download_template(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test download template callback."""
    # Create template file
    test_settings.paths.games_excel_file.parent.mkdir(parents=True, exist_ok=True)
    test_settings.paths.games_excel_file.write_text("test")

    _handle_download_template(
        mock_callback_query, mock_bot, admin_security, test_settings
    )

    mock_bot.send_document.assert_called_once()
    mock_bot.answer_callback_query.assert_called_once()

    # Cleanup
    test_settings.paths.games_excel_file.unlink()


def test_handle_download_template_not_found(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test download template callback when file not found."""
    # Ensure file doesn't exist
    if test_settings.paths.games_excel_file.exists():
        test_settings.paths.games_excel_file.unlink()

    _handle_download_template(
        mock_callback_query, mock_bot, admin_security, test_settings
    )

    mock_bot.answer_callback_query.assert_called_once()


def test_handle_sync_steam_menu(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
) -> None:
    """Test sync steam menu callback."""
    _handle_sync_steam_menu(
        mock_callback_query, mock_bot, admin_security
    )

    mock_bot.edit_message_text.assert_called_once()
    mock_bot.answer_callback_query.assert_called_once()


def test_handle_sync_steam_execute(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test sync steam execute callback."""
    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.synchronize_steam_games.return_value = (True, [])
        mock_change_db.return_value = mock_db

        _handle_sync_steam_execute(
            mock_callback_query, mock_bot, admin_security, test_settings
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_check_steam(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test check steam callback."""
    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.check_steam_games.return_value = (True, [])
        mock_change_db.return_value = mock_db

        _handle_check_steam(
            mock_callback_query, mock_bot, admin_security, test_settings
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_check_steam_with_missing(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test check steam callback with missing games."""
    from game_db.similarity_search import SimilarityMatch

    match = SimilarityMatch(
        original="Test Game",
        closest_match="Test Game Match",
        distance=1,
        score=0.95,
    )

    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.check_steam_games.return_value = (True, [match])
        mock_change_db.return_value = mock_db

        _handle_check_steam(
            mock_callback_query, mock_bot, admin_security, test_settings
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_add_steam_games(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test add steam games callback."""
    from game_db.similarity_search import SimilarityMatch

    match = SimilarityMatch(
        original="Test Game",
        closest_match="Test Game Match",
        distance=1,
        score=0.95,
    )

    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.check_steam_games.return_value = (True, [match])
        mock_db.add_steam_games_to_excel.return_value = True
        mock_change_db.return_value = mock_db

        _handle_add_steam_games(
            mock_callback_query, mock_bot, admin_security, test_settings
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_add_steam_games_no_games(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test add steam games callback when no games to add."""
    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.check_steam_games.return_value = (True, [])
        mock_change_db.return_value = mock_db

        _handle_add_steam_games(
            mock_callback_query, mock_bot, admin_security, test_settings
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_sync_metacritic_execute_full(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test metacritic sync execute callback in full mode."""
    from game_db.callback_handlers import _handle_sync_metacritic_execute

    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.synchronize_metacritic_games.return_value = True
        mock_change_db.return_value = mock_db

        _handle_sync_metacritic_execute(
            mock_callback_query,
            mock_bot,
            admin_security,
            test_settings,
            partial_mode=False,
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_sync_metacritic_execute_partial(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test metacritic sync execute callback in partial mode."""
    from game_db.callback_handlers import _handle_sync_metacritic_execute

    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.synchronize_metacritic_games.return_value = None
        mock_change_db.return_value = mock_db

        _handle_sync_metacritic_execute(
            mock_callback_query,
            mock_bot,
            admin_security,
            test_settings,
            partial_mode=True,
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_sync_hltb_execute_full(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test HLTB sync execute callback in full mode."""
    from game_db.callback_handlers import _handle_sync_hltb_execute

    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.synchronize_hltb_games.return_value = True
        mock_change_db.return_value = mock_db

        _handle_sync_hltb_execute(
            mock_callback_query,
            mock_bot,
            admin_security,
            test_settings,
            partial_mode=False,
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()


def test_handle_sync_hltb_execute_partial(
    mock_bot: Mock,
    mock_callback_query: Mock,
    admin_security: Security,
    test_settings: SettingsConfig,
) -> None:
    """Test HLTB sync execute callback in partial mode."""
    from game_db.callback_handlers import _handle_sync_hltb_execute

    with patch("game_db.callback_handlers.ChangeDB") as mock_change_db:
        mock_db = Mock()
        mock_db.synchronize_hltb_games.return_value = None
        mock_change_db.return_value = mock_db

        _handle_sync_hltb_execute(
            mock_callback_query,
            mock_bot,
            admin_security,
            test_settings,
            partial_mode=True,
        )

        mock_bot.answer_callback_query.assert_called()
        mock_bot.send_message.assert_called()
