"""Telegram bot entrypoint and handlers for the personal game database."""

from __future__ import annotations

import logging
from time import sleep

import telebot
from telebot.types import Message

from . import handlers
from .callback_handlers import handle_callback_query
from .config import (
    SettingsConfig,
    TokensConfig,
    UsersConfig,
    load_settings_config,
    load_tokens_config,
    load_users_config,
)
from .logging_config import configure_logging
from .security import Security
from .utils import clean_directory_safely

logger = logging.getLogger("game_db.bot")
telebot.telebot.logger.setLevel(logging.INFO)


class BotApplication:
    """Main application class managing bot lifecycle and dependencies."""

    def __init__(
        self,
        settings: SettingsConfig,
        tokens: TokensConfig,
        users: UsersConfig,
    ) -> None:
        """Initialize bot application with dependencies."""
        self.settings = settings
        self.tokens = tokens
        self.users = users
        self.bot = telebot.TeleBot(tokens.telegram_token, threaded=False)
        self.security = Security(users)

    def sendall(self, text: str) -> None:
        """Send a broadcast message to all users from the config."""
        if len(self.users.users) > 0:
            for user in self.users.users:
                try:
                    self.bot.send_message(user, text)
                except OSError:
                    logger.exception(
                        "Error sending message '%s' to user %s",
                        text,
                        user,
                    )

    def setup_handlers(self) -> None:
        """Register all message handlers with the bot."""

        @self.bot.message_handler(commands=["start", "help"])
        def handle_start_help(message: Message) -> None:
            """Handle /start and /help commands."""
            handlers.handle_start_help(message, self.bot, self.security)

        @self.bot.message_handler(content_types=["text"])
        def handle_text(message: Message) -> None:
            """Delegate text handling to handlers module."""
            handlers.handle_text(message, self.bot, self.security, self.settings)

        @self.bot.message_handler(
            content_types=["document", "photo", "audio", "video", "voice"]
        )
        def addfile(message: Message) -> None:
            """Handle file uploads from admin users."""
            handlers.handle_file_upload(message, self.bot, self.security, self.settings)

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call) -> None:
            """Handle inline keyboard callback queries."""
            handle_callback_query(call, self.bot, self.security, self.settings)

    def prepare_directories(self) -> None:
        """Prepare required directories and validate Excel file."""
        update_db_dir = self.settings.paths.update_db_dir
        files_dir = self.settings.paths.files_dir
        games_excel = self.settings.paths.games_excel_file

        # Ensure update_db directory exists and is empty
        # Use safe directory cleaning to prevent path traversal attacks
        update_db_dir.mkdir(parents=True, exist_ok=True)
        clean_directory_safely(update_db_dir, update_db_dir, keep_dirs=False)

        # Ensure files directory exists
        files_dir.mkdir(parents=True, exist_ok=True)

        # Ensure main Excel file exists
        if not games_excel.exists():
            raise ValueError(
                "You don't have file for DB creation at path " f"'{games_excel}'"
            )

    def run(self) -> None:
        """Start bot polling with error handling."""
        try:
            self.prepare_directories()
            self.bot.polling()
        except OSError:
            logger.exception("OS error during bot polling, restarting in 10s")
            self.bot.stop_polling()
            sleep(10)
            self.bot.polling()


def main() -> None:
    """Prepare directories and start bot polling."""
    configure_logging()
    settings = load_settings_config()
    tokens = load_tokens_config()
    users = load_users_config()

    app = BotApplication(settings, tokens, users)
    app.setup_handlers()
    app.run()


if __name__ == "__main__":
    main()
