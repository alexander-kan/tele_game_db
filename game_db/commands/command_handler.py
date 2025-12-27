"""Command handler for registering and executing commands."""

from __future__ import annotations

import logging

import telebot
from telebot.types import Message

from ..config import SettingsConfig
from ..security import Security
from .base import Command

logger = logging.getLogger("game_db.bot")


class CommandHandler:
    """Handler for registering and executing bot commands.

    This class manages command registration and routing based on
    message text patterns.
    """

    def __init__(self) -> None:
        """Initialize command handler."""
        self._exact_commands: dict[str, Command] = {}
        self._prefix_commands: list[tuple[str, Command]] = []
        self._substring_commands: list[tuple[str, Command]] = []

    def register_exact(self, trigger: str, command: Command) -> None:
        """Register command for exact text match.

        Args:
            trigger: Exact text that triggers the command
            command: Command instance to execute
        """
        self._exact_commands[trigger] = command
        logger.debug("Registered exact command: %s -> %s", trigger, command.name)

    def register_prefix(self, prefix: str, command: Command) -> None:
        """Register command for prefix match.

        Args:
            prefix: Text prefix that triggers the command
            command: Command instance to execute
        """
        self._prefix_commands.append((prefix, command))
        logger.debug("Registered prefix command: %s -> %s", prefix, command.name)

    def register_substring(self, substring: str, command: Command) -> None:
        """Register command for substring match.

        Args:
            substring: Text substring that triggers the command
            command: Command instance to execute
        """
        self._substring_commands.append((substring, command))
        logger.debug(
            "Registered substring command: %s -> %s",
            substring,
            command.name,
        )

    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> bool:
        """Execute command based on message text.

        Args:
            message: Telegram message
            bot: Telegram bot instance
            security: Security instance
            settings: Settings configuration

        Returns:
            True if a command was executed, False otherwise
        """
        text = message.text or ""

        # Check exact matches first
        if text in self._exact_commands:
            command = self._exact_commands[text]
            logger.debug("Executing exact command: %s", command.name)
            command.execute(message, bot, security, settings)
            return True

        # Check prefix matches
        for prefix, command in self._prefix_commands:
            if prefix in text:
                logger.debug("Executing prefix command: %s", command.name)
                command.execute(message, bot, security, settings)
                return True

        # Check substring matches
        for substring, command in self._substring_commands:
            if substring in text:
                logger.debug("Executing substring command: %s", command.name)
                command.execute(message, bot, security, settings)
                return True

        return False
