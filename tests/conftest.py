"""Shared pytest configuration and fixtures."""

from __future__ import annotations

# Import all fixtures from fixtures modules
# This makes them available to all tests automatically
# Using absolute imports for pytest compatibility
from tests.fixtures.db import empty_db, temp_db
from tests.fixtures.excel import empty_excel, temp_excel
from tests.fixtures.telegram import (
    admin_security,
    bot_app,
    mock_bot,
    mock_message,
    mock_message_with_document,
    mock_steam_api,
    test_config,
    test_tokens,
    test_users,
    user_security,
)

__all__ = [
    # Database fixtures
    "temp_db",
    "empty_db",
    # Excel fixtures
    "temp_excel",
    "empty_excel",
    # Telegram fixtures
    "mock_bot",
    "mock_message",
    "mock_message_with_document",
    "admin_security",
    "user_security",
    "test_config",
    "test_tokens",
    "test_users",
    "mock_steam_api",
    "bot_app",
]
