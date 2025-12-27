"""Unit tests for database_service module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from game_db.services.database_service import DatabaseService
from game_db.config import SettingsConfig, DBFilesConfig, Paths, TokensConfig


@pytest.fixture
def test_settings() -> SettingsConfig:
    """Create test settings."""
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
def mock_excel_importer() -> Mock:
    """Create mock ExcelImporter."""
    importer = Mock()
    importer.add_games = Mock(return_value=True)
    return importer


@pytest.fixture
def mock_db_manager() -> Mock:
    """Create mock DatabaseManager."""
    manager = Mock()
    manager.execute_scripts_from_sql_file = Mock()
    return manager


def test_database_service_init(test_settings: SettingsConfig) -> None:
    """Test DatabaseService initialization."""
    tokens = TokensConfig(
        telegram_token="test_token",
        steam_key="test_key",
        steam_id="test_id",
    )
    service = DatabaseService(test_settings, tokens)

    assert service.settings == test_settings
    assert service.excel_importer is not None
    assert service.db_manager is not None


@pytest.fixture
def test_tokens() -> TokensConfig:
    """Create test tokens."""
    return TokensConfig(
        telegram_token="test_token",
        steam_key="test_key",
        steam_id="test_id",
    )


@patch("game_db.services.database_service.DatabaseManager")
@patch("game_db.services.database_service.ExcelImporter")
def test_recreate_db_success(
    mock_excel_importer_class: Mock,
    mock_db_manager_class: Mock,
    test_settings: SettingsConfig,
    test_tokens: TokensConfig,
) -> None:
    """Test successful database recreation."""
    mock_db_manager = mock_db_manager_class.return_value
    mock_excel_importer = mock_excel_importer_class.return_value
    mock_excel_importer.add_games.return_value = True

    service = DatabaseService(test_settings, test_tokens)
    result = service.recreate_db("/tmp/test.xlsx")

    assert result is True
    assert mock_db_manager.execute_scripts_from_sql_file.call_count == 3
    mock_excel_importer.add_games.assert_called_once_with("/tmp/test.xlsx", "full")


@patch("game_db.services.database_service.DatabaseManager")
@patch("game_db.services.database_service.ExcelImporter")
def test_recreate_db_failure(
    mock_excel_importer_class: Mock,
    mock_db_manager_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test database recreation failure."""
    mock_db_manager = mock_db_manager_class.return_value
    mock_excel_importer = mock_excel_importer_class.return_value
    mock_excel_importer.add_games.return_value = False

    service = DatabaseService(test_settings, test_tokens)
    result = service.recreate_db("/tmp/test.xlsx")

    assert result is False
    assert mock_db_manager.execute_scripts_from_sql_file.call_count == 3
    mock_excel_importer.add_games.assert_called_once_with("/tmp/test.xlsx", "full")


