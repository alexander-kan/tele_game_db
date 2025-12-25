"""Callback query handlers for inline keyboard menus."""

from __future__ import annotations

import logging

import telebot
from telebot.types import CallbackQuery

from .config import DEFAULT_PLATFORMS, SettingsConfig
from .db import ChangeDB
from .exceptions import DatabaseError, GameDBError
from .inline_menu import InlineMenu
from .menu_callbacks import CallbackAction, parse_callback_data
from .security import Security
from .services import game_service
from .services.message_formatter import MessageFormatter
from . import texts

logger = logging.getLogger("game_db.bot")


def _send_menu_at_bottom(
    bot: telebot.TeleBot,
    chat_id: int,
    menu_markup: telebot.types.InlineKeyboardMarkup,
    message_text: str | None = None,
) -> None:
    """Send menu message at the bottom (for UX: results first, menu last).

    Args:
        bot: Telegram bot instance
        chat_id: Chat ID to send message to
        menu_markup: Inline keyboard markup
        message_text: Optional text to send with menu
    """
    if message_text:
        bot.send_message(chat_id, message_text, reply_markup=menu_markup)
    else:
        bot.send_message(chat_id, texts.MAIN_MENU, reply_markup=menu_markup)


def handle_callback_query(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    settings: SettingsConfig,
) -> None:
    """Handle callback query from inline keyboard.

    Args:
        call: CallbackQuery object from Telegram
        bot: Telegram bot instance
        security: Security instance for permission checks
        settings: Application settings
    """
    user_id = call.from_user.id if call.from_user else None

    if not security.user_check(user_id):
        logger.warning(
            "[UNAUTHORIZED_ACCESS] Unauthorized user %s tried to use callback",
            user_id,
        )
        bot.answer_callback_query(call.id, texts.PRIVATE_BOT_TEXT, show_alert=True)
        return

    try:
        action, args = parse_callback_data(call.data)
        logger.debug(
            "[CALLBACK] User %s triggered action %s with args %s",
            user_id,
            action,
            args,
        )

        if action == CallbackAction.MAIN_MENU:
            _handle_main_menu(call, bot, security)
        elif action == CallbackAction.MY_GAMES:
            _handle_my_games(call, bot, security)
        elif action == CallbackAction.STEAM_GAMES:
            _handle_steam_games(call, bot, security)
        elif action == CallbackAction.SWITCH_GAMES:
            _handle_switch_games(call, bot, security)
        elif action == CallbackAction.GAMES_LIST:
            _handle_games_list(call, bot, security, args)
        elif action == CallbackAction.COUNT_COMPLETED:
            _handle_count_completed(call, bot, security, args)
        elif action == CallbackAction.COUNT_TIME:
            _handle_count_time(call, bot, security, args)
        elif action == CallbackAction.STATISTICS:
            _handle_statistics(call, bot, security)
        elif action == CallbackAction.STATS_COMPLETED:
            _handle_stats_completed(call, bot, security)
        elif action == CallbackAction.STATS_TIME:
            _handle_stats_time(call, bot, security)
        elif action == CallbackAction.COMMANDS:
            _handle_commands(call, bot, security)
        elif action == CallbackAction.SHOW_USER_COMMANDS:
            _handle_show_user_commands(call, bot, security)
        elif action == CallbackAction.SHOW_ADMIN_COMMANDS:
            _handle_show_admin_commands(call, bot, security)
        elif action == CallbackAction.ADMIN_PANEL:
            _handle_admin_panel(call, bot, security)
        elif action == CallbackAction.FILE_MANAGEMENT:
            _handle_file_management(call, bot, security)
        elif action == CallbackAction.LIST_FILES:
            _handle_list_files(call, bot, security, settings)
        elif action == CallbackAction.DOWNLOAD_TEMPLATE:
            _handle_download_template(call, bot, security, settings)
        elif action == CallbackAction.SYNC_MENU:
            _handle_sync_menu(call, bot, security)
        elif action == CallbackAction.SYNC_STEAM:
            _handle_sync_steam_menu(call, bot, security)
        elif action == CallbackAction.SYNC_STEAM_EXECUTE:
            _handle_sync_steam_execute(call, bot, security, settings)
        elif action == CallbackAction.SYNC_METACRITIC:
            _handle_sync_metacritic_menu(call, bot, security)
        elif action == CallbackAction.SYNC_METACRITIC_FULL:
            _handle_sync_metacritic_execute(call, bot, security, settings, False)
        elif action == CallbackAction.SYNC_METACRITIC_PARTIAL:
            _handle_sync_metacritic_execute(call, bot, security, settings, True)
        elif action == CallbackAction.SYNC_HLTB:
            _handle_sync_hltb_menu(call, bot, security)
        elif action == CallbackAction.SYNC_HLTB_FULL:
            _handle_sync_hltb_execute(call, bot, security, settings, False)
        elif action == CallbackAction.SYNC_HLTB_PARTIAL:
            _handle_sync_hltb_execute(call, bot, security, settings, True)
        elif action == CallbackAction.BACK_TO_MY_GAMES:
            _handle_my_games(call, bot, security)
        elif action == CallbackAction.BACK_TO_MY_GAMES_FROM_STATS:
            _handle_my_games(call, bot, security)
        elif action == CallbackAction.BACK_TO_MAIN:
            _handle_main_menu(call, bot, security)
        elif action == CallbackAction.BACK_TO_MAIN_FROM_ADMIN:
            _handle_main_menu(call, bot, security)
        elif action == CallbackAction.BACK_TO_MAIN_FROM_SYNC:
            _handle_main_menu(call, bot, security)
        elif action == CallbackAction.BACK_TO_ADMIN:
            _handle_admin_panel(call, bot, security)
        elif action == CallbackAction.BACK_TO_SYNC_MENU:
            _handle_sync_menu(call, bot, security)
        elif action == CallbackAction.BACK_TO_SYNC_MENU_FROM_METACRITIC:
            _handle_sync_menu(call, bot, security)
        elif action == CallbackAction.BACK_TO_SYNC_MENU_FROM_HLTB:
            _handle_sync_menu(call, bot, security)
        else:
            logger.warning(
                "[CALLBACK] Unknown action %s from user %s", action, user_id
            )
            bot.answer_callback_query(call.id, "Неизвестное действие")

    except Exception as e:
        logger.exception(
            "[CALLBACK] Error handling callback from user %s: %s", user_id, str(e)
        )
        bot.answer_callback_query(
            call.id, "Произошла ошибка при обработке запроса", show_alert=True
        )


