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
                allowed values (e.g., {"STATUS": {"pass": "Completed"}})
        """
        self.values_dictionaries = values_dictionaries

    def validate_status(self, status_text: str) -> bool:
        """Validate status text against allowed values.

        Args:
            status_text: Status text to validate

        Returns:
            True if valid, False otherwise
        """
        # Dynamically get all status values from config
        allowed_statuses = list(self.values_dictionaries["STATUS"].values())
        return status_text in allowed_statuses

    def validate_platform(self, platform_text: str) -> bool:
        """Validate platform name against allowed values.

        Args:
            platform_text: Platform name to validate

        Returns:
            True if valid, False otherwise
        """
        # Dynamically get all platform values from config
        allowed_platforms = list(self.values_dictionaries["PLATFORM"].values())
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
            # Dynamically build list of allowed statuses for error message
            allowed_statuses = ", ".join(self.values_dictionaries["STATUS"].values())
            errors.append(
                f"Invalid status: {game_row.status}. "
                f"Must be one of: {allowed_statuses}"
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

        Platform IDs are assigned based on the order in values_dictionaries.ini:
        - ID 1 = not_defined (reserved, returns 1 for unknown)
        - ID 2+ = platforms in order of appearance in config

        Args:
            platform_text: Platform name

        Returns:
            Platform ID (2=first platform after not_defined, 3=second, etc., 1=unknown)
        """
        # Build platform map dynamically based on order in config
        # Skip "not_defined" as it's ID 1 (reserved for unknown)
        platform_map: dict[str, int] = {}
        platform_items = list(self.values_dictionaries["PLATFORM"].items())
        
        for idx, (key, value) in enumerate(platform_items):
            # ID starts from 2 (1 is reserved for "not_defined"/unknown)
            platform_map[value] = idx + 1
        
        return platform_map.get(platform_text.strip(), 1)
