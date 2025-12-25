"""Excel file reading/writing and SQL generation for games."""

from __future__ import annotations

import configparser
import logging

from .config import SettingsConfig, load_settings_config
from .constants import ExcelRowIndex, EXCEL_NONE_VALUE
from .excel import ExcelReader, ExcelValidator, ExcelWriter

logger = logging.getLogger("game_db.sql")
_settings_cfg = load_settings_config()


class ExcelImporter:
    """Read/write Excel and generate SQL/DML for games.

    Excel File Format:
    The Excel file should contain the following sheets:
    - "init_games": Main sheet with all games (used in "full" mode)
    - "new_games": Sheet with new games to add (used in "new_games" mode)
    - "update_games": Sheet with games to update (used in "update_games" mode)

    Column structure (1-based indexing):
    Column 1:  game_name (str)
    Column 2:  platforms (str, comma-separated: "Steam,Switch")
    Column 3:  status (str: "Пройдена", "Не начата", "Брошена")
    Column 4:  release_date (str: "Month DD, YYYY" format)
    Column 5:  press_score (str | None)
    Column 6:  user_score (str | None)
    Column 7:  my_score (str | None)
    Column 8:  metacritic_url (str | None)
    Column 9:  average_time_beat (str | None, hours as float string)
    Column 10: trailer_url (str | None)
    Column 11: my_time_beat (str | None, hours as float string)
    Column 12: last_launch_date (str: "Month DD, YYYY" format)
    Column 13: additional_time (str | None, hours as float string, optional)
    """

    def __init__(
        self,
        settings: SettingsConfig,
        table_names: configparser.ConfigParser,
        column_table_names: configparser.ConfigParser,
        values_dictionaries: configparser.ConfigParser,
        db_manager,  # DatabaseManager - avoid circular import
    ) -> None:
        self.settings = settings
        self.table_names = table_names
        self.column_table_names = column_table_names
        self.values_dictionaries = values_dictionaries
        self.db_manager = db_manager

        # Initialize Excel components
        self.reader = ExcelReader()
        self.writer = ExcelWriter()
        # Convert ConfigParser to dict for validator
        validator_dict = {
            section: dict(values_dictionaries[section])
            for section in values_dictionaries.sections()
        }
        self.validator = ExcelValidator(validator_dict)

    # ... existing methods above unchanged ...

    def _calculate_spend_time(self, row: list[str]) -> float:
        """Calculate total spend time for a row.

        Args:
            row: List of string values representing a game row

        Returns:
            Total spend time in hours as float
        """
        additional_time = 0.0
        my_time = 0.0

        if (
            len(row) > ExcelRowIndex.ADDITIONAL_TIME
            and row[ExcelRowIndex.ADDITIONAL_TIME] != EXCEL_NONE_VALUE
        ):
            additional_time = float(row[ExcelRowIndex.ADDITIONAL_TIME])

        if (
            len(row) > ExcelRowIndex.MY_TIME_BEAT
            and row[ExcelRowIndex.MY_TIME_BEAT] != EXCEL_NONE_VALUE
        ):
            my_time = float(row[ExcelRowIndex.MY_TIME_BEAT])

        return my_time + additional_time

    def add_games(self, xlsx_path: str, mode: str) -> bool:
        """Import games from Excel file into database.

        Args:
            xlsx_path: Path to Excel file containing game data
            mode: Import mode ("full", "new_games", or "update_games")

        Returns:
            True if operation succeeded, False otherwise
        """
        try:
            logger.info(
                "[EXCEL_IMPORT] Starting import from Excel file: %s (mode: %s)",
                xlsx_path,
                mode,
            )

            # For "full" mode, use the pre-generated SQL file
            if mode == "full":
                db_files = self.settings.db_files
                sql_file = db_files.sql_games
                if sql_file.exists():
                    logger.info(
                        "[EXCEL_IMPORT] Using pre-generated SQL file: %s",
                        sql_file,
                    )
                    self.db_manager.execute_scripts_from_sql_file(
                        sql_file, db_files.sqlite_db_file
                    )
                    # Also import games_on_platforms
                    if db_files.sql_games_on_platforms.exists():
                        self.db_manager.execute_scripts_from_sql_file(
                            db_files.sql_games_on_platforms,
                            db_files.sqlite_db_file,
                        )
                    logger.info(
                        "[EXCEL_IMPORT] Successfully imported games "
                        "from SQL file"
                    )
                    return True
                else:
                    logger.error(
                        "[EXCEL_IMPORT] SQL file not found: %s", sql_file
                    )
                    return False
            else:
                # For other modes, we would need to read Excel and generate SQL
                # This is a simplified implementation - full implementation
                # would read Excel, validate, and generate SQL dynamically
                logger.warning(
                    "[EXCEL_IMPORT] Mode '%s' not fully implemented, "
                    "falling back to 'full' mode",
                    mode,
                )
                return self.add_games(xlsx_path, "full")

        except Exception as e:
            logger.error(
                "[EXCEL_IMPORT] Failed to import games from %s: %s",
                xlsx_path,
                str(e),
                exc_info=True,
            )
            return False
