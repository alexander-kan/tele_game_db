"""Callback data constants for inline keyboard menus."""

from enum import Enum


class CallbackAction(str, Enum):
    """Callback action types for menu navigation."""

    # Main menu
    MAIN_MENU = "main"
    MY_GAMES = "my_games"
    COMMANDS = "commands"
    ADMIN_PANEL = "admin_panel"
    SYNC_MENU = "sync_menu"

    # My Games submenu
    STEAM_GAMES = "steam_games"
    SWITCH_GAMES = "switch_games"
    STATISTICS = "statistics"

    # Platform submenu (Steam/Switch)
    GAMES_LIST = "games_list"
    COUNT_COMPLETED = "count_completed"
    COUNT_TIME = "count_time"
    BACK_TO_MY_GAMES = "back_my_games"

    # Statistics submenu
    STATS_COMPLETED = "stats_completed"
    STATS_TIME = "stats_time"
    BACK_TO_MY_GAMES_FROM_STATS = "back_my_games_from_stats"

    # Commands submenu
    SHOW_USER_COMMANDS = "show_user_commands"
    SHOW_ADMIN_COMMANDS = "show_admin_commands"
    BACK_TO_MAIN = "back_main"

    # Admin panel submenu
    FILE_MANAGEMENT = "file_management"
    ADMIN_COMMANDS = "admin_commands"
    BACK_TO_MAIN_FROM_ADMIN = "back_main_from_admin"

    # File management submenu
    LIST_FILES = "list_files"
    DOWNLOAD_TEMPLATE = "download_template"
    BACK_TO_ADMIN = "back_admin"

    # Sync menu
    SYNC_STEAM = "sync_steam"
    CHECK_STEAM = "check_steam"
    ADD_STEAM_GAMES = "add_steam_games"
    SYNC_STEAM_EXECUTE = "sync_steam_execute"
    BACK_TO_SYNC_MENU = "back_to_sync_menu"
    BACK_TO_MAIN_FROM_SYNC = "back_main_from_sync"

    # Metacritic sync
    SYNC_METACRITIC = "sync_metacritic"
    SYNC_METACRITIC_FULL = "sync_metacritic_full"
    SYNC_METACRITIC_PARTIAL = "sync_metacritic_partial"
    BACK_TO_SYNC_MENU_FROM_METACRITIC = "back_to_sync_menu_from_metacritic"

    # HowLongToBeat sync
    SYNC_HLTB = "sync_hltb"
    SYNC_HLTB_FULL = "sync_hltb_full"
    SYNC_HLTB_PARTIAL = "sync_hltb_partial"
    BACK_TO_SYNC_MENU_FROM_HLTB = "back_to_sync_menu_from_hltb"


def build_callback_data(action: CallbackAction, *args: str) -> str:
    """Build callback data string from action and optional arguments.

    Args:
        action: Callback action type
        *args: Optional additional arguments (e.g., platform, offset, limit)

    Returns:
        Formatted callback data string
    """
    parts = [action.value]
    parts.extend(str(arg) for arg in args)
    return "|".join(parts)


def parse_callback_data(data: str) -> tuple[CallbackAction, list[str]]:
    """Parse callback data string into action and arguments.

    Args:
        data: Callback data string

    Returns:
        Tuple of (action, list of arguments)
    """
    parts = data.split("|")
    try:
        action = CallbackAction(parts[0])
        args = parts[1:] if len(parts) > 1 else []
        return action, args
    except ValueError:
        # Fallback for unknown actions
        return CallbackAction.MAIN_MENU, []
