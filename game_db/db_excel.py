"""Excel file reading/writing and SQL generation for games."""

from __future__ import annotations

import configparser
import logging
import uuid
from datetime import datetime
from pathlib import Path

from .config import SettingsConfig, load_settings_config
from .constants import (
    DB_DATE_NOT_SET,
    ExcelColumn,
    ExcelRowIndex,
    EXCEL_DATE_NOT_SET,
    EXCEL_NONE_VALUE,
)
from .excel import ExcelReader, ExcelValidator, ExcelWriter
from .excel.models import GameRow

logger = logging.getLogger("game_db.sql")
_settings_cfg = load_settings_config()


class ExcelImporter:
    """Read/write Excel and generate SQL/DML for games.

    Excel File Format:
    The Excel file should contain the following sheet:
    - "init_games": Main sheet with all games

    Column structure (1-based indexing):
    Column 1:  game_name (str)
    Column 2:  platforms (str, comma-separated: "Steam,Switch")
    Column 3:  status (str: "Completed", "Not Started", "Dropped")
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
            mode: Import mode ("full")

        Returns:
            True if operation succeeded, False otherwise
        """
        try:
            logger.info(
                "[EXCEL_IMPORT] Starting import from Excel file: %s (mode: %s)",
                xlsx_path,
                mode,
            )

            if mode != "full":
                logger.error(
                    "[EXCEL_IMPORT] Unsupported mode '%s'. Only 'full' mode is supported.",
                    mode,
                )
                return False

            db_files = self.settings.db_files

            # Generate SQL files from Excel
            logger.info(
                "[EXCEL_IMPORT] Generating SQL files from Excel: %s",
                xlsx_path,
            )
            game_id_map = self.generate_dml_games_sql(xlsx_path, db_files.sql_games)
            self.generate_dml_games_on_platforms_sql(
                xlsx_path, db_files.sql_games_on_platforms, game_id_map
            )

            # Now use the generated SQL files
            sql_file = db_files.sql_games
            if sql_file.exists():
                logger.info(
                    "[EXCEL_IMPORT] Using generated SQL file: %s",
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
                    "[EXCEL_IMPORT] Successfully imported games " "from SQL file"
                )
                return True
            else:
                logger.error("[EXCEL_IMPORT] Failed to generate SQL file: %s", sql_file)
                return False

        except Exception as e:
            logger.error(
                "[EXCEL_IMPORT] Failed to import games from %s: %s",
                xlsx_path,
                str(e),
                exc_info=True,
            )
            return False

    def _parse_excel_date_to_db_date(self, date_str: str | None) -> str:
        """Convert Excel date format "Month DD, YYYY" to DB format "YYYY-MM-DD".

        Args:
            date_str: Date string in Excel format ("Month DD, YYYY") or None

        Returns:
            Date string in DB format ("YYYY-MM-DD") or DB_DATE_NOT_SET
        """
        if not date_str or date_str == EXCEL_DATE_NOT_SET:
            return DB_DATE_NOT_SET

        try:
            # Parse "Month DD, YYYY" or "Month D, YYYY" format
            # Example: "May 2, 2024" or "May 02, 2024" -> datetime(2024, 5, 2)
            import re

            date_str_clean = date_str.strip()
            # Normalize: ensure day has leading zero if it's a single digit
            # "May 2, 2024" -> "May 02, 2024"
            date_str_normalized = re.sub(r"(\w+) (\d{1}),", r"\1 0\2,", date_str_clean)
            date_obj = datetime.strptime(date_str_normalized, "%B %d, %Y")
            return date_obj.strftime("%Y-%m-%d")
        except (ValueError, AttributeError) as e:
            logger.warning(
                "[SQL_GENERATION] Failed to parse date: %s (%s), using default",
                date_str,
                str(e),
            )
            return DB_DATE_NOT_SET

    def _escape_sql_string(self, value: str | None) -> str:
        """Escape SQL string value for INSERT statement.

        Args:
            value: String value to escape

        Returns:
            Escaped string value
        """
        if value is None:
            return "none"
        value_str = str(value).strip()
        if not value_str or value_str == EXCEL_NONE_VALUE:
            return "none"
        # Escape single quotes by doubling them
        return value_str.replace("'", "''")

    def _format_sql_value(self, value: str | None, field_type: str = "str") -> str:
        """Format value for SQL INSERT statement.

        Args:
            value: Value to format
            field_type: Type of field ("str", "float", "int")

        Returns:
            Formatted SQL value string
        """
        if value is None or value == "" or value == EXCEL_NONE_VALUE:
            if field_type == "str":
                return '"none"'
            return "0.0" if field_type == "float" else "0"

        value_str = str(value).strip()
        if not value_str or value_str == EXCEL_NONE_VALUE:
            if field_type == "str":
                return '"none"'
            return "0.0" if field_type == "float" else "0"

        if field_type == "str":
            escaped = self._escape_sql_string(value_str)
            return f'"{escaped}"'
        elif field_type == "float":
            try:
                float_val = float(value_str)
                return str(float_val)
            except (ValueError, TypeError):
                return "0.0"
        elif field_type == "int":
            try:
                int_val = int(float(value_str))
                return str(int_val)
            except (ValueError, TypeError):
                return "0"
        return f'"{value_str}"'

    def generate_dml_games_sql(
        self, xlsx_path: str | Path, sql_games_path: str | Path
    ) -> dict[str, str]:
        """Generate dml_games.sql file from Excel file.

        Args:
            xlsx_path: Path to Excel file
            sql_games_path: Path to output SQL file

        Returns:
            Dictionary mapping game_name -> game_id for use in platforms SQL
        """
        logger.info(
            "[SQL_GENERATION] Generating dml_games.sql from Excel: %s",
            xlsx_path,
        )

        workbook = self.reader.load_workbook(xlsx_path)
        sheet = self.reader.get_sheet(workbook, "init_games")

        # Read all game rows
        game_rows = self.reader.read_game_rows(sheet)

        # Remove existing SQL file
        sql_games_path = Path(sql_games_path)
        if sql_games_path.exists():
            sql_games_path.unlink()

        # Dictionary to store game_name -> game_id mapping
        game_id_map: dict[str, str] = {}

        # Write SQL file
        with open(sql_games_path, "w", encoding="utf-8") as f:
            f.write(
                "INSERT INTO games "
                "(game_id, game_name, status, release_date, press_score, "
                "user_score, my_score, metacritic_url, average_time_beat, "
                "trailer_url, my_time_beat, last_launch_date)\n"
            )
            f.write("VALUES\n")

            # First pass: validate and collect valid rows
            # Note: game_rows already skips header (row 1), so first row is row 2
            valid_game_rows: list[tuple[GameRow, int]] = []
            for i, game_row in enumerate(game_rows):
                is_valid, errors = self.validator.validate_game_row(game_row)
                if not is_valid:
                    # Excel row number = index + 2 (since we skip row 1 header)
                    excel_row_num = i + 2
                    logger.warning(
                        "[SQL_GENERATION] Skipping invalid row %d: %s",
                        excel_row_num,
                        ", ".join(errors),
                    )
                    continue
                # Excel row number = index + 2 (since we skip row 1 header)
                excel_row_num = i + 2
                valid_game_rows.append((game_row, excel_row_num))

            # Second pass: generate SQL for valid rows
            for idx, (game_row, excel_row_num) in enumerate(valid_game_rows):
                # Generate GUID for game_id
                game_id = str(uuid.uuid4())
                game_id_map[game_row.game_name] = game_id

                # Get status ID
                status_id = self.validator.get_status_id(game_row.status)

                # Convert dates
                release_date_db = self._parse_excel_date_to_db_date(
                    game_row.release_date
                )
                last_launch_date_db = self._parse_excel_date_to_db_date(
                    game_row.last_launch_date
                )

                # Format values
                game_name = self._format_sql_value(game_row.game_name, "str")
                press_score = self._format_sql_value(game_row.press_score, "float")
                user_score = self._format_sql_value(game_row.user_score, "float")
                my_score = self._format_sql_value(game_row.my_score, "str")
                metacritic_url = self._format_sql_value(game_row.metacritic_url, "str")
                average_time_beat = self._format_sql_value(
                    game_row.average_time_beat, "float"
                )
                trailer_url = self._format_sql_value(game_row.trailer_url, "str")
                my_time_beat = self._format_sql_value(game_row.my_time_beat, "float")

                # Write INSERT statement
                f.write(
                    f'("{game_id}", {game_name}, "{status_id}", '
                    f'"{release_date_db}", {press_score}, {user_score}, '
                    f"{my_score}, {metacritic_url}, {average_time_beat}, "
                    f'{trailer_url}, {my_time_beat}, "{last_launch_date_db}")'
                )

                # Add comma or semicolon
                if idx < len(valid_game_rows) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")

        logger.info(
            "[SQL_GENERATION] Generated dml_games.sql with %d games",
            len(valid_game_rows),
        )
        return game_id_map

    def generate_dml_games_on_platforms_sql(
        self,
        xlsx_path: str | Path,
        sql_platforms_path: str | Path,
        game_id_map: dict[str, str],
    ) -> None:
        """Generate dml_games_on_platforms.sql file from Excel file.

        Args:
            xlsx_path: Path to Excel file
            sql_platforms_path: Path to output SQL file
            game_id_map: Dictionary mapping game_name -> game_id
        """
        logger.info(
            "[SQL_GENERATION] Generating dml_games_on_platforms.sql from Excel: %s",
            xlsx_path,
        )

        workbook = self.reader.load_workbook(xlsx_path)
        sheet = self.reader.get_sheet(workbook, "init_games")

        # Read all game rows
        game_rows = self.reader.read_game_rows(sheet)

        # Remove existing SQL file
        sql_platforms_path = Path(sql_platforms_path)
        if sql_platforms_path.exists():
            sql_platforms_path.unlink()

        # Write SQL file
        with open(sql_platforms_path, "w", encoding="utf-8") as f:
            f.write(
                "INSERT INTO games_on_platforms " "(platform_id, reference_game_id)\n"
            )
            f.write("VALUES\n")

            platform_entries: list[tuple[str, str]] = []

            for i, game_row in enumerate(game_rows):
                # Validate row
                is_valid, errors = self.validator.validate_game_row(game_row)
                if not is_valid:
                    # Excel row number = index + 2 (since we skip row 1 header)
                    excel_row_num = i + 2
                    logger.warning(
                        "[SQL_GENERATION] Skipping invalid row %d for platforms: %s",
                        excel_row_num,
                        ", ".join(errors),
                    )
                    continue

                # Get game_id from map
                game_id = game_id_map.get(game_row.game_name)
                if not game_id:
                    logger.warning(
                        "[SQL_GENERATION] Game ID not found for: %s",
                        game_row.game_name,
                    )
                    continue

                # Parse platforms (comma-separated)
                platforms = [
                    p.strip() for p in game_row.platforms.split(",") if p.strip()
                ]

                # Generate entries for each platform
                for platform in platforms:
                    platform_id = self.validator.get_platform_id(platform)
                    if platform_id != 1:  # Skip "not_defined"
                        platform_entries.append((str(platform_id), game_id))

            # Write all platform entries
            for i, (platform_id, ref_game_id) in enumerate(platform_entries):
                f.write(f'("{platform_id}", "{ref_game_id}")')
                if i < len(platform_entries) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")

        logger.info(
            "[SQL_GENERATION] Generated dml_games_on_platforms.sql with %d entries",
            len(platform_entries),
        )
