"""Inline keyboard menu building for Telegram bot."""

from __future__ import annotations

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from .menu_callbacks import CallbackAction, build_callback_data
from .security import Security


class InlineMenu:
    """Build inline keyboards for the bot."""

    @staticmethod
    def main_menu(security: Security, user_id: int) -> InlineKeyboardMarkup:
        """Build main menu inline keyboard.

        Args:
            security: Security instance for admin checks
            user_id: User ID to check admin status

        Returns:
            InlineKeyboardMarkup with main menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="🎮 My Games",
                callback_data=build_callback_data(CallbackAction.MY_GAMES),
            ),
            InlineKeyboardButton(
                text="📋 Commands",
                callback_data=build_callback_data(CallbackAction.COMMANDS),
            ),
        )

        if security.admin_check(user_id):
            markup.add(
                InlineKeyboardButton(
                    text="🛠 Admin Panel",
                    callback_data=build_callback_data(CallbackAction.ADMIN_PANEL),
                )
            )

        markup.add(
            InlineKeyboardButton(
                text="🔄 Database Sync",
                callback_data=build_callback_data(CallbackAction.SYNC_MENU),
            )
        )

        return markup

    @staticmethod
    def my_games_menu() -> InlineKeyboardMarkup:
        """Build 'My Games' submenu inline keyboard.

        Returns:
            InlineKeyboardMarkup with my games menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="💾 Steam Games",
                callback_data=build_callback_data(CallbackAction.STEAM_GAMES),
            ),
            InlineKeyboardButton(
                text="🎮 Switch Games",
                callback_data=build_callback_data(CallbackAction.SWITCH_GAMES),
            ),
            InlineKeyboardButton(
                text="📊 Statistics",
                callback_data=build_callback_data(CallbackAction.STATISTICS),
            ),
            InlineKeyboardButton(
                text="⬅️ Back to Main Menu",
                callback_data=build_callback_data(CallbackAction.MAIN_MENU),
            ),
        )
        return markup

    @staticmethod
    def platform_menu(
        platform: str, offset: int = 1, limit: int = 10
    ) -> InlineKeyboardMarkup:
        """Build platform-specific menu (Steam/Switch) inline keyboard.

        Args:
            platform: Platform name (Steam or Switch)
            offset: Current offset for pagination
            limit: Number of games per page

        Returns:
            InlineKeyboardMarkup with platform menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        end_range = offset + limit - 1
        range_text = f"🔢 Games ({offset}–{end_range})"
        markup.add(
            InlineKeyboardButton(
                text=range_text,
                callback_data=build_callback_data(
                    CallbackAction.GAMES_LIST, platform, str(offset), str(limit)
                ),
            ),
            InlineKeyboardButton(
                text="📈 Completed Count",
                callback_data=build_callback_data(
                    CallbackAction.COUNT_COMPLETED, platform
                ),
            ),
            InlineKeyboardButton(
                text="⏱ Time in Games",
                callback_data=build_callback_data(
                    CallbackAction.COUNT_TIME, platform
                ),
            ),
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data=build_callback_data(CallbackAction.BACK_TO_MY_GAMES),
            ),
        )
        return markup

    @staticmethod
    def platform_menu_with_pagination(
        platform: str, offset: int, limit: int
    ) -> InlineKeyboardMarkup:
        """Build platform menu with updated pagination.

        Args:
            platform: Platform name (Steam or Switch)
            offset: Next offset for pagination
            limit: Number of games per page

        Returns:
            InlineKeyboardMarkup with updated pagination
        """
        markup = InlineKeyboardMarkup(row_width=1)
        end_range = offset + limit - 1
        range_text = f"🔢 Games ({offset}–{end_range})"
        markup.add(
            InlineKeyboardButton(
                text=range_text,
                callback_data=build_callback_data(
                    CallbackAction.GAMES_LIST, platform, str(offset), str(limit)
                ),
            ),
            InlineKeyboardButton(
                text="📈 Completed Count",
                callback_data=build_callback_data(
                    CallbackAction.COUNT_COMPLETED, platform
                ),
            ),
            InlineKeyboardButton(
                text="⏱ Time in Games",
                callback_data=build_callback_data(
                    CallbackAction.COUNT_TIME, platform
                ),
            ),
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data=build_callback_data(CallbackAction.BACK_TO_MY_GAMES),
            ),
        )
        return markup

    @staticmethod
    def statistics_menu() -> InlineKeyboardMarkup:
        """Build statistics submenu inline keyboard.

        Returns:
            InlineKeyboardMarkup with statistics menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="📈 Completed Games",
                callback_data=build_callback_data(CallbackAction.STATS_COMPLETED),
            ),
            InlineKeyboardButton(
                text="⏱ Time Spent",
                callback_data=build_callback_data(CallbackAction.STATS_TIME),
            ),
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data=build_callback_data(
                    CallbackAction.BACK_TO_MY_GAMES_FROM_STATS
                ),
            ),
        )
        return markup

    @staticmethod
    def commands_menu(security: Security, user_id: int) -> InlineKeyboardMarkup:
        """Build commands submenu inline keyboard.

        Args:
            security: Security instance for admin checks
            user_id: User ID to check admin status

        Returns:
            InlineKeyboardMarkup with commands menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="📖 User Commands",
                callback_data=build_callback_data(CallbackAction.SHOW_USER_COMMANDS),
            ),
            InlineKeyboardButton(
                text="⬅️ Back to Main Menu",
                callback_data=build_callback_data(
                    CallbackAction.BACK_TO_MAIN
                ),
            ),
        )
        return markup

    @staticmethod
    def admin_panel_menu() -> InlineKeyboardMarkup:
        """Build admin panel submenu inline keyboard.

        Returns:
            InlineKeyboardMarkup with admin panel menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="📁 File Management",
                callback_data=build_callback_data(CallbackAction.FILE_MANAGEMENT),
            ),
            InlineKeyboardButton(
                text="🧰 Admin Commands",
                callback_data=build_callback_data(CallbackAction.ADMIN_COMMANDS),
            ),
            InlineKeyboardButton(
                text="⬅️ Back to Main Menu",
                callback_data=build_callback_data(
                    CallbackAction.BACK_TO_MAIN_FROM_ADMIN
                ),
            ),
        )
        return markup

    @staticmethod
    def file_management_menu() -> InlineKeyboardMarkup:
        """Build file management submenu inline keyboard.

        Returns:
            InlineKeyboardMarkup with file management menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="📄 File List",
                callback_data=build_callback_data(CallbackAction.LIST_FILES),
            ),
            InlineKeyboardButton(
                text="⬇️ Download Game Template",
                callback_data=build_callback_data(CallbackAction.DOWNLOAD_TEMPLATE),
            ),
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data=build_callback_data(CallbackAction.BACK_TO_ADMIN),
            ),
        )
        return markup

    @staticmethod
    def sync_menu() -> InlineKeyboardMarkup:
        """Build sync menu inline keyboard.

        Returns:
            InlineKeyboardMarkup with sync menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="🔍 Check Steam Data",
                callback_data=build_callback_data(CallbackAction.CHECK_STEAM),
            ),
            InlineKeyboardButton(
                text="🔄 Steam Sync",
                callback_data=build_callback_data(CallbackAction.SYNC_STEAM_EXECUTE),
            ),
            InlineKeyboardButton(
                text="🎯 Metacritic Sync",
                callback_data=build_callback_data(CallbackAction.SYNC_METACRITIC),
            ),
            InlineKeyboardButton(
                text="⏱ HowLongToBeat Sync",
                callback_data=build_callback_data(CallbackAction.SYNC_HLTB),
            ),
            InlineKeyboardButton(
                text="⬅️ Back to Main Menu",
                callback_data=build_callback_data(CallbackAction.BACK_TO_MAIN_FROM_SYNC),
            ),
        )
        return markup

    @staticmethod
    def steam_check_menu(has_missing_games: bool = False) -> InlineKeyboardMarkup:
        """Build Steam check menu inline keyboard.

        Args:
            has_missing_games: If True, show "Add Found Games to DB" button

        Returns:
            InlineKeyboardMarkup with Steam check menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        if has_missing_games:
            markup.add(
                InlineKeyboardButton(
                    text="➕ Add Found Games to DB",
                    callback_data=build_callback_data(
                        CallbackAction.ADD_STEAM_GAMES
                    ),
                ),
            )
        markup.add(
            InlineKeyboardButton(
                text="🔍 Check Steam Data",
                callback_data=build_callback_data(CallbackAction.CHECK_STEAM),
            ),
            InlineKeyboardButton(
                text="⬅️ Back to Sync Menu",
                callback_data=build_callback_data(
                    CallbackAction.BACK_TO_SYNC_MENU
                ),
            ),
        )
        return markup

    @staticmethod
    def metacritic_sync_menu() -> InlineKeyboardMarkup:
        """Build Metacritic sync submenu inline keyboard.

        Returns:
            InlineKeyboardMarkup with Metacritic sync menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="🎯 Metacritic Sync Full",
                callback_data=build_callback_data(
                    CallbackAction.SYNC_METACRITIC_FULL
                ),
            ),
            InlineKeyboardButton(
                text="🎯 Metacritic Sync Partial",
                callback_data=build_callback_data(
                    CallbackAction.SYNC_METACRITIC_PARTIAL
                ),
            ),
            InlineKeyboardButton(
                text="⬅️ Back to Sync Menu",
                callback_data=build_callback_data(
                    CallbackAction.BACK_TO_SYNC_MENU_FROM_METACRITIC
                ),
            ),
        )
        return markup

    @staticmethod
    def hltb_sync_menu() -> InlineKeyboardMarkup:
        """Build HowLongToBeat sync submenu inline keyboard.

        Returns:
            InlineKeyboardMarkup with HowLongToBeat sync menu buttons
        """
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                text="⏱ HowLongToBeat Sync Full",
                callback_data=build_callback_data(
                    CallbackAction.SYNC_HLTB_FULL
                ),
            ),
            InlineKeyboardButton(
                text="⏱ HowLongToBeat Sync Partial",
                callback_data=build_callback_data(
                    CallbackAction.SYNC_HLTB_PARTIAL
                ),
            ),
            InlineKeyboardButton(
                text="⬅️ Back to Sync Menu",
                callback_data=build_callback_data(
                    CallbackAction.BACK_TO_SYNC_MENU_FROM_HLTB
                ),
            ),
        )
        return markup
