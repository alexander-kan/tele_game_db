"""Menu-related commands."""

from __future__ import annotations

import logging

import telebot
from telebot.types import Message

from .. import menu, texts
from ..config import SettingsConfig
from ..inline_menu import InlineMenu
from ..security import Security
from .base import Command

logger = logging.getLogger("game_db.bot")


class ClearMenuCommand(Command):
    """Command to clear the reply keyboard menu."""

    @property
    def name(self) -> str:
        return "clear_menu"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute clear menu command."""
        if not message.from_user:
            return
        bot.send_message(
            message.from_user.id,
            texts.MENU_CLEARED,
            reply_markup=menu.BotMenu.clear_menu(),
        )


class MainMenuCommand(Command):
    """Command to show main menu."""

    @property
    def name(self) -> str:
        return "main_menu"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute main menu command."""
        if not message.from_user:
            return
        bot.send_message(
            message.from_user.id,
            texts.MAIN_MENU,
            reply_markup=InlineMenu.main_menu(security, message.from_user.id),
        )


class FileMenuCommand(Command):
    """Command to show file management menu."""

    @property
    def name(self) -> str:
        return "file_menu"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute file menu command."""
        bot.send_message(
            message.chat.id,
            texts.FILE_MENU,
            reply_markup=menu.BotMenu.file_menu(message, security),
        )


class GameListsMenuCommand(Command):
    """Command to show game lists menu."""

    @property
    def name(self) -> str:
        return "game_lists_menu"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute game lists menu command."""
        bot.send_message(
            message.chat.id,
            texts.GAME_LISTS_MENU,
            reply_markup=menu.BotMenu.next_game(message),
        )


class ShowCommandsCommand(Command):
    """Command to show available user commands."""

    @property
    def name(self) -> str:
        return "show_commands"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute show commands command."""
        if not message.from_user:
            return
        bot.send_message(
            message.chat.id,
            texts.USER_COMMANDS_HELP,
            reply_markup=InlineMenu.main_menu(security, message.from_user.id),
        )


class ShowAdminCommandsCommand(Command):
    """Command to show available admin commands."""

    @property
    def name(self) -> str:
        return "show_admin_commands"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute show admin commands command."""
        if not message.from_user:
            return
        if security.admin_check(message.chat.id):
            bot.send_message(
                message.chat.id,
                texts.ADMIN_COMMANDS_HELP,
                reply_markup=InlineMenu.main_menu(security, message.from_user.id),
            )
        else:
            bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
