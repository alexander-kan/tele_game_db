"""Game-related commands."""

from __future__ import annotations

import logging

import telebot
from telebot.types import Message

from .. import menu, texts
from ..config import DEFAULT_PLATFORMS, SettingsConfig
from ..exceptions import DatabaseError, GameDBError
from ..inline_menu import InlineMenu
from ..security import Security
from ..services import game_service
from ..services.message_formatter import MessageFormatter
from .base import Command

logger = logging.getLogger("game_db.bot")


def _get_platforms() -> list[str]:
    """Get list of platforms from database with fallback to default."""
    try:
        platforms = game_service.get_platforms()
        return platforms if platforms else DEFAULT_PLATFORMS
    except DatabaseError as e:
        # Domain exception from service layer - log and use defaults
        logger.warning(
            "Failed to load platforms from database: %s, using defaults",
            str(e),
            exc_info=True,
        )
        return DEFAULT_PLATFORMS
    except GameDBError as e:
        # Other domain exceptions (e.g., SQLFileNotFoundError) - log and use defaults
        logger.warning(
            "Failed to load platforms: %s, using defaults",
            str(e),
            exc_info=True,
        )
        return DEFAULT_PLATFORMS


class GetGameCommand(Command):
    """Command to search and display game information."""

    @property
    def name(self) -> str:
        return "get_game"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute get game command."""
        if not message.text:
            return
        if not message.from_user:
            return

        try:
            get_from_db = game_service.query_game(message.text)
        except DatabaseError as e:
            logger.error(
                "Database error querying game '%s': %s",
                message.text,
                str(e),
                exc_info=True,
            )
            bot.send_message(
                message.from_user.id,
                texts.GAME_QUERY_ERROR,
                reply_markup=menu.BotMenu.main_menu(message, security),
            )
            return

        formatter = MessageFormatter()

        if len(get_from_db) > 1 and message.text[-1] != "#":
            game_db = formatter.format_multiple_games(get_from_db)
        elif message.text[-1] == "#":
            name = message.text.replace("getgame ", "").replace("#", "")
            game_db = texts.GAME_QUERY_ERROR
            for row in get_from_db:
                if row[0].lower() == name.lower():
                    game_db = formatter.format_game_info(row)
                    break
        elif len(get_from_db) < 1:
            game_db = texts.GAME_NOT_FOUND
        else:
            game_db = formatter.format_game_info(get_from_db[0])

        bot.send_message(
            message.from_user.id,
            game_db,
            reply_markup=InlineMenu.main_menu(security, message.from_user.id),
        )


class SteamGameListCommand(Command):
    """Command to show Steam game list."""

    @property
    def name(self) -> str:
        return "steam_game_list"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute Steam game list command."""
        if not message.from_user:
            return
        from ..handlers import game_list

        next_list = game_list(message, "Steam")
        bot.send_message(
            message.from_user.id,
            next_list[1],
            reply_markup=menu.BotMenu.next_game(next_list[0]),
        )


class SwitchGameListCommand(Command):
    """Command to show Switch game list."""

    @property
    def name(self) -> str:
        return "switch_game_list"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute Switch game list command."""
        if not message.from_user:
            return
        from ..handlers import game_list

        next_list = game_list(message, "Switch")
        bot.send_message(
            message.from_user.id,
            next_list[1],
            reply_markup=menu.BotMenu.next_game(next_list[0]),
        )


class CountGamesCommand(Command):
    """Command to count completed games by platform."""

    @property
    def name(self) -> str:
        return "count_games"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute count games command."""
        if not message.from_user:
            return
        platforms = _get_platforms()
        platform_counts = {}
        for platform in platforms:
            try:
                platform_counts[platform] = game_service.count_complete_games(
                    platform
                )
            except DatabaseError as e:
                logger.error(
                    "Database error counting games for platform '%s': %s",
                    platform,
                    str(e),
                    exc_info=True,
                )
                platform_counts[platform] = 0

        formatter = MessageFormatter()
        count_complete_text = formatter.format_completed_games_stats(
            platform_counts
        )
        bot.send_message(
            message.from_user.id,
            count_complete_text,
            reply_markup=menu.BotMenu.next_game(message),
        )


class CountTimeCommand(Command):
    """Command to count time spent on games by platform."""

    @property
    def name(self) -> str:
        return "count_time"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute count time command."""
        if not message.from_user:
            return
        platforms = _get_platforms()
        # Collect time data for completed games
        platform_times = {}
        for platform in platforms:
            try:
                expected, real = game_service.count_spend_time(platform, 0)
                platform_times[platform] = (expected, real)
            except DatabaseError as e:
                logger.error(
                    "Database error counting time for platform '%s': %s",
                    platform,
                    str(e),
                    exc_info=True,
                )
                platform_times[platform] = (None, None)

        # Calculate total real time by summing real_time from all platforms
        # real_time is in hours, so we convert to seconds for format_time_stats
        total_real_hours = 0.0
        for platform, (expected, real) in platform_times.items():
            if real is not None:
                total_real_hours += real

        # Convert hours to seconds for format_time_stats
        total_real_seconds = total_real_hours * 3600

        formatter = MessageFormatter()
        # For overall statistics, show total line
        count_complete_text = formatter.format_time_stats(
            platform_times, total_real_seconds, show_total=True
        )

        bot.send_message(
            message.from_user.id,
            count_complete_text,
            reply_markup=menu.BotMenu.next_game(message),
        )
