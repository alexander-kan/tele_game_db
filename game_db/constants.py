"""Constants for the game_db application."""

from __future__ import annotations

from enum import IntEnum


class ExcelColumn(IntEnum):
    """Excel column indices (1-based) for game data.

    These constants represent the column positions in Excel files
    used for importing game data.
    """

    GAME_NAME = 1
    PLATFORMS = 2
    STATUS = 3
    RELEASE_DATE = 4
    PRESS_SCORE = 5
    USER_SCORE = 6
    MY_SCORE = 7
    METACRITIC_URL = 8
    AVERAGE_TIME_BEAT = 9
    TRAILER_URL = 10
    MY_TIME_BEAT = 11
    LAST_LAUNCH_DATE = 12
    ADDITIONAL_TIME = 13


class ExcelRowIndex(IntEnum):
    """Row indices (0-based) for accessing game data in lists.

    These constants represent the index positions when accessing
    game data from Excel rows as Python lists (0-based indexing).
    """

    GAME_NAME = 0
    PLATFORMS = 1
    STATUS = 2
    RELEASE_DATE = 3
    PRESS_SCORE = 4
    USER_SCORE = 5
    MY_SCORE = 6
    METACRITIC_URL = 7
    AVERAGE_TIME_BEAT = 8
    TRAILER_URL = 9
    MY_TIME_BEAT = 10
    LAST_LAUNCH_DATE = 11
    ADDITIONAL_TIME = 12


# Domain-level sentinel values used in Excel and database.
#
# These values are persisted in Excel files and in the SQLite database and
# therefore MUST NOT be changed without providing a migration for existing
# data and updating all related tests.

# Text value written to Excel to indicate that numeric value (time, score, etc.)
# is intentionally absent.
EXCEL_NONE_VALUE = "none"

# Human‑readable Excel date that means "no date set".
EXCEL_DATE_NOT_SET = "December 12, 4712"

# Database date string that represents "no date set" in games table.
DB_DATE_NOT_SET = "4712-12-12"
