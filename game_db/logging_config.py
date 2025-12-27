"""Centralized logging configuration for the project."""

from __future__ import annotations

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _create_base_handlers(level: int) -> list[logging.Handler]:
    """Create console and rotating file handlers with common formatter."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "game_db.log"

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    return [file_handler, console_handler]


def configure_logging(level: int = logging.INFO) -> None:
    """Configure logging for application, HTTP, SQL and bot loggers.

    This sets up:
    - root logger with console and rotating file handlers;
    - dedicated named loggers:
      * ``game_db.bot``     – Telegram bot events;
      * ``game_db.sql``     – database/SQL operations;
      * ``game_db.http``    – HTTP/requests and external APIs.
    """
    handlers = _create_base_handlers(level)

    # Root logger
    logging.basicConfig(level=level, handlers=handlers, force=True)

    # Application-specific loggers
    bot_logger: Logger = logging.getLogger("game_db.bot")
    sql_logger: Logger = logging.getLogger("game_db.sql")
    http_logger: Logger = logging.getLogger("game_db.http")

    for logger in (bot_logger, sql_logger, http_logger):
        logger.setLevel(level)
        logger.propagate = True  # use root handlers

    # Tune third-party libraries if needed
    logging.getLogger("requests").setLevel(logging.WARNING)
