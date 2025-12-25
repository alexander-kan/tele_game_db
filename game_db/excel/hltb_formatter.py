"""Excel formatting for HowLongToBeat synchronization.

This module provides functionality to update Excel cells with
HowLongToBeat game data, specifically average time to beat.
"""

from __future__ import annotations

import logging

from openpyxl.worksheet.worksheet import Worksheet

from ..constants import ExcelColumn

logger = logging.getLogger("game_db.excel.hltb")


class HowLongToBeatExcelFormatter:
    """Format Excel cells with HowLongToBeat game data."""

    @staticmethod
    def format_time(time_hours: float | None) -> str | None:
        """Format time value for Excel.

        Args:
            time_hours: Time in hours from HowLongToBeat

        Returns:
            Formatted time string (hours as float) or None
        """
        if time_hours is None:
            return None

        try:
            time_float = float(time_hours)
            if time_float <= 0:
                return None
            return str(time_float)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def update_game_row(
        sheet: Worksheet,
        row_number: int,
        hltb_data: dict,
    ) -> None:
        """Update Excel row with HowLongToBeat game data.

        Updates AVERAGE_TIME_BEAT column.

        Args:
            sheet: Excel worksheet to update
            row_number: Row number (1-based) to update
            hltb_data: Dictionary with HowLongToBeat data
        """
        # Update average time to beat
        # Use main_story if available, otherwise use completionist
        time_hours = hltb_data.get("main_story") or hltb_data.get(
            "completionist"
        ) or hltb_data.get("main_extra") or hltb_data.get("all_styles")

        formatted_time = HowLongToBeatExcelFormatter.format_time(time_hours)
        if formatted_time is not None:
            sheet.cell(
                row=row_number, column=ExcelColumn.AVERAGE_TIME_BEAT
            ).value = formatted_time
            logger.debug(
                "Updated AVERAGE_TIME_BEAT for row %d: %s hours",
                row_number,
                formatted_time,
            )