@patch("game_db.services.database_service.DatabaseManager")
@patch("game_db.services.database_service.ExcelImporter")
def test_add_games(
    mock_excel_importer_class: Mock,
    mock_db_manager_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test adding games."""
    mock_excel_importer = mock_excel_importer_class.return_value
    mock_excel_importer.add_games.return_value = True

    service = DatabaseService(test_settings, test_tokens)
    result = service.add_games("/tmp/test.xlsx", "full")

    assert result is True
    mock_excel_importer.add_games.assert_called_once_with("/tmp/test.xlsx", "full")


@patch("game_db.services.database_service.SteamSynchronizer")
def test_synchronize_steam_games(
    mock_steam_sync_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test Steam games synchronization."""
    mock_steam_sync = mock_steam_sync_class.return_value
    mock_steam_sync.synchronize_steam_games.return_value = (True, [])

    service = DatabaseService(test_settings, test_tokens)
    result = service.synchronize_steam_games("/tmp/test.xlsx")

    assert result == (True, [])
    mock_steam_sync.synchronize_steam_games.assert_called_once_with("/tmp/test.xlsx")


@patch("game_db.services.database_service.SteamSynchronizer")
def test_check_steam_games(
    mock_steam_sync_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test checking Steam games."""
    from game_db.similarity_search import SimilarityMatch

    mock_steam_sync = mock_steam_sync_class.return_value
    mock_matches = [
        SimilarityMatch(original="Game 1", closest_match=None, distance=5, score=0.5)
    ]
    mock_steam_sync.check_steam_games.return_value = mock_matches

    service = DatabaseService(test_settings, test_tokens)
    result = service.check_steam_games("/tmp/test.xlsx")

    assert result == mock_matches
    mock_steam_sync.check_steam_games.assert_called_once_with("/tmp/test.xlsx")


@patch("game_db.services.database_service.SteamSynchronizer")
def test_add_steam_games_to_excel(
    mock_steam_sync_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test adding Steam games to Excel."""
    mock_steam_sync = mock_steam_sync_class.return_value
    mock_steam_sync.add_steam_games_to_excel.return_value = True

    service = DatabaseService(test_settings, test_tokens)
    result = service.add_steam_games_to_excel("/tmp/test.xlsx", ["Game 1", "Game 2"])

    assert result is True
    mock_steam_sync.add_steam_games_to_excel.assert_called_once_with(
        "/tmp/test.xlsx", ["Game 1", "Game 2"]
    )


@patch("game_db.services.database_service.MetacriticSynchronizer")
def test_synchronize_metacritic_games(
    mock_metacritic_sync_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test Metacritic games synchronization."""
    mock_metacritic_sync = mock_metacritic_sync_class.return_value
    mock_metacritic_sync.synchronize_metacritic_games.return_value = True

    service = DatabaseService(test_settings, test_tokens)
    result = service.synchronize_metacritic_games("/tmp/test.xlsx", partial_mode=False)

    assert result is True
    mock_metacritic_sync.synchronize_metacritic_games.assert_called_once_with(
        "/tmp/test.xlsx", partial_mode=False
    )


@patch("game_db.services.database_service.MetacriticSynchronizer")
def test_synchronize_metacritic_games_partial(
    mock_metacritic_sync_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test Metacritic games synchronization in partial mode."""
    mock_metacritic_sync = mock_metacritic_sync_class.return_value
    mock_metacritic_sync.synchronize_metacritic_games.return_value = True

    service = DatabaseService(test_settings, test_tokens)
    result = service.synchronize_metacritic_games("/tmp/test.xlsx", partial_mode=True)

    assert result is True
    mock_metacritic_sync.synchronize_metacritic_games.assert_called_once_with(
        "/tmp/test.xlsx", partial_mode=True
    )


@patch("game_db.services.database_service.HowLongToBeatSynchronizer")
def test_synchronize_hltb_games(
    mock_hltb_sync_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test HowLongToBeat games synchronization."""
    mock_hltb_sync = mock_hltb_sync_class.return_value
    mock_hltb_sync.synchronize_hltb_games.return_value = True

    service = DatabaseService(test_settings, test_tokens)
    result = service.synchronize_hltb_games("/tmp/test.xlsx", partial_mode=False)

    assert result is True
    mock_hltb_sync.synchronize_hltb_games.assert_called_once_with(
        "/tmp/test.xlsx", partial_mode=False
    )


@patch("game_db.services.database_service.HowLongToBeatSynchronizer")
def test_synchronize_hltb_games_partial(
    mock_hltb_sync_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test HowLongToBeat games synchronization in partial mode."""
    mock_hltb_sync = mock_hltb_sync_class.return_value
    mock_hltb_sync.synchronize_hltb_games.return_value = True

    service = DatabaseService(test_settings, test_tokens)
    result = service.synchronize_hltb_games("/tmp/test.xlsx", partial_mode=True)

    assert result is True
    mock_hltb_sync.synchronize_hltb_games.assert_called_once_with(
        "/tmp/test.xlsx", partial_mode=True
    )


@patch("game_db.services.database_service.DictionariesBuilder")
def test_create_dml_dictionaries(
    mock_dictionaries_builder_class: Mock,
    test_settings: SettingsConfig,
) -> None:
    """Test creating DML dictionaries."""
    mock_builder = mock_dictionaries_builder_class.return_value
    mock_builder.create_dml_dictionaries = Mock()

    service = DatabaseService(test_settings, test_tokens)
    service.create_dml_dictionaries("/tmp/dictionaries.sql")

    mock_builder.create_dml_dictionaries.assert_called_once_with(
        "/tmp/dictionaries.sql"
    )
