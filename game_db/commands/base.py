"""Base command class for Command Pattern implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod

import telebot
from telebot.types import Message

from ..config import SettingsConfig
from ..security import Security


class Command(ABC):
    """Base class for all bot commands.

    Each command encapsulates a specific action that can be executed
    in response to a user message.
    """

    @abstractmethod
    def execute(
        self,
        message: Message,
        bot: telebot.TeleBot,
        security: Security,
        settings: SettingsConfig,
    ) -> None:
        """Execute the command.

        Args:
            message: Telegram message that triggered the command
            bot: Telegram bot instance
            security: Security instance for authorization checks
            settings: Application settings configuration
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return command name for identification."""
        pass
