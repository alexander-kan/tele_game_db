"""Tests for config module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from game_db.config import (
    DEFAULT_PLATFORMS,
    DBFilesConfig,
    Paths,
    SettingsConfig,
    TokensConfig,
    UsersConfig,
    load_settings_config,
    load_tokens_config,
    load_users_config,
)


class TestConfigDataclasses:
    """Test configuration dataclasses."""

    def test_paths_creation(self) -> None:
        """Test Paths dataclass creation."""
        backup_dir = Path("/tmp/backup")
        update_db_dir = Path("/tmp/update_db")
        files_dir = Path("/tmp/files")
        sql_root = Path("/tmp/sql")
        sqlite_db_file = Path("/tmp/games.db")
        games_excel_file = Path("/tmp/games.xlsx")

        paths = Paths(
            backup_dir=backup_dir,
            update_db_dir=update_db_dir,
            files_dir=files_dir,
            sql_root=sql_root,
            sqlite_db_file=sqlite_db_file,
            games_excel_file=games_excel_file,
        )

        assert paths.backup_dir == backup_dir
        assert paths.update_db_dir == update_db_dir
        assert paths.files_dir == files_dir
        assert paths.sql_root == sql_root
        assert paths.sqlite_db_file == sqlite_db_file
        assert paths.games_excel_file == games_excel_file

    def test_paths_frozen(self) -> None:
        """Test that Paths is frozen (immutable)."""
        paths = Paths(
            backup_dir=Path("/tmp/backup"),
            update_db_dir=Path("/tmp/update_db"),
            files_dir=Path("/tmp/files"),
            sql_root=Path("/tmp/sql"),
            sqlite_db_file=Path("/tmp/games.db"),
            games_excel_file=Path("/tmp/games.xlsx"),
        )

        with pytest.raises(Exception):  # dataclass frozen raises
            paths.backup_dir = Path("/new/path")  # type: ignore

    def test_settings_config_creation(self) -> None:
        """Test SettingsConfig creation."""
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

        settings = SettingsConfig(
            paths=paths, db_files=db_files, owner_name="Alexander"
        )
        assert settings.paths == paths
        assert settings.db_files == db_files
        assert settings.owner_name == "Alexander"

    def test_tokens_config_creation(self) -> None:
        """Test TokensConfig creation."""
        tokens = TokensConfig(
            telegram_token="test_token",
            steam_key="test_steam_key",
            steam_id="test_steam_id",
        )

        assert tokens.telegram_token == "test_token"
        assert tokens.steam_key == "test_steam_key"
        assert tokens.steam_id == "test_steam_id"

    def test_users_config_creation(self) -> None:
        """Test UsersConfig creation."""
        users_cfg = UsersConfig(users=["12345", "67890"], admins=["12345"])

        assert users_cfg.users == ["12345", "67890"]
        assert users_cfg.admins == ["12345"]

    def test_users_config_empty(self) -> None:
        """Test UsersConfig with empty lists."""
        users_cfg = UsersConfig(users=[], admins=[])

        assert users_cfg.users == []
        assert users_cfg.admins == []


class TestConfigLoaders:
    """Test configuration loading functions."""

    def test_load_users_config(self, tmp_path: Path) -> None:
        """Test load_users_config with temporary config file."""
        # Create temporary users.ini
        users_ini = tmp_path / "users.ini"
        users_ini.write_text("[users]\n" "users = 12345 67890\n" "admins = 12345\n")

        # Mock PROJECT_ROOT to point to tmp_path
        import game_db.config as config_module

        original_root = config_module.PROJECT_ROOT
        config_module.PROJECT_ROOT = tmp_path

        try:
            # Create settings directory
            (tmp_path / "settings").mkdir()
            (tmp_path / "settings" / "users.ini").write_text(
                "[users]\n" "users = 12345 67890\n" "admins = 12345\n"
            )

            users_cfg = load_users_config()

            assert "12345" in users_cfg.users
            assert "67890" in users_cfg.users
            assert "12345" in users_cfg.admins
        finally:
            config_module.PROJECT_ROOT = original_root

    def test_load_users_config_empty(self, tmp_path: Path) -> None:
        """Test load_users_config with empty values."""
        import game_db.config as config_module

        original_root = config_module.PROJECT_ROOT
        config_module.PROJECT_ROOT = tmp_path

        try:
            # Create settings directory
            (tmp_path / "settings").mkdir()
            (tmp_path / "settings" / "users.ini").write_text(
                "[users]\n" "users = \n" "admins = \n"
            )

            users_cfg = load_users_config()

            assert users_cfg.users == []
            assert users_cfg.admins == []
        finally:
            config_module.PROJECT_ROOT = original_root

    def test_load_tokens_config(self, tmp_path: Path) -> None:
        """Test load_tokens_config with temporary config file."""
        import game_db.config as config_module

        original_root = config_module.PROJECT_ROOT
        config_module.PROJECT_ROOT = tmp_path

        try:
            # Create settings directory
            (tmp_path / "settings").mkdir()
            (tmp_path / "settings" / "t_token.ini").write_text(
                "[token]\n"
                "token = test_telegram_token\n"
                "steam_key = test_steam_key\n"
                "steam_id = test_steam_id\n"
            )

            tokens_cfg = load_tokens_config()

            assert tokens_cfg.telegram_token == "test_telegram_token"
            assert tokens_cfg.steam_key == "test_steam_key"
            assert tokens_cfg.steam_id == "test_steam_id"
        finally:
            config_module.PROJECT_ROOT = original_root

    def test_load_settings_config(self, tmp_path: Path) -> None:
        """Test load_settings_config with temporary config file."""
        import game_db.config as config_module

        original_root = config_module.PROJECT_ROOT
        config_module.PROJECT_ROOT = tmp_path

        try:
            # Create settings directory and files
            (tmp_path / "settings").mkdir()
            (tmp_path / "settings" / "settings.ini").write_text(
                "[FILES]\n"
                "sql_games = sql_querry/create_db/dml/dml_games.sql\n"
                "sql_games_on_platforms = sql_querry/create_db/dml/dml_games_on_platforms.sql\n"
                "sql_dictionaries = sql_querry/create_db/dml/dml_dictionaries.sql\n"
                "sql_drop_tables = sql_querry/create_db/drop_tables.sql\n"
                "sql_create_tables = sql_querry/create_db/create_tables.sql\n"
                "sqlite_db_file = games.db\n"
            )
            (tmp_path / "backup_db").mkdir()
            (tmp_path / "update_db").mkdir()
            (tmp_path / "files").mkdir()
            (tmp_path / "sql_querry").mkdir()

            settings_cfg = load_settings_config()

            assert settings_cfg.paths.backup_dir == tmp_path / "backup_db"
            assert settings_cfg.paths.update_db_dir == tmp_path / "update_db"
            assert settings_cfg.paths.files_dir == tmp_path / "files"
            assert settings_cfg.paths.sql_root == tmp_path / "sql_querry"
            assert settings_cfg.paths.sqlite_db_file == tmp_path / "games.db"
            assert (
                settings_cfg.paths.games_excel_file
                == tmp_path / "backup_db" / "games.xlsx"
            )
            # Test default owner_name when OWNER section is missing
            assert settings_cfg.owner_name == "Alexander"
        finally:
            config_module.PROJECT_ROOT = original_root

    def test_load_settings_config_with_owner_name(self, tmp_path: Path) -> None:
        """Test load_settings_config loads owner_name from OWNER section."""
        import game_db.config as config_module

        original_root = config_module.PROJECT_ROOT
        config_module.PROJECT_ROOT = tmp_path

        try:
            # Create settings directory and files
            (tmp_path / "settings").mkdir()
            (tmp_path / "settings" / "settings.ini").write_text(
                "[FILES]\n"
                "sql_games = sql_querry/create_db/dml/dml_games.sql\n"
                "sql_games_on_platforms = sql_querry/create_db/dml/dml_games_on_platforms.sql\n"
                "sql_dictionaries = sql_querry/create_db/dml/dml_dictionaries.sql\n"
                "sql_drop_tables = sql_querry/create_db/drop_tables.sql\n"
                "sql_create_tables = sql_querry/create_db/create_tables.sql\n"
                "sqlite_db_file = games.db\n"
                "\n"
                "[OWNER]\n"
                "owner_name = John\n"
            )
            (tmp_path / "backup_db").mkdir()
            (tmp_path / "update_db").mkdir()
            (tmp_path / "files").mkdir()
            (tmp_path / "sql_querry").mkdir()

            settings_cfg = load_settings_config()

            assert settings_cfg.owner_name == "John"
        finally:
            config_module.PROJECT_ROOT = original_root

    def test_load_settings_config_owner_name_default(self, tmp_path: Path) -> None:
        """Test load_settings_config uses default owner_name when OWNER section is missing."""
        import game_db.config as config_module

        original_root = config_module.PROJECT_ROOT
        config_module.PROJECT_ROOT = tmp_path

        try:
            # Create settings directory and files (without OWNER section)
            (tmp_path / "settings").mkdir()
            (tmp_path / "settings" / "settings.ini").write_text(
                "[FILES]\n"
                "sql_games = sql_querry/create_db/dml/dml_games.sql\n"
                "sql_games_on_platforms = sql_querry/create_db/dml/dml_games_on_platforms.sql\n"
                "sql_dictionaries = sql_querry/create_db/dml/dml_dictionaries.sql\n"
                "sql_drop_tables = sql_querry/create_db/drop_tables.sql\n"
                "sql_create_tables = sql_querry/create_db/create_tables.sql\n"
                "sqlite_db_file = games.db\n"
            )
            (tmp_path / "backup_db").mkdir()
            (tmp_path / "update_db").mkdir()
            (tmp_path / "files").mkdir()
            (tmp_path / "sql_querry").mkdir()

            settings_cfg = load_settings_config()

            # Should default to "Alexander" when OWNER section is missing
            assert settings_cfg.owner_name == "Alexander"
        finally:
            config_module.PROJECT_ROOT = original_root


class TestDefaultPlatforms:
    """Test DEFAULT_PLATFORMS constant."""

    def test_default_platforms_list(self) -> None:
        """Test that DEFAULT_PLATFORMS contains expected platforms."""
        expected_platforms = [
            "PC GOG",
            "PC Origin",
            "PS Vita",
            "PS4",
            "PS5",
            "Steam",
            "Switch",
        ]

        assert DEFAULT_PLATFORMS == expected_platforms

    def test_default_platforms_not_empty(self) -> None:
        """Test that DEFAULT_PLATFORMS is not empty."""
        assert len(DEFAULT_PLATFORMS) > 0

    def test_default_platforms_all_strings(self) -> None:
        """Test that all items in DEFAULT_PLATFORMS are strings."""
        assert all(isinstance(platform, str) for platform in DEFAULT_PLATFORMS)
