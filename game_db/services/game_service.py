"""Game-related domain logic: search, lists, statistics."""

from __future__ import annotations

import logging

from ..config import load_settings_config
from ..exceptions import DatabaseError, GameDBError
from ..repositories.game_repository import GameRepository

logger = logging.getLogger("game_db.services")

# Load settings explicitly and pass db_path to repository
# This is better than relying on GameRepository's default behavior
_settings = load_settings_config()
_repository = GameRepository(_settings.paths.sqlite_db_file)


def query_game(game_name: str) -> list[tuple]:
    """Query game info by name from the database.

    Args:
        game_name: Game name or search term

    Returns:
        List of tuples with game information

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        return _repository.query_game(game_name)
    except GameDBError:
        # Re-raise domain exceptions as-is (DatabaseError, SQLFileNotFoundError, etc.)
        raise
    except Exception as e:
        # Catch-all for truly unexpected errors (should not happen in normal operation)
        # Wrap in domain exception and log technical details
        logger.error(
            "Unexpected error querying game '%s'",
            game_name,
            exc_info=True,
        )
        raise DatabaseError(f"Unexpected error querying game: {str(e)}") from e


def get_next_game_list(
    from_row: int, how_much_row: int, platform: str
) -> list[tuple[str, str | None, str | None, str | None]]:
    """Get a list of next games from the DB for given platform.

    Args:
        from_row: Starting row (offset)
        how_much_row: Number of rows to return (limit)
        platform: Platform name to filter by

    Returns:
        List of tuples with game information

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        return _repository.get_next_game_list(from_row, how_much_row, platform)
    except GameDBError:
        # Re-raise domain exceptions as-is
        raise
    except Exception as e:
        # Catch-all for truly unexpected errors
        logger.error(
            "Unexpected error getting game list for platform '%s'",
            platform,
            exc_info=True,
        )
        raise DatabaseError(f"Unexpected error getting game list: {str(e)}") from e


def count_complete_games(platform: str) -> int:
    """Count completed games for given platform.

    Args:
        platform: Platform name to filter by

    Returns:
        Number of completed games (0 if error occurs)

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        return _repository.count_complete_games(platform)
    except GameDBError:
        # Re-raise domain exceptions as-is
        raise
    except Exception as e:
        # Catch-all for truly unexpected errors
        logger.error(
            "Unexpected error counting complete games for platform '%s'",
            platform,
            exc_info=True,
        )
        raise DatabaseError(f"Unexpected error counting games: {str(e)}") from e


def count_spend_time(platform: str, mode: int) -> tuple[float | None, float | None]:
    """Count time spent for a platform, optionally only for completed games.

    Args:
        platform: Platform name to filter by
        mode: 0 = only completed games, 1 = all games

    Returns:
        Tuple of (expected_time, real_time) in hours

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        return _repository.count_spend_time(platform, mode)
    except GameDBError:
        # Re-raise domain exceptions as-is
        raise
    except Exception as e:
        # Catch-all for truly unexpected errors
        logger.error(
            "Unexpected error counting time for platform '%s' (mode: %d)",
            platform,
            mode,
            exc_info=True,
        )
        raise DatabaseError(f"Unexpected error counting time: {str(e)}") from e


def get_platforms() -> list[str]:
    """Get list of all platforms from the database.

    Returns:
        List of platform names sorted alphabetically

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        return _repository.get_platforms()
    except GameDBError:
        # Re-raise domain exceptions as-is
        raise
    except Exception as e:
        # Catch-all for truly unexpected errors
        logger.error(
            "Unexpected error getting platforms",
            exc_info=True,
        )
        raise DatabaseError(f"Unexpected error getting platforms: {str(e)}") from e
