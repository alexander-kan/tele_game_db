"""Custom exceptions for game_db application."""

from __future__ import annotations


class GameDBError(Exception):
    """Base exception for game_db errors."""


class DatabaseError(GameDBError):
    """Database operation error.

    Raised when database operations fail (connection, query execution, etc.)
    """

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """Initialize database error.

        Args:
            message: Error message
            original_error: Original exception that caused
                this error
        """
        super().__init__(message)
        self.original_error = original_error
        self.message = message


class DatabaseConnectionError(DatabaseError):
    """Database connection error.

    Raised when unable to connect to the database.
    """


class DatabaseQueryError(DatabaseError):
    """Database query execution error.

    Raised when a SQL query fails to execute.
    """

    def __init__(
        self,
        message: str,
        sql: str | None = None,
        params: tuple | None = None,
        original_error: Exception | None = None,
    ) -> None:
        """Initialize database query error.

        Args:
            message: Error message
            sql: SQL query that failed (optional)
            params: Query parameters (optional)
            original_error: Original exception that caused this error
        """
        super().__init__(message, original_error)
        self.sql = sql
        self.params = params


class GameNotFoundError(GameDBError):
    """Game not found in database.

    Raised when a requested game cannot be found.
    """

    def __init__(self, game_name: str) -> None:
        """Initialize game not found error.

        Args:
            game_name: Name of the game that was not found
        """
        super().__init__(f"Game '{game_name}' not found in database")
        self.game_name = game_name


class PlatformNotFoundError(GameDBError):
    """Platform not found in database.

    Raised when a requested platform cannot be found.
    """

    def __init__(self, platform_name: str) -> None:
        """Initialize platform not found error.

        Args:
            platform_name: Name of the platform that was not found
        """
        super().__init__(f"Platform '{platform_name}' not found in database")
        self.platform_name = platform_name


class SQLFileNotFoundError(GameDBError):
    """SQL file not found error.

    Raised when a required SQL file cannot be found or read.
    """

    def __init__(self, sql_file: str) -> None:
        """Initialize SQL file not found error.

        Args:
            sql_file: Path to the SQL file that was not found
        """
        super().__init__(f"SQL file '{sql_file}' not found or cannot be read")
        self.sql_file = sql_file
