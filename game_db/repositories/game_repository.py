"""Repository for game-related database queries."""

from __future__ import annotations

import functools
import logging
import sqlite3
from pathlib import Path

from ..config import PROJECT_ROOT, load_settings_config
from ..exceptions import (DatabaseConnectionError, DatabaseQueryError,
                          SQLFileNotFoundError)

logger = logging.getLogger("game_db.sql")
_settings_cfg = load_settings_config()

# SQL files used by the repository
_REQUIRED_SQL_FILES = [
    "query_game.sql",
    "get_next_game_list.sql",
    "count_complete_games.sql",
    "count_spend_time_completed.sql",
    "count_spend_time.sql",
]


class GameRepository:
    """Repository for game database queries.

    This class encapsulates all SQL queries related to games,
    providing a clean interface without exposing raw SQL/cursors.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        """Initialize repository with database path.

        Args:
            db_path: Optional path to SQLite database.
                If None, uses path from settings (loaded at module import time).
                **Recommended**: Pass `db_path` explicitly, e.g.,
                `SettingsConfig.paths.sqlite_db_file`, to avoid implicit
                dependency on global configuration state.

        Note:
            The default behavior (when `db_path` is None) loads the database
            path from `SettingsConfig` at module import time. While this works
            for backward compatibility, explicitly passing the database path
            is recommended for better dependency injection and testability.
        """
        if db_path is None:
            # Fallback to global config for backward compatibility
            # This is loaded at module import time, not ideal for DI
            self.db_path = _settings_cfg.paths.sqlite_db_file
        else:
            self.db_path = Path(db_path)
        # Validate SQL files on initialization
        self._validate_sql_files()

    @staticmethod
    @functools.lru_cache(maxsize=32)
    def _load_sql_cached(sql_file: str) -> str:
        """Load SQL query from file with caching.

        This method is cached to avoid reading SQL files on every query.
        The cache is shared across all instances of GameRepository.

        Args:
            sql_file: Relative path from sql_querry/queries/

        Returns:
            SQL query string

        Raises:
            SQLFileNotFoundError: If SQL file cannot be found or read
        """
        sql_path = PROJECT_ROOT / "sql_querry" / "queries" / sql_file
        try:
            with open(sql_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.debug("Loaded SQL file: %s", sql_file)
                return content
        except FileNotFoundError as e:
            logger.error(
                "SQL file not found: %s (full path: %s)",
                sql_file,
                sql_path,
            )
            raise SQLFileNotFoundError(str(sql_path)) from e
        except OSError as e:
            logger.error(
                "Failed to read SQL file: %s (full path: %s)",
                sql_file,
                sql_path,
                exc_info=True,
            )
            raise SQLFileNotFoundError(str(sql_path)) from e

    def _load_sql(self, sql_file: str) -> str:
        """Load SQL query from file (wrapper for cached method).

        Args:
            sql_file: Relative path from sql_querry/queries/

        Returns:
            SQL query string

        Raises:
            SQLFileNotFoundError: If SQL file cannot be found or read
        """
        return self._load_sql_cached(sql_file)

    def _validate_sql_files(self) -> None:
        """Validate that all required SQL files exist and are readable.

        This method is called during initialization to ensure all SQL files
        are available before any queries are executed.

        Raises:
            SQLFileNotFoundError: If any required SQL file is missing
        """
        queries_dir = PROJECT_ROOT / "sql_querry" / "queries"
        missing_files: list[str] = []

        for sql_file in _REQUIRED_SQL_FILES:
            sql_path = queries_dir / sql_file
            if not sql_path.exists():
                missing_files.append(str(sql_path))
                logger.error("Required SQL file not found: %s", sql_path)
            elif not sql_path.is_file():
                missing_files.append(str(sql_path))
                logger.error("SQL path is not a file: %s", sql_path)
            else:
                # Try to read the file to ensure it's readable
                try:
                    with open(sql_path, "r", encoding="utf-8") as f:
                        f.read()
                    logger.debug("Validated SQL file: %s", sql_file)
                except OSError as e:
                    missing_files.append(str(sql_path))
                    logger.error(
                        "SQL file is not readable: %s - %s",
                        sql_path,
                        str(e),
                    )

        if missing_files:
            raise SQLFileNotFoundError(
                f"Missing or unreadable SQL files: {', '.join(missing_files)}"
            )

        logger.info("Validated %d SQL files successfully", len(_REQUIRED_SQL_FILES))

    @staticmethod
    def clear_sql_cache() -> None:
        """Clear the SQL file cache.

        Useful for testing or when SQL files are updated during runtime.
        """
        GameRepository._load_sql_cached.cache_clear()
        logger.debug("SQL cache cleared")

    def _execute_query(self, sql: str, params: tuple | None = None) -> list[tuple]:
        """Execute a SELECT query and return results.

        Args:
            sql: SQL query string
            params: Optional query parameters

        Returns:
            List of result tuples

        Raises:
            DatabaseConnectionError: If unable to connect to database
            DatabaseQueryError: If query execution fails
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
        except sqlite3.Error as e:
            logger.error(
                "Failed to connect to database: %s",
                self.db_path,
                exc_info=True,
            )
            raise DatabaseConnectionError(
                f"Failed to connect to database at {self.db_path}",
                original_error=e,
            ) from e

        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(
                "SQLite error executing query. SQL: %s, Params: %s",
                sql[:100] if len(sql) > 100 else sql,
                params,
                exc_info=True,
            )
            raise DatabaseQueryError(
                f"Failed to execute query: {str(e)}",
                sql=sql,
                params=params,
                original_error=e,
            ) from e
        finally:
            conn.close()

    def query_game(self, game_name: str) -> list[tuple]:
        """Query game info by name from the database.

        Args:
            game_name: Game name or search term (may contain "getgame" prefix
                and "#" suffix for exact match)

        Returns:
            List of tuples with game information:
            (game_name, status, platforms, press_score, average_time_beat,
             user_score, my_score, metacritic_url, trailer_url,
             my_time_beat, last_launch_date)

        Raises:
            DatabaseQueryError: If query execution fails
            SQLFileNotFoundError: If SQL file cannot be found
        """
        # Clean up game name
        if game_name and game_name[-1] == "#":
            game_name = game_name.replace("#", "")
        term = game_name.replace("getgame", "", 1).strip()
        like_term = f"%{term}%"

        logger.debug("Querying game: %s (search term: %s)", game_name, term)
        sql = self._load_sql("query_game.sql")
        return self._execute_query(sql, (like_term,))

    def get_next_game_list(
        self, from_row: int, how_much_row: int, platform: str
    ) -> list[tuple[str, str | None, str | None, str | None]]:
        """Get a list of next games from the DB for given platform.

        Args:
            from_row: Starting row (offset)
            how_much_row: Number of rows to return (limit)
            platform: Platform name to filter by

        Returns:
            List of tuples: (game_name, press_score, average_time_beat,
                           trailer_url)
        """
        sql = self._load_sql("get_next_game_list.sql")
        return self._execute_query(sql, (platform, how_much_row, from_row))

    def count_complete_games(self, platform: str) -> int:
        """Count completed games for given platform.

        Args:
            platform: Platform name to filter by

        Returns:
            Number of completed games
        """
        sql = self._load_sql("count_complete_games.sql")
        results = self._execute_query(sql, (platform,))
        if results and results[0] and results[0][0] is not None:
            return int(results[0][0])
        return 0

    def count_spend_time(
        self, platform: str, mode: int
    ) -> tuple[float | None, float | None]:
        """Count time spent for a platform.

        Args:
            platform: Platform name to filter by
            mode: 0 = only completed games, 1 = all games

        Returns:
            Tuple of (expected_time, real_time) in hours
        """
        if mode == 0:
            sql = self._load_sql("count_spend_time_completed.sql")
        else:
            sql = self._load_sql("count_spend_time.sql")

        results = self._execute_query(sql, (platform,))

        if not results or not results[0]:
            return (None, None)

        row = results[0]
        return (row[0], row[1])

    def get_platforms(self) -> list[str]:
        """Get list of all platforms from the database.

        Returns:
            List of platform names sorted alphabetically

        Raises:
            DatabaseQueryError: If query execution fails
        """
        sql = "SELECT platform_name FROM platform_dictionary " "ORDER BY platform_name"
        logger.debug("Fetching platforms from database")
        results = self._execute_query(sql)
        platforms = [row[0] for row in results if row[0]]
        logger.debug("Found %d platforms", len(platforms))
        return platforms
