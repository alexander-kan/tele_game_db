"""Tests for error handling in handlers and commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from game_db.exceptions import DatabaseError, DatabaseQueryError

pytestmark = pytest.mark.error_handling


class TestHandlersErrorHandling:
    """Test error handling in handlers."""

    @patch("game_db.commands.game_commands.game_service")
    def test_handle_get_game_database_error(
        self,
        mock_game_service: Mock,
        mock_bot: Mock,
        mock_message: Mock,
        admin_security,
    ) -> None:
        """Test handle_get_game handles database errors."""
        from game_db import handlers

        mock_message.text = "getgame Test Game"
        mock_game_service.query_game.side_effect = DatabaseError(
            "Database connection failed"
        )

        from game_db.config import DBFilesConfig, Paths, SettingsConfig

        paths = Paths(
            backup_dir=Path("/tmp"),
            update_db_dir=Path("/tmp"),
            files_dir=Path("/tmp"),
            sql_root=Path("/tmp"),
            sqlite_db_file=Path("/tmp/db.db"),
            games_excel_file=Path("/tmp/games.xlsx"),
        )
        db_files = DBFilesConfig(
            sql_games=Path("/tmp/sql/dml_games.sql"),
            sql_games_on_platforms=Path(
                "/tmp/sql/dml_games_on_platforms.sql"
            ),
            sql_dictionaries=Path("/tmp/sql/dml_dictionaries.sql"),
            sql_drop_tables=Path("/tmp/sql/drop_tables.sql"),
            sql_create_tables=Path("/tmp/sql/create_tables.sql"),
            sqlite_db_file=paths.sqlite_db_file,
        )
        test_config = SettingsConfig(paths=paths, db_files=db_files, owner_name="Alexander")
        handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

        # Should send error message to user
        mock_bot.send_message.assert_called()
        call_args = mock_bot.send_message.call_args
        # Check that error message was sent
        assert call_args is not None

    @patch("game_db.commands.game_commands.game_service")
    def test_handle_count_games_database_error(
        self,
        mock_game_service: Mock,
        mock_bot: Mock,
        mock_message: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test handle_count_games handles database errors gracefully."""
        from game_db import handlers

        mock_message.text = "How many games Alexander completed"
        mock_game_service.get_platforms.return_value = ["Steam", "Switch"]
        mock_game_service.count_complete_games.side_effect = DatabaseError(
            "Query failed"
        )

        handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

        # Should still send a message (with 0 counts for failed platforms)
        mock_bot.send_message.assert_called_once()

    @patch("game_db.commands.game_commands.game_service")
    def test_handle_count_time_database_error(
        self,
        mock_game_service: Mock,
        mock_bot: Mock,
        mock_message: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test handle_count_time handles database errors gracefully."""
        from game_db import handlers

        mock_message.text = "How much time Alexander spent on games"
        mock_game_service.get_platforms.return_value = ["Steam", "Switch"]
        mock_game_service.count_spend_time.side_effect = DatabaseError(
            "Query failed"
        )

        handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

        # Should still send a message
        mock_bot.send_message.assert_called_once()

    @patch("game_db.commands.game_commands.game_service")
    def test_handle_get_game_empty_result(
        self,
        mock_game_service: Mock,
        mock_bot: Mock,
        mock_message: Mock,
        admin_security,
    ) -> None:
        """Test handle_get_game handles empty search results."""
        from game_db import handlers

        mock_message.text = "getgame NonExistentGame"
        mock_game_service.query_game.return_value = []

        from game_db.config import DBFilesConfig, Paths, SettingsConfig

        paths = Paths(
            backup_dir=Path("/tmp"),
            update_db_dir=Path("/tmp"),
            files_dir=Path("/tmp"),
            sql_root=Path("/tmp"),
            sqlite_db_file=Path("/tmp/db.db"),
            games_excel_file=Path("/tmp/games.xlsx"),
        )
        db_files = DBFilesConfig(
            sql_games=Path("/tmp/sql/dml_games.sql"),
            sql_games_on_platforms=Path(
                "/tmp/sql/dml_games_on_platforms.sql"
            ),
            sql_dictionaries=Path("/tmp/sql/dml_dictionaries.sql"),
            sql_drop_tables=Path("/tmp/sql/drop_tables.sql"),
            sql_create_tables=Path("/tmp/sql/create_tables.sql"),
            sqlite_db_file=paths.sqlite_db_file,
        )
        test_config = SettingsConfig(paths=paths, db_files=db_files, owner_name="Alexander")
        handlers.handle_text(mock_message, mock_bot, admin_security, test_config)

        # Should send "game not found" message
        mock_bot.send_message.assert_called_once()

    def test_handle_file_upload_download_error(
        self,
        mock_bot: Mock,
        mock_message_with_document: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test handle_file_upload handles download errors."""
        from game_db import handlers

        mock_bot.get_file.side_effect = Exception("Download failed")

        handlers.handle_file_upload(
            mock_message_with_document, mock_bot, admin_security, test_config
        )

        # Should handle error gracefully
        mock_bot.send_message.assert_called()

    def test_handle_file_upload_invalid_file_type(
        self,
        mock_bot: Mock,
        mock_message_with_document: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test handle_file_upload rejects invalid file types."""
        from game_db import handlers

        mock_message_with_document.document.file_name = "malicious.exe"

        handlers.handle_file_upload(
            mock_message_with_document, mock_bot, admin_security, test_config
        )

        # Should send error message
        mock_bot.send_message.assert_called_once()

    def test_handle_file_upload_path_traversal(
        self,
        mock_bot: Mock,
        mock_message_with_document: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test handle_file_upload prevents path traversal."""
        from game_db import handlers

        mock_message_with_document.document.file_name = "../../etc/passwd"

        handlers.handle_file_upload(
            mock_message_with_document, mock_bot, admin_security, test_config
        )

        # Should reject the file
        mock_bot.send_message.assert_called_once()


class TestCommandsErrorHandling:
    """Test error handling in command classes."""

    @patch("game_db.commands.game_commands.game_service")
    def test_get_game_command_database_error(
        self,
        mock_game_service: Mock,
        mock_bot: Mock,
        mock_message: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test GetGameCommand handles database errors."""
        from game_db.commands import GetGameCommand

        mock_message.text = "getgame Test"
        mock_game_service.query_game.side_effect = DatabaseQueryError(
            "Query failed", sql="SELECT ..."
        )

        command = GetGameCommand()
        command.execute(mock_message, mock_bot, admin_security, test_config)

        # Should send error message
        mock_bot.send_message.assert_called()

    @patch("game_db.commands.game_commands.game_service")
    def test_count_games_command_partial_failure(
        self,
        mock_game_service: Mock,
        mock_bot: Mock,
        mock_message: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test CountGamesCommand handles partial platform failures."""
        from game_db.commands import CountGamesCommand

        mock_game_service.get_platforms.return_value = [
            "Steam",
            "Switch",
            "PS4",
        ]
        # One platform fails
        mock_game_service.count_complete_games.side_effect = [
            DatabaseError("Failed"),
            5,  # Success
            3,  # Success
        ]

        command = CountGamesCommand()
        command.execute(mock_message, mock_bot, admin_security, test_config)

        # Should still send message with partial results
        mock_bot.send_message.assert_called_once()

    def test_remove_file_command_invalid_filename(
        self,
        mock_bot: Mock,
        mock_message: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test RemoveFileCommand handles invalid filenames."""
        from game_db.commands import RemoveFileCommand

        mock_message.text = "removefile ../../../etc/passwd"

        command = RemoveFileCommand()
        command.execute(mock_message, mock_bot, admin_security, test_config)

        # Should send error message
        mock_bot.send_message.assert_called()

    def test_get_file_command_nonexistent_file(
        self,
        mock_bot: Mock,
        mock_message: Mock,
        test_config,
        admin_security,
    ) -> None:
        """Test GetFileCommand handles nonexistent files."""
        from game_db.commands import GetFileCommand

        mock_message.text = "getfile nonexistent.xlsx"

        command = GetFileCommand()
        command.execute(mock_message, mock_bot, admin_security, test_config)

        # Should send "file not found" message
        mock_bot.send_message.assert_called()
