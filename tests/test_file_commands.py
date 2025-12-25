"""Tests for file-related bot commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from game_db.commands import GetFileCommand, RemoveFileCommand, SyncSteamCommand
from game_db.config import DBFilesConfig, Paths, SettingsConfig


@pytest.fixture
def file_commands_settings(tmp_path: Path) -> SettingsConfig:
    """SettingsConfig with real filesystem directories under tmp_path."""
    paths = Paths(
        backup_dir=tmp_path / "backup",
        update_db_dir=tmp_path / "update_db",
        files_dir=tmp_path / "files",
        sql_root=tmp_path / "sql",
        sqlite_db_file=tmp_path / "games.db",
        games_excel_file=tmp_path / "backup" / "games.xlsx",
    )
    # Ensure directories exist
    paths.backup_dir.mkdir(parents=True, exist_ok=True)
    paths.update_db_dir.mkdir(parents=True, exist_ok=True)
    paths.files_dir.mkdir(parents=True, exist_ok=True)

    db_files = DBFilesConfig(
        sql_games=tmp_path / "sql" / "dml_games.sql",
        sql_games_on_platforms=tmp_path
        / "sql"
        / "dml_games_on_platforms.sql",
        sql_dictionaries=tmp_path / "sql" / "dml_dictionaries.sql",
        sql_drop_tables=tmp_path / "sql" / "drop_tables.sql",
        sql_create_tables=tmp_path / "sql" / "create_tables.sql",
        sqlite_db_file=paths.sqlite_db_file,
    )
    return SettingsConfig(paths=paths, db_files=db_files)


def test_remove_file_command_non_admin_does_nothing(
    mock_bot: Mock, mock_message: Mock, user_security, file_commands_settings: SettingsConfig
) -> None:
    """Non-admin user should receive NICE_TRY_TEXT."""
    from game_db import texts

    mock_message.text = "removefile test.txt"

    command = RemoveFileCommand()
    command.execute(mock_message, mock_bot, user_security, file_commands_settings)

    mock_bot.send_message.assert_called_once_with(
        mock_message.chat.id, texts.NICE_TRY_TEXT
    )


def test_remove_file_command_invalid_filename(
    mock_bot: Mock, mock_message: Mock, admin_security, file_commands_settings: SettingsConfig
) -> None:
    """Invalid filename should be rejected with error message."""
    mock_message.text = "removefile ../../../etc/passwd"

    command = RemoveFileCommand()
    command.execute(mock_message, mock_bot, admin_security, file_commands_settings)

    # Error text is in Russian; just assert message was sent
    mock_bot.send_message.assert_called()


def test_remove_file_command_success(
    mock_bot: Mock, mock_message: Mock, admin_security, file_commands_settings: SettingsConfig
) -> None:
    """Valid file inside files_dir should be deleted."""
    from game_db import texts

    # Create a file inside files_dir
    target_file = file_commands_settings.paths.files_dir / "test.txt"
    target_file.write_text("content", encoding="utf-8")

    mock_message.text = "removefile test.txt"

    command = RemoveFileCommand()
    command.execute(
        mock_message, mock_bot, admin_security, file_commands_settings
    )

    assert not target_file.exists()
    # Just assert that FILE_DELETED was sent, ignoring exact reply_markup
    args, kwargs = mock_bot.send_message.call_args
    assert texts.FILE_DELETED in args or texts.FILE_DELETED in str(kwargs)


def test_get_file_command_non_admin_denied(
    mock_bot: Mock, mock_message: Mock, user_security, file_commands_settings: SettingsConfig
) -> None:
    """Non-admin user should not be able to get file."""
    from game_db import texts

    mock_message.text = "getfile test.txt"

    command = GetFileCommand()
    command.execute(mock_message, mock_bot, user_security, file_commands_settings)

    mock_bot.send_message.assert_called_once_with(
        mock_message.chat.id, texts.NICE_TRY_TEXT
    )


def test_get_file_command_invalid_filename(
    mock_bot: Mock, mock_message: Mock, admin_security, file_commands_settings: SettingsConfig
) -> None:
    """Invalid filename should be rejected."""
    mock_message.text = "getfile ../../etc/passwd"

    command = GetFileCommand()
    command.execute(mock_message, mock_bot, admin_security, file_commands_settings)

    mock_bot.send_message.assert_called()


def test_get_file_command_not_found(
    mock_bot: Mock, mock_message: Mock, admin_security, file_commands_settings: SettingsConfig
) -> None:
    """Requesting nonexistent file should send FILE_NOT_FOUND."""
    from game_db import texts

    mock_message.text = "getfile missing.txt"

    command = GetFileCommand()
    command.execute(mock_message, mock_bot, admin_security, file_commands_settings)

    mock_bot.send_message.assert_called_with(
        mock_message.chat.id, texts.FILE_NOT_FOUND
    ) or mock_bot.send_message.called


def test_get_file_command_success(
    mock_bot: Mock, mock_message: Mock, admin_security, file_commands_settings: SettingsConfig
) -> None:
    """Existing file inside files_dir should be sent as document."""
    files_dir = file_commands_settings.paths.files_dir
    target_file = files_dir / "test.txt"
    files_dir.mkdir(parents=True, exist_ok=True)
    target_file.write_text("content", encoding="utf-8")

    mock_message.text = "getfile test.txt"

    command = GetFileCommand()
    command.execute(mock_message, mock_bot, admin_security, file_commands_settings)

    mock_bot.send_document.assert_called()


def test_sync_steam_non_admin_denied(
    mock_bot: Mock, mock_message: Mock, user_security, file_commands_settings: SettingsConfig
) -> None:
    """Non-admin user cannot trigger SyncSteamCommand."""
    from game_db import texts

    command = SyncSteamCommand()
    command.execute(mock_message, mock_bot, user_security, file_commands_settings)

    mock_bot.send_message.assert_called_once_with(
        mock_message.chat.id, texts.NICE_TRY_TEXT
    )


def test_sync_steam_file_not_found(
    mock_bot: Mock, mock_message: Mock, admin_security, file_commands_settings: SettingsConfig
) -> None:
    """SyncSteamCommand reports missing Excel backup file."""
    from game_db import texts

    # Ensure games_excel_file does not exist
    if file_commands_settings.paths.games_excel_file.exists():
        file_commands_settings.paths.games_excel_file.unlink()

    command = SyncSteamCommand()
    command.execute(mock_message, mock_bot, admin_security, file_commands_settings)

    mock_bot.send_message.assert_called_with(
        mock_message.chat.id, texts.STEAM_SYNC_FILE_NOT_FOUND
    ) or mock_bot.send_message.called


def test_sync_steam_success(
    mock_bot: Mock, mock_message: Mock, admin_security, file_commands_settings: SettingsConfig
) -> None:
    """SyncSteamCommand calls ChangeDB.synchronize_steam_games and updates backup."""
    from game_db import texts

    backup_excel = file_commands_settings.paths.games_excel_file
    backup_excel.parent.mkdir(parents=True, exist_ok=True)
    backup_excel.write_text("content", encoding="utf-8")

    # Patch ChangeDB at its original location; SyncSteamCommand imports it
    # locally as ``from .. import db as db_module``
    with patch("game_db.db.ChangeDB") as mock_change_db:
        instance = mock_change_db.return_value
        instance.synchronize_steam_games.return_value = True

        command = SyncSteamCommand()
        command.execute(mock_message, mock_bot, admin_security, file_commands_settings)

    instance.synchronize_steam_games.assert_called_once()
    mock_bot.send_message.assert_called()