def _handle_main_menu(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle main menu callback."""
    user_id = call.from_user.id if call.from_user else None
    bot.edit_message_text(
        texts.MAIN_MENU,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.main_menu(security, user_id),
    )
    bot.answer_callback_query(call.id)


def _handle_my_games(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle 'My Games' submenu callback."""
    bot.edit_message_text(
        "Мои игры",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.my_games_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_steam_games(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle Steam games submenu callback."""
    bot.edit_message_text(
        "Steam игры",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.platform_menu("Steam"),
    )
    bot.answer_callback_query(call.id)


def _handle_switch_games(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle Switch games submenu callback."""
    bot.edit_message_text(
        "Switch игры",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.platform_menu("Switch"),
    )
    bot.answer_callback_query(call.id)


def _handle_games_list(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    args: list[str],
) -> None:
    """Handle games list callback with pagination.

    Args:
        call: CallbackQuery object
        bot: Telegram bot instance
        security: Security instance
        args: List of [platform, offset, limit]
    """
    if len(args) < 3:
        logger.warning("[CALLBACK] Invalid args for GAMES_LIST: %s", args)
        bot.answer_callback_query(call.id, "Ошибка: неверные параметры")
        return

    platform = args[0]
    try:
        offset = int(args[1])
        limit = int(args[2])
    except ValueError:
        logger.warning("[CALLBACK] Invalid offset/limit for GAMES_LIST: %s", args)
        bot.answer_callback_query(call.id, "Ошибка: неверные параметры пагинации")
        return

    try:
        games = game_service.get_next_game_list(offset - 1, limit, platform)
        formatter = MessageFormatter()
        message_text = formatter.format_game_list(games)

        # Calculate next offset for pagination
        next_offset = offset + limit

        bot.edit_message_text(
            message_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=InlineMenu.platform_menu_with_pagination(
                platform, next_offset, limit
            ),
        )
        bot.answer_callback_query(call.id)
    except (DatabaseError, GameDBError) as e:
        logger.exception(
            "[CALLBACK] Error getting games list for platform %s: %s", platform, str(e)
        )
        bot.answer_callback_query(call.id, "Ошибка при получении списка игр", show_alert=True)


def _handle_count_completed(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    args: list[str],
) -> None:
    """Handle count completed games callback.

    Args:
        call: CallbackQuery object
        bot: Telegram bot instance
        security: Security instance
        args: List with [platform]
    """
    if not args:
        logger.warning("[CALLBACK] Invalid args for COUNT_COMPLETED: %s", args)
        bot.answer_callback_query(call.id, "Ошибка: неверные параметры")
        return

    platform = args[0]
    try:
        count = game_service.count_complete_games(platform)
        message_text = f"Пройдено игр на {platform}: {count}"
        bot.edit_message_text(
            message_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=InlineMenu.platform_menu(platform),
        )
        bot.answer_callback_query(call.id)
    except (DatabaseError, GameDBError) as e:
        logger.exception(
            "[CALLBACK] Error counting completed games for platform %s: %s",
            platform,
            str(e),
        )
        bot.answer_callback_query(
            call.id, "Ошибка при подсчёте пройденных игр", show_alert=True
        )


def _handle_count_time(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    args: list[str],
) -> None:
    """Handle count time callback.

    Args:
        call: CallbackQuery object
        bot: Telegram bot instance
        security: Security instance
        args: List with [platform]
    """
    if not args:
        logger.warning("[CALLBACK] Invalid args for COUNT_TIME: %s", args)
        bot.answer_callback_query(call.id, "Ошибка: неверные параметры")
        return

    platform = args[0]
    try:
        # Mode 1 = all games (not just completed)
        expected_time, real_time = game_service.count_spend_time(platform, mode=1)
        formatter = MessageFormatter()
        platform_times = {platform: (expected_time, real_time)}
        message_text = formatter.format_time_stats(
            platform_times, 0.0, show_total=False
        )

        bot.edit_message_text(
            message_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=InlineMenu.platform_menu(platform),
        )
        bot.answer_callback_query(call.id)
    except (DatabaseError, GameDBError) as e:
        logger.exception(
            "[CALLBACK] Error counting time for platform %s: %s", platform, str(e)
        )
        bot.answer_callback_query(call.id, "Ошибка при подсчёте времени", show_alert=True)


def _handle_statistics(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle statistics submenu callback."""
    bot.edit_message_text(
        "Статистика",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.statistics_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_stats_completed(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle stats completed callback."""
    try:
        platforms = game_service.get_platforms() or DEFAULT_PLATFORMS
        platform_counts = {}
        for platform in platforms:
            try:
                count = game_service.count_complete_games(platform)
                platform_counts[platform] = count
            except (DatabaseError, GameDBError):
                platform_counts[platform] = 0

        formatter = MessageFormatter()
        message_text = formatter.format_completed_games_stats(platform_counts)

        bot.edit_message_text(
            message_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=InlineMenu.statistics_menu(),
        )
        bot.answer_callback_query(call.id)
    except (DatabaseError, GameDBError) as e:
        logger.exception("[CALLBACK] Error getting stats completed: %s", str(e))
        bot.answer_callback_query(
            call.id, "Ошибка при получении статистики", show_alert=True
        )


def _handle_stats_time(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle stats time callback."""
    try:
        platforms = game_service.get_platforms() or DEFAULT_PLATFORMS
        platform_times = {}
        total_real_seconds = 0.0

        for platform in platforms:
            try:
                expected_time, real_time = game_service.count_spend_time(platform, mode=1)
                platform_times[platform] = (expected_time, real_time)
                if real_time is not None:
                    total_real_seconds += real_time * 3600
            except (DatabaseError, GameDBError):
                platform_times[platform] = (None, None)

        formatter = MessageFormatter()
        message_text = formatter.format_time_stats(
            platform_times, total_real_seconds, show_total=True
        )

        bot.edit_message_text(
            message_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=InlineMenu.statistics_menu(),
        )
        bot.answer_callback_query(call.id)
    except (DatabaseError, GameDBError) as e:
        logger.exception("[CALLBACK] Error getting stats time: %s", str(e))
        bot.answer_callback_query(
            call.id, "Ошибка при получении статистики", show_alert=True
        )


def _handle_commands(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle commands submenu callback."""
    user_id = call.from_user.id if call.from_user else None
    bot.edit_message_text(
        "Команды",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.commands_menu(security, user_id),
    )
    bot.answer_callback_query(call.id)


def _handle_show_user_commands(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle show user commands callback."""
    bot.edit_message_text(
        texts.USER_COMMANDS_HELP,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.commands_menu(security, call.from_user.id if call.from_user else None),
    )
    bot.answer_callback_query(call.id)


def _handle_show_admin_commands(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle show admin commands callback."""
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    bot.edit_message_text(
        texts.ADMIN_COMMANDS_HELP,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.admin_panel_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_admin_panel(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle admin panel submenu callback."""
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    bot.edit_message_text(
        "Админ-панель",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.admin_panel_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_file_management(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle file management submenu callback."""
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    bot.edit_message_text(
        texts.FILE_MENU,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.file_management_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_list_files(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    settings: SettingsConfig,
) -> None:
    """Handle list files callback."""
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    try:
        files_dir = settings.paths.files_dir
        if not files_dir.exists():
            files_dir.mkdir(parents=True, exist_ok=True)

        files = sorted(files_dir.iterdir())
        if not files:
            message_text = "Файлы не найдены"
        else:
            file_list = "\n".join(f"• {f.name}" for f in files if f.is_file())
            message_text = f"Доступные файлы:\n\n{file_list}"

        bot.edit_message_text(
            message_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=InlineMenu.file_management_menu(),
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.exception("[CALLBACK] Error listing files: %s", str(e))
        bot.answer_callback_query(call.id, "Ошибка при получении списка файлов", show_alert=True)


def _handle_download_template(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    settings: SettingsConfig,
) -> None:
    """Handle download template callback."""
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    try:
        template_path = settings.paths.games_excel_file
        if not template_path.exists():
            bot.answer_callback_query(
                call.id, "Файл шаблона не найден", show_alert=True
            )
            return

        with open(template_path, "rb") as file_obj:
            bot.send_document(call.message.chat.id, file_obj)
        bot.answer_callback_query(call.id, "Шаблон отправлен")
    except Exception as e:
        logger.exception("[CALLBACK] Error sending template: %s", str(e))
        bot.answer_callback_query(call.id, "Ошибка при отправке шаблона", show_alert=True)


def _handle_sync_menu(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle sync menu callback."""
    bot.edit_message_text(
        "Синхронизация Базы",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.sync_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_sync_steam_menu(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle Steam sync menu callback."""
    bot.edit_message_text(
        "Синхронизация Steam",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.steam_sync_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_sync_steam_execute(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    settings: SettingsConfig,
) -> None:
    """Handle Steam sync execution callback."""
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    bot.answer_callback_query(call.id, "Запущена синхронизация Steam...")

    try:
        create = ChangeDB()
        xlsx_path = str(settings.paths.games_excel_file)
        success, similarity_matches = create.synchronize_steam_games(xlsx_path)

        if success:
            formatter = MessageFormatter()
            missing_games_text = formatter.format_steam_sync_missing_games(similarity_matches)

            # Send results first, then menu
            if missing_games_text:
                bot.send_message(call.message.chat.id, missing_games_text)
            bot.send_message(
                call.message.chat.id,
                texts.STEAM_SYNC_SUCCESS,
                reply_markup=InlineMenu.steam_sync_menu(),
            )
        else:
            bot.send_message(
                call.message.chat.id,
                texts.STEAM_SYNC_ERROR,
                reply_markup=InlineMenu.steam_sync_menu(),
            )
    except Exception as e:
        logger.exception("[CALLBACK] Error executing Steam sync: %s", str(e))
        bot.send_message(
            call.message.chat.id,
            texts.STEAM_SYNC_ERROR,
            reply_markup=InlineMenu.steam_sync_menu(),
        )


def _handle_sync_metacritic_menu(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle Metacritic sync menu callback."""
    bot.edit_message_text(
        "Синхронизация Metacritic",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.metacritic_sync_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_sync_metacritic_execute(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    settings: SettingsConfig,
    partial_mode: bool,
) -> None:
    """Handle Metacritic sync execution callback.

    Args:
        call: CallbackQuery object
        bot: Telegram bot instance
        security: Security instance
        settings: Application settings
        partial_mode: If True, only sync games missing scores
    """
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    bot.answer_callback_query(call.id, "Запущена синхронизация Metacritic...")

    try:
        create = ChangeDB()
        xlsx_path = str(settings.paths.games_excel_file)
        result = create.synchronize_metacritic_games(
            xlsx_path, test_mode=False, partial_mode=partial_mode
        )

        if result is None:
            # No data to sync (partial mode only)
            message_text = texts.METACRITIC_SYNC_NO_DATA
        elif result:
            message_text = texts.METACRITIC_SYNC_SUCCESS
        else:
            message_text = texts.METACRITIC_SYNC_ERROR

        bot.send_message(
            call.message.chat.id,
            message_text,
            reply_markup=InlineMenu.metacritic_sync_menu(),
        )
    except Exception as e:
        logger.exception("[CALLBACK] Error executing Metacritic sync: %s", str(e))
        bot.send_message(
            call.message.chat.id,
            texts.METACRITIC_SYNC_ERROR,
            reply_markup=InlineMenu.metacritic_sync_menu(),
        )


def _handle_sync_hltb_menu(call: CallbackQuery, bot: telebot.TeleBot, security: Security) -> None:
    """Handle HowLongToBeat sync menu callback."""
    bot.edit_message_text(
        "Синхронизация HowLongToBeat",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=InlineMenu.hltb_sync_menu(),
    )
    bot.answer_callback_query(call.id)


def _handle_sync_hltb_execute(
    call: CallbackQuery,
    bot: telebot.TeleBot,
    security: Security,
    settings: SettingsConfig,
    partial_mode: bool,
) -> None:
    """Handle HowLongToBeat sync execution callback.

    Args:
        call: CallbackQuery object
        bot: Telegram bot instance
        security: Security instance
        settings: Application settings
        partial_mode: If True, only sync games missing average_time_beat
    """
    user_id = call.from_user.id if call.from_user else None
    if not security.admin_check(user_id):
        bot.answer_callback_query(call.id, texts.PERMISSION_DENIED_TEXT, show_alert=True)
        return

    bot.answer_callback_query(call.id, "Запущена синхронизация HowLongToBeat...")

    try:
        create = ChangeDB()
        xlsx_path = str(settings.paths.games_excel_file)
        result = create.synchronize_hltb_games(
            xlsx_path, test_mode=False, partial_mode=partial_mode
        )

        if result is None:
            # No data to sync (partial mode only)
            message_text = texts.HLTB_SYNC_NO_DATA
        elif result:
            message_text = texts.HLTB_SYNC_SUCCESS
        else:
            message_text = texts.HLTB_SYNC_ERROR

        bot.send_message(
            call.message.chat.id,
            message_text,
            reply_markup=InlineMenu.hltb_sync_menu(),
        )
    except Exception as e:
        logger.exception("[CALLBACK] Error executing HLTB sync: %s", str(e))
        bot.send_message(
            call.message.chat.id,
            texts.HLTB_SYNC_ERROR,
            reply_markup=InlineMenu.hltb_sync_menu(),
        )
