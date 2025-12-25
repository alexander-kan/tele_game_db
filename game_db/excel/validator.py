"""Excel data validation functionality."""

from __future__ import annotations

import logging

from .models import GameRow

logger = logging.getLogger("game_db.excel")


class ExcelValidator:
    """Validate game data from Excel files."""

    def __init__(
        self,
        values_dictionaries: dict[str, dict[str, str]],
    ) -> None:
        """Initialize validator with configuration.

        Args:
            values_dictionaries: Dictionary mapping field names to
                allowed values (e.g., {"STATUS": {"pass": "Пройдена"}})
        """
        self.values_dictionaries = values_dictionaries

    def validate_status(self, status_text: str) -> bool:
        """Validate status text against allowed values.

        Args:
            status_text: Status text to validate

        Returns:
            True if valid, False otherwise
        """
        allowed_statuses = [
            self.values_dictionaries["STATUS"]["pass"],
            self.values_dictionaries["STATUS"]["not_started"],
            self.values_dictionaries["STATUS"]["abandoned"],
        ]
        return status_text in allowed_statuses

    def validate_platform(self, platform_text: str) -> bool:
        """Validate platform name against allowed values.

        Args:
            platform_text: Platform name to validate

        Returns:
            True if valid, False otherwise
        """
        allowed_platforms = [
            self.values_dictionaries["PLATFORM"]["steam"],
            self.values_dictionaries["PLATFORM"]["switch"],
            self.values_dictionaries["PLATFORM"]["ps4"],
            self.values_dictionaries["PLATFORM"]["ps_vita"],
            self.values_dictionaries["PLATFORM"]["pc_origin"],
            self.values_dictionaries["PLATFORM"]["pc_gog"],
            self.values_dictionaries["PLATFORM"]["ps5"],
            self.values_dictionaries["PLATFORM"]["n3ds"],
        ]
        return platform_text.strip() in allowed_platforms

    def validate_game_row(self, game_row: GameRow) -> tuple[bool, list[str]]:
        """Validate a complete game row.

        Args:
            game_row: GameRow instance to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: list[str] = []

        # Validate required fields
        if not game_row.game_name or not game_row.game_name.strip():
            errors.append("Game name is required")

        if not game_row.status:
            errors.append("Status is required")
        elif not self.validate_status(game_row.status):
            errors.append(
                f"Invalid status: {game_row.status}. "
                f"Must be one of: Пройдена, Не начата, Брошена"
            )

        if not game_row.platforms:
            errors.append("At least one platform is required")
        else:
            # Validate each platform
            for platform in game_row.platforms.split(","):
                if not self.validate_platform(platform.strip()):
                    errors.append(f"Invalid platform: {platform.strip()}")

        # Validate date format (basic check)
        if game_row.release_date:
            if "," not in game_row.release_date:
                errors.append(
                    f"Invalid release date format: {game_row.release_date}. "
                    f"Expected: 'Month DD, YYYY'"
                )

        return len(errors) == 0, errors

    def get_status_id(self, status_text: str) -> int:
        """Map status text to dictionary ID.

        Args:
            status_text: Status text

        Returns:
            Status ID (1=pass, 2=not_started, 3=abandoned, 0=unknown)
        """
        if status_text == self.values_dictionaries["STATUS"]["pass"]:
            return 1
        elif status_text == self.values_dictionaries["STATUS"]["not_started"]:
            return 2
        elif status_text == self.values_dictionaries["STATUS"]["abandoned"]:
            return 3
        else:
            logger.warning("Unknown status: %s", status_text)
            return 0

    def get_platform_id(self, platform_text: str) -> int:
        """Map platform name to dictionary ID.

        Args:
            platform_text: Platform name

        Returns:
            Platform ID (2=Steam, 3=Switch, etc., 1=unknown)
        """
        platform_map = {
            self.values_dictionaries["PLATFORM"]["steam"]: 2,
            self.values_dictionaries["PLATFORM"]["switch"]: 3,
            self.values_dictionaries["PLATFORM"]["ps4"]: 4,
            self.values_dictionaries["PLATFORM"]["ps_vita"]: 5,
            self.values_dictionaries["PLATFORM"]["pc_origin"]: 6,
            self.values_dictionaries["PLATFORM"]["pc_gog"]: 7,
            self.values_dictionaries["PLATFORM"]["ps5"]: 8,
            self.values_dictionaries["PLATFORM"]["n3ds"]: 9,
        }
        return platform_map.get(platform_text.strip(), 1)
