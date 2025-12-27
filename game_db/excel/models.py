"""Data models for Excel game rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class GameRow:
    """Represents a single game row from Excel file.

    This dataclass provides a structured representation of game data
    read from Excel files, replacing the previous list-based approach.
    """

    game_name: str
    platforms: str  # Comma-separated platform names
    status: str  # "Completed", "Not Started", "Dropped"
    release_date: str  # "Month DD, YYYY" format
    press_score: Optional[str] = None
    user_score: Optional[str] = None
    my_score: Optional[str] = None
    metacritic_url: Optional[str] = None
    average_time_beat: Optional[str] = None  # Hours as float string
    trailer_url: Optional[str] = None
    my_time_beat: Optional[str] = None  # Hours as float string
    last_launch_date: Optional[str] = None  # "Month DD, YYYY" format
    additional_time: Optional[str] = None  # Hours as float string

    @classmethod
    def from_list(cls, row: list) -> GameRow:
        """Create GameRow from list (backward compatibility).

        Args:
            row: List of cell values from Excel row

        Returns:
            GameRow instance
        """
        from ..constants import ExcelRowIndex

        return cls(
            game_name=(
                row[ExcelRowIndex.GAME_NAME]
                if len(row) > ExcelRowIndex.GAME_NAME
                else ""
            ),
            platforms=(
                row[ExcelRowIndex.PLATFORMS]
                if len(row) > ExcelRowIndex.PLATFORMS
                else ""
            ),
            status=row[ExcelRowIndex.STATUS] if len(row) > ExcelRowIndex.STATUS else "",
            release_date=(
                row[ExcelRowIndex.RELEASE_DATE]
                if len(row) > ExcelRowIndex.RELEASE_DATE
                else ""
            ),
            press_score=(
                row[ExcelRowIndex.PRESS_SCORE]
                if len(row) > ExcelRowIndex.PRESS_SCORE
                else None
            ),
            user_score=(
                row[ExcelRowIndex.USER_SCORE]
                if len(row) > ExcelRowIndex.USER_SCORE
                else None
            ),
            my_score=(
                row[ExcelRowIndex.MY_SCORE]
                if len(row) > ExcelRowIndex.MY_SCORE
                else None
            ),
            metacritic_url=(
                row[ExcelRowIndex.METACRITIC_URL]
                if len(row) > ExcelRowIndex.METACRITIC_URL
                else None
            ),
            average_time_beat=(
                row[ExcelRowIndex.AVERAGE_TIME_BEAT]
                if len(row) > ExcelRowIndex.AVERAGE_TIME_BEAT
                else None
            ),
            trailer_url=(
                row[ExcelRowIndex.TRAILER_URL]
                if len(row) > ExcelRowIndex.TRAILER_URL
                else None
            ),
            my_time_beat=(
                row[ExcelRowIndex.MY_TIME_BEAT]
                if len(row) > ExcelRowIndex.MY_TIME_BEAT
                else None
            ),
            last_launch_date=(
                row[ExcelRowIndex.LAST_LAUNCH_DATE]
                if len(row) > ExcelRowIndex.LAST_LAUNCH_DATE
                else None
            ),
            additional_time=(
                row[ExcelRowIndex.ADDITIONAL_TIME]
                if len(row) > ExcelRowIndex.ADDITIONAL_TIME
                else None
            ),
        )

    def to_list(self) -> list:
        """Convert GameRow to list format (backward compatibility).

        Returns:
            List of values matching Excel row structure
        """
        return [
            self.game_name,
            self.platforms,
            self.status,
            self.release_date,
            self.press_score,
            self.user_score,
            self.my_score,
            self.metacritic_url,
            self.average_time_beat,
            self.trailer_url,
            self.my_time_beat,
            self.last_launch_date,
            self.additional_time,
        ]
