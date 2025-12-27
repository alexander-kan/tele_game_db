"""HowLongToBeat.com client wrapper.

This module provides functionality to fetch game completion time data
from HowLongToBeat.com using the howlongtobeatpy library.
"""

from __future__ import annotations

import logging

try:
    from howlongtobeatpy import HowLongToBeat  # type: ignore[import-untyped]
except ImportError:
    HowLongToBeat = None  # type: ignore[assignment]

logger = logging.getLogger("game_db.hltb")


class HowLongToBeatClient:
    """Client for fetching game data from HowLongToBeat.com."""

    def __init__(self) -> None:
        """Initialize HowLongToBeat client."""
        if HowLongToBeat is None:
            raise ImportError(
                "howlongtobeatpy library is not installed. "
                "Install it with: poetry add howlongtobeatpy"
            )
        self.client = HowLongToBeat()

    def search_game(self, game_name: str) -> dict | None:
        """Search for game on HowLongToBeat and return best match data.

        Args:
            game_name: Name of the game to search for

        Returns:
            Dictionary with game data (main_story, completionist, etc.)
            or None if not found
        """
        try:
            results = self.client.search(game_name)
            if not results:
                logger.warning("No HowLongToBeat results found for game: %s", game_name)
                return None

            # Get best match by similarity
            best_match = max(results, key=lambda x: x.similarity)

            # Extract time data
            hltb_data = {
                "game_name": best_match.game_name,
                "game_id": best_match.game_id,
                "main_story": best_match.main_story,
                "main_extra": best_match.main_extra,
                "completionist": best_match.completionist,
                "all_styles": best_match.all_styles,
                "similarity": best_match.similarity,
            }

            logger.debug(
                "Found HowLongToBeat data for '%s': main_story=%.1f hours",
                game_name,
                best_match.main_story or 0.0,
            )

            return hltb_data
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Error searching HowLongToBeat for game '%s': %s",
                game_name,
                str(e),
            )
            return None
