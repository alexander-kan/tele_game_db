"""Tests for ExcelImporter mapping and helper functions."""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

from game_db.config import DBFilesConfig, Paths, SettingsConfig
from game_db.constants import ExcelRowIndex, EXCEL_NONE_VALUE
from game_db.db_excel import ExcelImporter


def _make_excel_importer() -> ExcelImporter:
    settings = SettingsConfig(
        paths=Paths(
            backup_dir=Path("/tmp/backup"),
            update_db_dir=Path("/tmp/update_db"),
            files_dir=Path("/tmp/files"),
            sql_root=Path("/tmp/sql_root"),
            sqlite_db_file=Path("/tmp/test.db"),
            games_excel_file=Path("/tmp/backup/games.xlsx"),
        ),
        db_files=DBFilesConfig(
            sql_games=Path("games.sql"),
            sql_games_on_platforms=Path("games_on_platforms.sql"),
            sql_dictionaries=Path("dictionaries.sql"),
            sql_drop_tables=Path("drop_tables.sql"),
            sql_create_tables=Path("create_tables.sql"),
            sqlite_db_file=Path("/tmp/test.db"),
        ),
        owner_name="Alexander",
    )
    table_names = configparser.ConfigParser()
    column_table_names = configparser.ConfigParser()
    values_dictionaries = configparser.ConfigParser()
    return ExcelImporter(
        settings, table_names, column_table_names, values_dictionaries, None
    )


# ... many tests above unchanged ...


def test_calculate_spend_time_sums_both_fields() -> None:
    """_calculate_spend_time sums my_time_beat and additional_time."""
    importer = _make_excel_importer()
    row: list[str] = [""] * (ExcelRowIndex.ADDITIONAL_TIME + 1)
    row[ExcelRowIndex.MY_TIME_BEAT] = "2.5"
    row[ExcelRowIndex.ADDITIONAL_TIME] = "1.5"

    total = importer._calculate_spend_time(row)  # type: ignore[attr-defined]
    assert total == 4.0


def test_calculate_spend_time_ignores_none_strings() -> None:
    """_calculate_spend_time treats sentinel 'none' as zero."""
    importer = _make_excel_importer()
    row: list[str] = [""] * (ExcelRowIndex.ADDITIONAL_TIME + 1)
    row[ExcelRowIndex.MY_TIME_BEAT] = EXCEL_NONE_VALUE
    row[ExcelRowIndex.ADDITIONAL_TIME] = EXCEL_NONE_VALUE

    total = importer._calculate_spend_time(row)  # type: ignore[attr-defined]
    assert total == 0.0


# rest of file unchanged...
