"""Database management service for high-level DB operations.

This service encapsulates operations like recreating the database from Excel,
adding games, and synchronizing with Steam. It uses typed configuration objects
and dependency injection for better testability and maintainability.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..config import (
    SettingsConfig,
    TokensConfig,
    load_table_names_config,
    load_column_table_names_config,
    load_values_dictionaries_config,
)
from ..db import (
    DatabaseManager,
    HowLongToBeatSynchronizer,
    MetacriticSynchronizer,
    SteamSynchronizer,
)
from ..db_dictionaries import DictionariesBuilder
from ..db_excel import ExcelImporter

logger = logging.getLogger("game_db.services.database")


class DatabaseService:
    """Service for database operations: recreation, game management, Steam sync.

    This service provides high-level operations for managing the game database.
    It accepts typed configuration objects and uses dependency injection for
    better testability.

    Args:
        settings: Application settings configuration
        tokens: Tokens configuration (for Steam API)
    """

    def __init__(
        self,
        settings: SettingsConfig,
        tokens: TokensConfig,
    ) -> None:
        """Initialize database service with configuration.

        Args:
            settings: Application settings configuration
            tokens: Tokens configuration for Steam API
        """
        self.settings = settings
        self.tokens = tokens

        # Load dictionary configs (still using ConfigParser for backward compatibility)
        self.table_names = load_table_names_config()
        self.column_table_names = load_column_table_names_config()
        self.values_dictionaries = load_values_dictionaries_config()

        # Initialize components
        self.db_manager = DatabaseManager()
        self.dictionaries_builder = DictionariesBuilder(
            self.table_names,
            self.column_table_names,
            self.values_dictionaries,
        )
        self.excel_importer = ExcelImporter(
            self.settings,
            self.table_names,
            self.column_table_names,
            self.values_dictionaries,
            self.db_manager,
        )
        self.steam_synchronizer = SteamSynchronizer(
            self.tokens,
            self.excel_importer,
            self.db_manager,
            self.settings,
        )
        self.metacritic_synchronizer = MetacriticSynchronizer(
            self.excel_importer,
            self.db_manager,
            self.settings,
            test_mode=False,  # Can be set via environment variable or config
        )
        # HLTB synchronizer is created on-demand to avoid import errors
        # if library is not installed
        self._hltb_synchronizer: HowLongToBeatSynchronizer | None = None

    def recreate_db(self, xlsx: str | Path) -> bool:
        """Drop, recreate and fill database from Excel file.

        This operation:
        1. Drops all existing tables
        2. Creates new tables
        3. Populates dictionary tables (status, platform)
        4. Imports games from Excel file

        Args:
            xlsx: Path to Excel file containing game data

        Returns:
            True if operation succeeded, False otherwise
        """
        xlsx_path = Path(xlsx)
        logger.info(
            "[DB_RECREATION] Starting database recreation from Excel file: %s",
            xlsx_path,
        )

        db_files = self.settings.db_files

        # Drop existing tables
        self.db_manager.execute_scripts_from_sql_file(
            db_files.sql_drop_tables,
            db_files.sqlite_db_file,
        )

        # Create new tables
        self.db_manager.execute_scripts_from_sql_file(
            db_files.sql_create_tables,
            db_files.sqlite_db_file,
        )

        # Populate dictionaries
        self.db_manager.execute_scripts_from_sql_file(
            db_files.sql_dictionaries,
            db_files.sqlite_db_file,
        )

        # Import games from Excel
        result = self.excel_importer.add_games(str(xlsx_path), "full")
        if result:
            logger.info(
                "[DB_RECREATION] Successfully recreated database from %s",
                xlsx_path,
            )
        else:
            logger.error(
                "[DB_RECREATION] Failed to recreate database from %s",
                xlsx_path,
                exc_info=True,
            )

        return result

    def add_games(self, xlsx: str | Path, mode: str) -> bool:
        """Add games from Excel file to existing database.

        Args:
            xlsx: Path to Excel file containing game data
            mode: Import mode ("full" or "update")

        Returns:
            True if operation succeeded, False otherwise
        """
        xlsx_path = Path(xlsx)
        logger.info(
            "[DB_UPDATE] Adding games from Excel file: %s (mode: %s)",
            xlsx_path,
            mode,
        )
        return self.excel_importer.add_games(str(xlsx_path), mode)

    def synchronize_steam_games(
        self, xlsx_path: str | Path
    ) -> tuple[bool, list]:
        """Synchronize Steam playtime and dates with Excel and recreate DB.

        This operation:
        1. Fetches game data from Steam API
        2. Updates Excel file with playtime and last launch dates
        3. Finds similar games for missing ones
        4. Recreates the database with updated data

        Args:
            xlsx_path: Path to Excel file to update

        Returns:
            Tuple of (success: bool, similarity_matches: list)
        """
        xlsx = Path(xlsx_path)
        logger.info(
            "[STEAM_SYNC] Starting Steam synchronization with Excel file: %s",
            xlsx,
        )
        return self.steam_synchronizer.synchronize_steam_games(str(xlsx))

    def synchronize_metacritic_games(
        self,
        xlsx_path: str | Path,
        test_mode: bool = False,
        partial_mode: bool = False,
    ) -> bool | None:
        """Synchronize Metacritic data with Excel and recreate DB.

        This operation:
        1. Reads games from Excel that have Metacritic URLs
        2. Fetches data from Metacritic for each game (with 10s delay)
        3. Updates Excel file with release date, scores, and URL
        4. Recreates the database with updated data

        Args:
            xlsx_path: Path to Excel file to update
            test_mode: If True, limit to 20 games for testing
            partial_mode: If True, only sync games missing press_score or user_score

        Returns:
            True if operation succeeded, False otherwise
        """
        xlsx = Path(xlsx_path)
        logger.info(
            "[METACRITIC_SYNC] Starting Metacritic synchronization with Excel file: %s (test_mode: %s, partial_mode: %s)",
            xlsx,
            test_mode,
            partial_mode,
        )

        # Create synchronizer with test mode setting
        synchronizer = MetacriticSynchronizer(
            self.excel_importer,
            self.db_manager,
            self.settings,
            test_mode=test_mode,
        )
        return synchronizer.synchronize_metacritic_games(
            str(xlsx), partial_mode=partial_mode
        )

    def synchronize_hltb_games(
        self,
        xlsx_path: str | Path,
        test_mode: bool = False,
        partial_mode: bool = False,
    ) -> bool | None:
        """Synchronize HowLongToBeat data with Excel and recreate DB.

        This operation:
        1. Reads all games from Excel
        2. Fetches completion time data from HowLongToBeat for each game (with 10s delay)
        3. Updates Excel file with average time to beat
        4. Recreates the database with updated data

        Args:
            xlsx_path: Path to Excel file to update
            test_mode: If True, limit to 20 games for testing
            partial_mode: If True, only sync games missing average_time_beat

        Returns:
            True if operation succeeded, False if error, None if no data to sync
        """
        xlsx = Path(xlsx_path)
        logger.info(
            "[HLTB_SYNC] Starting HowLongToBeat synchronization with Excel file: %s (test_mode: %s, partial_mode: %s)",
            xlsx,
            test_mode,
            partial_mode,
        )

        # Create synchronizer on-demand (lazy initialization)
        if self._hltb_synchronizer is None:
            self._hltb_synchronizer = HowLongToBeatSynchronizer(
                self.excel_importer,
                self.db_manager,
                self.settings,
                test_mode=test_mode,
            )
        else:
            # Update test_mode if synchronizer already exists
            self._hltb_synchronizer.test_mode = test_mode

        return self._hltb_synchronizer.synchronize_hltb_games(
            str(xlsx), partial_mode=partial_mode
        )

    def create_dml_dictionaries(self, sql_dictionaries: str | Path) -> None:
        """Generate SQL file for dictionary inserts (status/platform).

        Args:
            sql_dictionaries: Path to output SQL file
        """
        sql_path = Path(sql_dictionaries)
        logger.info(
            "[DML_GENERATION] Creating DML dictionaries file: %s", sql_path
        )
        self.dictionaries_builder.create_dml_dictionaries(str(sql_path))
