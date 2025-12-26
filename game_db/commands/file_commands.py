"""File management commands."""

from __future__ import annotations

import logging

import telebot
from telebot.types import Message

from .. import menu, texts
from ..config import SettingsConfig
from ..security import Security
from ..utils import (
    is_file_type_allowed,
    is_path_safe,
    safe_delete_file,
    validate_file_name,
)
from .base import Command

logger = logging.getLogger("game_db.bot")


class RemoveFileCommand(Command):
    """Command to safely remove a file."""

    @property
    def name(self) -> str:
        return "remove_file"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute remove file command."""
        if not security.admin_check(message.chat.id):
            bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
            return

        if not message.text:
            return
        file_name = message.text.replace("removefile ", "").strip()

        if not validate_file_name(file_name):
            logger.warning(
                "Invalid file name provided by user %s: %s",
                message.chat.id,
                file_name,
            )
            bot.send_message(
                message.chat.id,
                "Invalid file name",
                reply_markup=menu.BotMenu.file_menu(message, security),
            )
            return

        target_path = settings.paths.files_dir / file_name

        if safe_delete_file(target_path, settings.paths.files_dir):
            bot.send_message(
                message.chat.id,
                texts.FILE_DELETED,
                reply_markup=menu.BotMenu.file_menu(message, security),
            )
        else:
            logger.warning(
                "Failed to delete file: %s (requested by user %s)",
                target_path,
                message.chat.id,
            )
            bot.send_message(
                message.chat.id,
                "Failed to delete file",
                reply_markup=menu.BotMenu.file_menu(message, security),
            )


class GetFileCommand(Command):
    """Command to safely retrieve a file."""

    @property
    def name(self) -> str:
        return "get_file"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute get file command."""
        if not security.admin_check(message.chat.id):
            bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
            return

        if not message.text:
            return
        file_name = message.text.replace("getfile ", "").strip()

        if not validate_file_name(file_name):
            logger.warning(
                "Invalid file name provided by user %s: %s",
                message.chat.id,
                file_name,
            )
            bot.send_message(
                message.chat.id,
                "Invalid file name",
                reply_markup=menu.BotMenu.file_menu(message, security),
            )
            return

        target_path = settings.paths.files_dir / file_name

        if not is_path_safe(target_path, settings.paths.files_dir):
            logger.warning(
                "Path traversal attempt detected from user %s: %s",
                message.chat.id,
                file_name,
            )
            bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
            return

        if target_path.is_file():
            try:
                with open(target_path, "rb") as file_obj:
                    bot.send_document(message.chat.id, file_obj)
            except OSError as e:
                logger.error(
                    "Failed to read file %s: %s",
                    target_path,
                    str(e),
                    exc_info=True,
                )
                bot.send_message(
                    message.chat.id,
                    "Error reading file",
                    reply_markup=menu.BotMenu.file_menu(message, security),
                )
        else:
            bot.send_message(message.chat.id, texts.FILE_NOT_FOUND)


class SyncSteamCommand(Command):
    """Command to synchronize games with Steam."""

    @property
    def name(self) -> str:
        return "sync_steam"

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute Steam synchronization command."""
        if not security.admin_check(message.chat.id):
            bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
            return

        from .. import db as db_module

        backup_excel = settings.paths.games_excel_file
        update_excel = settings.paths.update_db_dir / "games.xlsx"

        try:
            if not backup_excel.exists():
                bot.send_message(
                    message.chat.id, texts.STEAM_SYNC_FILE_NOT_FOUND
                )
                return

            # Copy current backup Excel to update_db
            update_excel.parent.mkdir(parents=True, exist_ok=True)
            with backup_excel.open("rb") as src, update_excel.open("wb") as dst:
                dst.write(src.read())

            create = db_module.ChangeDB()
            success, _ = create.synchronize_steam_games(str(update_excel))
            if success:
                # Replace original backup with updated version
                backup_excel.write_bytes(update_excel.read_bytes())
                bot.send_message(message.chat.id, texts.STEAM_SYNC_SUCCESS)
            else:
                bot.send_message(message.chat.id, texts.STEAM_SYNC_ERROR)
        except OSError:
            logger.exception("Filesystem error during Steam sync")
            bot.send_message(
                message.chat.id, texts.STEAM_SYNC_FILESYSTEM_ERROR
            )
