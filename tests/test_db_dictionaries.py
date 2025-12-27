"""Tests for db_dictionaries module."""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

from game_db.db_dictionaries import DictionariesBuilder


class TestDictionariesBuilder:
    """Test DictionariesBuilder class."""

    @pytest.fixture
    def mock_configs(self) -> tuple[configparser.ConfigParser, ...]:
        """Create mock configuration parsers."""
        table_names = configparser.ConfigParser()
        table_names["TABLES"] = {
            "status_dictionary": "status_dictionary",
            "platform_dictionary": "platform_dictionary",
        }

        column_table_names = configparser.ConfigParser()
        column_table_names["status_dictionary"] = {
            "status_name": "status_name",
        }
        column_table_names["platform_dictionary"] = {
            "platform_name": "platform_name",
        }

        values_dictionaries = configparser.ConfigParser()
        values_dictionaries["STATUS"] = {
            "pass": "Completed",
            "not_started": "Not Started",
            "abandoned": "Dropped",
        }
        values_dictionaries["PLATFORM"] = {
            "not_defined": "NOT DEFINED",
            "steam": "Steam",
            "switch": "Switch",
            "ps4": "PS4",
            "ps_vita": "PS Vita",
            "pc_origin": "PC Origin",
            "pc_gog": "PC GOG",
            "ps5": "PS5",
            "n3ds": "N3DS",
        }

        return table_names, column_table_names, values_dictionaries

    @pytest.fixture
    def builder(
        self, mock_configs: tuple[configparser.ConfigParser, ...]
    ) -> DictionariesBuilder:
        """Create DictionariesBuilder instance."""
        table_names, column_table_names, values_dictionaries = mock_configs
        return DictionariesBuilder(table_names, column_table_names, values_dictionaries)

    def test_create_dml_dictionaries_creates_file(
        self, builder: DictionariesBuilder, tmp_path: Path
    ) -> None:
        """Test that create_dml_dictionaries creates SQL file."""
        sql_file = tmp_path / "dml_dictionaries.sql"

        builder.create_dml_dictionaries(str(sql_file))

        assert sql_file.exists()

    def test_create_dml_dictionaries_overwrites_existing(
        self, builder: DictionariesBuilder, tmp_path: Path
    ) -> None:
        """Test that create_dml_dictionaries overwrites existing file."""
        sql_file = tmp_path / "dml_dictionaries.sql"
        sql_file.write_text("old content")

        builder.create_dml_dictionaries(str(sql_file))

        content = sql_file.read_text()
        assert "old content" not in content

    def test_create_dml_dictionaries_status_inserts(
        self, builder: DictionariesBuilder, tmp_path: Path
    ) -> None:
        """Test that status dictionary SQL contains correct inserts."""
        sql_file = tmp_path / "dml_dictionaries.sql"

        builder.create_dml_dictionaries(str(sql_file))

        content = sql_file.read_text()
        assert "INSERT INTO" in content
        assert "status_dictionary" in content
        assert "status_name" in content
        assert "Completed" in content
        assert "Not Started" in content
        assert "Dropped" in content

    def test_create_dml_dictionaries_platform_inserts(
        self, builder: DictionariesBuilder, tmp_path: Path
    ) -> None:
        """Test that platform dictionary SQL contains correct inserts."""
        sql_file = tmp_path / "dml_dictionaries.sql"

        builder.create_dml_dictionaries(str(sql_file))

        content = sql_file.read_text()
        assert "platform_dictionary" in content
        assert "platform_name" in content
        # Check that all platforms from mock config are present
        assert "NOT DEFINED" in content
        assert "Steam" in content
        assert "Switch" in content
        assert "PS4" in content
        assert "PS Vita" in content
        assert "PC Origin" in content
        assert "PC GOG" in content
        assert "PS5" in content
        assert "N3DS" in content

    def test_create_dml_dictionaries_sql_structure(
        self, builder: DictionariesBuilder, tmp_path: Path
    ) -> None:
        """Test that generated SQL has correct structure."""
        sql_file = tmp_path / "dml_dictionaries.sql"

        builder.create_dml_dictionaries(str(sql_file))

        content = sql_file.read_text()
        # Check that both INSERT statements are present
        assert content.count("INSERT INTO") == 2
        assert content.count("VALUES") == 2
        # Check that status insert comes before platform insert
        status_pos = content.find("status_dictionary")
        platform_pos = content.find("platform_dictionary")
        assert status_pos < platform_pos
