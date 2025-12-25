"""Command pattern implementation for bot handlers."""

from __future__ import annotations

from .base import Command
from .command_handler import CommandHandler
from .file_commands import (
    GetFileCommand,
    RemoveFileCommand,
    SyncSteamCommand,
)
from .game_commands import (
    CountGamesCommand,
    CountTimeCommand,
    GetGameCommand,
    SteamGameListCommand,
    SwitchGameListCommand,
)
from .menu_commands import (
    ClearMenuCommand,
    FileMenuCommand,
    GameListsMenuCommand,
    MainMenuCommand,
    ShowAdminCommandsCommand,
    ShowCommandsCommand,
)

__all__ = [
    "Command",
    "CommandHandler",
    "ClearMenuCommand",
    "MainMenuCommand",
    "FileMenuCommand",
    "GameListsMenuCommand",
    "ShowCommandsCommand",
    "ShowAdminCommandsCommand",
    "GetGameCommand",
    "SteamGameListCommand",
    "SwitchGameListCommand",
    "CountGamesCommand",
    "CountTimeCommand",
    "RemoveFileCommand",
    "GetFileCommand",
    "SyncSteamCommand",
]
