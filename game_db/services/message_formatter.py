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
            str(press_score) if press_score else "не указано"
        )
        avg_time_str = (
            float_to_time(str(average_time_beat))
            if average_time_beat
            else "не указано"
        )
        user_score_str = (
            str(user_score) if user_score else "не указано"
        )
        my_score_str = str(my_score) if my_score else "не указано"
        metacritic_str = (
            str(metacritic_url) if metacritic_url else "не указано"
        )
        trailer_str = (
            str(trailer_url) if trailer_url else "не указано"
        )

        return (
            f"Полное название игры \n{str(game_name)}\n"
            f"Статус прохождения: {str(status)}\n"
            f"Платформы: {str(platforms)}\n"
            f"Оценка игры прессой: {press_score_str}\n"
            f"Среднее время прохождения: {avg_time_str}\n"
            f"Оценка пользователей: {user_score_str}\n"
            f"Моя оценка: {my_score_str}\n"
            f"Моё время в игре: {my_time}\n"
            f"Дата последнего запуска: {last_launch}\n"
            f"Ссылка на Metacritic: {metacritic_str}\n"
            f"Ссылка на трейлер: {trailer_str}"
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
            f"Много игр ({len(games)}), "
            "уточни какая интересна:\n\n"
            f"{game_list_text}\n"
            'Если интересна именно эта игра, введи "getgame",'
            " затем точное название и знак # в конце (без пробела)"
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
                f"\n\nПолное название игры - {str(row[0])}\n"
                f"Оценка игры прессой - {str(row[1])}\n"
                f"Среднее время прохождения - {str(row[2])}\n"
                f"Трейлер - {str(row[3])}\n"
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
                        f"Полное название игры - {game.game_name}",
                        f"Оценка игры прессой - {game.press_score or 'не указано'}",
                        "\n",
                    ]
                )
            )

        if not lines:
            return "Список игр пуст."

        return "".join(lines) + "\n" + GAME_HAVE_NEXT_GAME

    @staticmethod
    def format_completed_games_stats(platform_counts: dict[str, int]) -> str:
        """Format completed games statistics by platform.

        Args:
            platform_counts: Dictionary mapping platform names to completed game counts

        Returns:
            Formatted string with statistics
        """
        stats_lines = []
        for platform, count in sorted(platform_counts.items()):
            stats_lines.append(f"{platform}: {count}")
        return "Сколько игр прошёл Александр:\n" + "\n".join(stats_lines)

    @staticmethod
    def format_time_stats(
        platform_times: dict[str, tuple[float | None, float | None]],
        total_real_seconds: float,
        show_total: bool = True,
    ) -> str:
        """Format time statistics by platform.

        Args:
            platform_times: Dictionary mapping platform names to
                (expected_time, real_time) tuples in hours
            total_real_seconds: Total real time in seconds across all platforms
            show_total: Whether to show "Всего времени потрачено" line.
                Should be False for single platform views,
                True for overall stats.

        Returns:
            Formatted string with time statistics
        """
        stats_lines = []
        for platform, (expected, real) in sorted(platform_times.items()):
            if expected is not None or real is not None:
                expected_str = (
                    float_to_time(expected) if expected is not None else "не указано"
                )
                real_str = (
                    float_to_time(real) if real is not None else "не указано"
                )
                stats_lines.append(
                    f"{platform}: ожидаемое - {expected_str}, реальное - {real_str}"
                )

        # Only show total line for overall statistics (multiple platforms)
        if show_total:
            total_hours = total_real_seconds / 3600
            total_str = float_to_time(total_hours)
            stats_lines.append(
                f"\nВсего времени потрачено: {total_str}"
            )

        return "Сколько времени Александр потратил на игры:\n" + "\n".join(stats_lines)

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

        lines = ["Игры из Steam, которых нет в базе:"]
        has_any_match = False

        for match in matches:
            lines.append(f"\n• original: {match.original}")
            if match.closest_match:
                has_any_match = True
                lines.append(
                    f"  closestMatch: {match.closest_match} "
                    f"(расстояние: {match.distance}, скор: {match.score:.2f})"
                )
            else:
                lines.append("  closestMatch: null")

        if not has_any_match:
            lines.append(f"\n{STEAM_SYNC_ALL_UNIQUE}")

        return "\n".join(lines)
