"""Formatting helpers for bot messages."""

from __future__ import annotations

from typing import Iterable

from ..constants import DB_DATE_NOT_SET, EXCEL_NONE_VALUE
from ..similarity_search import SimilarityMatch
from ..texts import (
    GAME_HAVE_NEXT_GAME,
    GAME_IN_DB,
    GAME_NEVER_PLAYED,
    GAME_TIME_IS_NONE,
    STEAM_SYNC_ALL_UNIQUE,
)
from ..types import GameInfo, GameListItem
from ..utils import float_to_time


class MessageFormatter:
    """Helper class to format messages sent by the bot."""

    @staticmethod
    def format_game_info(game_row: tuple) -> str:
        """Format detailed information about a single game.

        Args:
            game_row: Tuple with game information from GameRepository

        Returns:
            Formatted string with game details
        """
        (
            game_name,
            status,
            platforms,
            press_score,
            average_time_beat,
            user_score,
            my_score,
            metacritic_url,
            trailer_url,
            my_time_beat,
            last_launch_date,
        ) = game_row

        my_time = (
            str(float_to_time(my_time_beat))
            if my_time_beat and my_time_beat != EXCEL_NONE_VALUE
            else GAME_TIME_IS_NONE
        )
        last_launch = (
            str(last_launch_date)
            if last_launch_date and last_launch_date != DB_DATE_NOT_SET
            else GAME_NEVER_PLAYED
        )

        press_score_str = (
            str(press_score) if press_score else "not specified"
        )
        avg_time_str = (
            float_to_time(str(average_time_beat))
            if average_time_beat
            else "not specified"
        )
        user_score_str = (
            str(user_score) if user_score else "not specified"
        )
        my_score_str = str(my_score) if my_score else "not specified"
        metacritic_str = (
            str(metacritic_url) if metacritic_url else "not specified"
        )
        trailer_str = (
            str(trailer_url) if trailer_url else "not specified"
        )

        return (
            f"Full Game Name\n{str(game_name)}\n"
            f"Status: {str(status)}\n"
            f"Platforms: {str(platforms)}\n"
            f"Press Score: {press_score_str}\n"
            f"Average Playtime: {avg_time_str}\n"
            f"User Score: {user_score_str}\n"
            f"My Score: {my_score_str}\n"
            f"My Playtime: {my_time}\n"
            f"Last Launch Date: {last_launch}\n"
            f"Metacritic Link: {metacritic_str}\n"
            f"Trailer Link: {trailer_str}"
        )

    @staticmethod
    def format_multiple_games(games: list[tuple]) -> str:
        """Format a list of game names when multiple matches found.

        Args:
            games: List of game tuples from game_service.query_game

        Returns:
            Message asking user to specify which game they want.
        """
        game_list_text = "\n".join(f" {row[0]}\n" for row in games)
        return (
            f"Multiple games ({len(games)}), "
            "please specify which one:\n\n"
            f"{game_list_text}\n"
            'If you want this specific game, enter "getgame",'
            " then the exact name and # at the end (no space)"
        )

    @staticmethod
    def format_game_list(games: list[tuple]) -> str:
        """Format a list of games for platform browsing.

        Args:
            games: List of tuples from game_service.get_next_game_list with:
                (game_name, press_score, average_time_beat, trailer_url)

        Returns:
            Formatted string with game list.
        """
        platform_game_list = ""
        for row in games:
            platform_game_list += (
                f"\n\nFull Game Name - {str(row[0])}\n"
                f"Press Score - {str(row[1])}\n"
                f"Average Playtime - {str(row[2])}\n"
                f"Trailer - {str(row[3])}\n"
            )
        return platform_game_list

    @staticmethod
    def format_next_game_message(games: Iterable[GameListItem]) -> str:
        """Format message for next game list by platform.

        Args:
            games: Iterable of GameListItem objects

        Returns:
            Formatted string with game list and hint about next page.
        """
        lines = []
        for game in games:
            lines.append(
                "\n".join(
                    [
                        f"Full Game Name - {game.game_name}",
                        f"Press Score - {game.press_score or 'not specified'}",
                        "\n",
                    ]
                )
            )

        if not lines:
            return "Game list is empty."

        return "".join(lines) + "\n" + GAME_HAVE_NEXT_GAME

    @staticmethod
    def format_completed_games_stats(
        platform_counts: dict[str, int], owner_name: str
    ) -> str:
        """Format completed games statistics by platform.

        Args:
            platform_counts: Dictionary mapping platform names to completed game counts
            owner_name: Name of the database owner

        Returns:
            Formatted string with statistics
        """
        stats_lines = []
        for platform, count in sorted(platform_counts.items()):
            stats_lines.append(f"{platform}: {count}")
        return f"How many games {owner_name} completed:\n" + "\n".join(stats_lines)

    @staticmethod
    def format_time_stats(
        platform_times: dict[str, tuple[float | None, float | None]],
        total_real_seconds: float,
        owner_name: str,
        show_total: bool = True,
    ) -> str:
        """Format time statistics by platform.

        Args:
            platform_times: Dictionary mapping platform names to
                (expected_time, real_time) tuples in hours
            total_real_seconds: Total real time in seconds across all platforms
            owner_name: Name of the database owner
            show_total: Whether to show "Total time spent" line.
                Should be False for single platform views,
                True for overall stats.

        Returns:
            Formatted string with time statistics
        """
        stats_lines = []
        for platform, (expected, real) in sorted(platform_times.items()):
            if expected is not None or real is not None:
                expected_str = (
                    float_to_time(expected) if expected is not None else "not specified"
                )
                real_str = (
                    float_to_time(real) if real is not None else "not specified"
                )
                stats_lines.append(
                    f"{platform}: expected - {expected_str}, real - {real_str}"
                )

        # Only show total line for overall statistics (multiple platforms)
        if show_total:
            total_hours = total_real_seconds / 3600
            total_str = float_to_time(total_hours)
            stats_lines.append(
                f"\nTotal time spent: {total_str}"
            )

        return f"How much time {owner_name} spent on games:\n" + "\n".join(stats_lines)

    @staticmethod
    def format_steam_sync_missing_games(
        matches: list[SimilarityMatch],
    ) -> str:
        """Format message about missing games from Steam API with similarity matches.

        Args:
            matches: List of SimilarityMatch objects

        Returns:
            Formatted string with missing games and their closest matches
        """
        if not matches:
            return ""

        lines = ["Games from Steam not found in database:"]
        has_any_match = False

        for match in matches:
            lines.append(f"\n• original: {match.original}")
            if match.closest_match:
                has_any_match = True
                lines.append(
                    f"  closestMatch: {match.closest_match} "
                    f"(distance: {match.distance}, score: {match.score:.2f})"
                )
            else:
                lines.append("  closestMatch: null")

        if not has_any_match:
            lines.append(f"\n{STEAM_SYNC_ALL_UNIQUE}")

        return "\n".join(lines)
