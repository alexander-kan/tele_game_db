"""Handlers for Telegram bot messages and commands."""

from __future__ import annotations

import logging

import telebot
from telebot.types import Message

from . import db as db_module
from . import menu, texts
from .commands import (
    ClearMenuCommand,
    CommandHandler,
    CountGamesCommand,
    CountTimeCommand,
    FileMenuCommand,
    GameListsMenuCommand,
    GetFileCommand,
    GetGameCommand,
    MainMenuCommand,
    RemoveFileCommand,
    ShowAdminCommandsCommand,
    ShowCommandsCommand,
    SteamGameListCommand,
    SwitchGameListCommand,
    SyncSteamCommand,
)
from .config import DEFAULT_PLATFORMS, SettingsConfig
from .exceptions import DatabaseError, GameDBError
from .inline_menu import InlineMenu
from .security import Security
from .services import game_service
from .services.message_formatter import MessageFormatter
from .utils import (
    is_file_type_allowed,
    is_path_safe,
    safe_delete_file,
    validate_file_name,
)

logger = logging.getLogger("game_db.bot")

# Global command handler instance
_command_handler: CommandHandler | None = None


def _get_command_handler(owner_name: str | None = None) -> CommandHandler:
    """Get or create the global command handler instance.

    Args:
        owner_name: Name of the database owner (defaults to "Alexander")

    Returns:
        CommandHandler instance with all commands registered
    """
    global _command_handler
    if _command_handler is None:
        _command_handler = CommandHandler()

        # Register menu commands
        _command_handler.register_exact("Clear Menu", ClearMenuCommand())
        _command_handler.register_exact("Back to Main Menu", MainMenuCommand())
        _command_handler.register_exact("File Management Menu", FileMenuCommand())
        _command_handler.register_exact("Game Lists", GameListsMenuCommand())
        _command_handler.register_exact(
            "Show Available Commands", ShowCommandsCommand()
        )
        _command_handler.register_exact(
            "Show Admin Commands",
            ShowAdminCommandsCommand(),
        )

        # Register game commands (use owner_name from settings, default to "Alexander")
        owner = owner_name if owner_name is not None else "Alexander"
        _command_handler.register_exact(
            f"How many games {owner} completed", CountGamesCommand()
        )
        _command_handler.register_exact(
            f"How much time {owner} spent on games",
            CountTimeCommand(),
        )
        _command_handler.register_exact(
            "Synchronize games to Steam", SyncSteamCommand()
        )
        _command_handler.register_prefix("getgame", GetGameCommand())
        _command_handler.register_substring("Steam Games List", SteamGameListCommand())
        _command_handler.register_substring(
            "Switch Games List", SwitchGameListCommand()
        )

        # Register file commands
        _command_handler.register_prefix("removefile", RemoveFileCommand())
        _command_handler.register_prefix("getfile", GetFileCommand())

        logger.info("Command handler initialized with all commands")

    return _command_handler


def _get_platforms() -> list[str]:
    """Get list of platforms from database with fallback to default.

    Returns:
        List of platform names
    """
    try:
        platforms = game_service.get_platforms()
        return platforms if platforms else DEFAULT_PLATFORMS
    except DatabaseError as e:
        # Domain exception from service layer - log and use defaults
        logger.warning(
            "Failed to load platforms from database: %s, using defaults",
            str(e),
            exc_info=True,
        )
        return DEFAULT_PLATFORMS
    except GameDBError as e:
        # Other domain exceptions (e.g., SQLFileNotFoundError) - log and use defaults
        logger.warning(
            "Failed to load platforms: %s, using defaults",
            str(e),
            exc_info=True,
        )
        return DEFAULT_PLATFORMS


def handle_start_help(message: Message, bot: telebot.TeleBot, sec: Security) -> None:
    """Handle /start and /help commands."""
    user_id = message.chat.id if message.chat else None
    if not sec.user_check(message.chat.id):
        logger.warning(
            "[UNAUTHORIZED_ACCESS] Unauthorized user %s tried to use /start command",
            user_id,
        )
        bot.send_message(message.chat.id, texts.PRIVATE_BOT_TEXT)
        return
    logger.info(
        "[USER_ACCESS] Authorized user %s accessed /start command",
        user_id,
    )
    bot.send_message(
        message.chat.id,
        texts.MAIN_MENU,
        reply_markup=InlineMenu.main_menu(sec, message.chat.id),
    )


def _handle_clear_menu(message: Message, bot: telebot.TeleBot, _sec: Security) -> None:
    """Handle clear menu command."""
    if not message.from_user:
        return
    bot.send_message(
        message.from_user.id,
        texts.MENU_CLEARED,
        reply_markup=menu.BotMenu.clear_menu(),
    )


def _handle_main_menu(message: Message, bot: telebot.TeleBot, sec: Security) -> None:
    """Handle main menu command."""
    if not message.from_user:
        return
    bot.send_message(
        message.from_user.id,
        texts.MAIN_MENU,
        reply_markup=menu.BotMenu.main_menu(message, sec),
    )


def _handle_file_menu(message: Message, bot: telebot.TeleBot, sec: Security) -> None:
    """Handle file menu command."""
    bot.send_message(
        message.chat.id,
        texts.FILE_MENU,
        reply_markup=menu.BotMenu.file_menu(message, sec),
    )


def _handle_game_lists_menu(
    message: Message, bot: telebot.TeleBot, _sec: Security
) -> None:
    """Handle game lists menu command."""
    from .config import load_settings_config

    settings = load_settings_config()
    bot.send_message(
        message.chat.id,
        texts.GAME_LISTS_MENU,
        reply_markup=menu.BotMenu.next_game(message, settings.owner_name),
    )


def _handle_show_commands(
    message: Message, bot: telebot.TeleBot, sec: Security
) -> None:
    """Handle show commands command."""
    bot.send_message(
        message.chat.id,
        texts.USER_COMMANDS_HELP,
        reply_markup=menu.BotMenu.main_menu(message, sec),
    )


def _handle_show_admin_commands(
    message: Message, bot: telebot.TeleBot, sec: Security
) -> None:
    """Handle show admin commands command."""
    user_id = message.chat.id if message.chat else None
    if sec.admin_check(message.chat.id):
        logger.info(
            "[USER_ACCESS] Admin user %s accessed admin commands",
            user_id,
        )
        bot.send_message(
            message.chat.id,
            texts.ADMIN_COMMANDS_HELP,
            reply_markup=InlineMenu.main_menu(sec, message.chat.id),
        )
    else:
        logger.warning(
            "[UNAUTHORIZED_ACCESS] Non-admin user %s tried to access admin commands",
            user_id,
        )
        bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)


def _handle_sync_steam(
    message: Message,
    bot: telebot.TeleBot,
    sec: Security,
    settings: SettingsConfig,
) -> None:
    """Handle Steam synchronization command."""
    user_id = message.chat.id if message.chat else None
    if not sec.admin_check(message.chat.id):
        logger.warning(
            "[UNAUTHORIZED_ACCESS] Non-admin user %s tried to sync Steam games",
            user_id,
        )
        bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
        return

    backup_excel = settings.paths.games_excel_file
    update_excel = settings.paths.update_db_dir / "games.xlsx"

    logger.info(
        "[STEAM_SYNC] User %s initiated Steam synchronization",
        user_id,
    )

    try:
        if not backup_excel.exists():
            logger.warning(
                "[STEAM_SYNC] Backup Excel file not found: %s (user: %s)",
                backup_excel,
                user_id,
            )
            bot.send_message(message.chat.id, texts.STEAM_SYNC_FILE_NOT_FOUND)
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
            logger.info(
                "[STEAM_SYNC] Steam synchronization completed successfully "
                "(user: %s, file: %s)",
                user_id,
                update_excel,
            )
            bot.send_message(message.chat.id, texts.STEAM_SYNC_SUCCESS)
        else:
            logger.error(
                "[STEAM_SYNC] Steam synchronization failed " "(user: %s, file: %s)",
                user_id,
                update_excel,
                exc_info=True,
            )
            bot.send_message(message.chat.id, texts.STEAM_SYNC_ERROR)
    except OSError:
        logger.error(
            "[STEAM_SYNC] Filesystem error during Steam sync (user: %s)",
            user_id,
            exc_info=True,
        )
        bot.send_message(message.chat.id, texts.STEAM_SYNC_FILESYSTEM_ERROR)


def _handle_steam_game_list(
    message: Message, bot: telebot.TeleBot, _sec: Security, settings: SettingsConfig
) -> None:
    """Handle Steam game list command."""
    if not message.from_user:
        return
    next_list = game_list(message, "Steam")
    bot.send_message(
        message.from_user.id,
        next_list[1],
        reply_markup=menu.BotMenu.next_game(next_list[0], settings.owner_name),
    )


def _handle_switch_game_list(
    message: Message, bot: telebot.TeleBot, _sec: Security, settings: SettingsConfig
) -> None:
    """Handle Switch game list command."""
    if not message.from_user:
        return
    next_list = game_list(message, "Switch")
    bot.send_message(
        message.from_user.id,
        next_list[1],
        reply_markup=menu.BotMenu.next_game(next_list[0], settings.owner_name),
    )


def handle_text(
    message: Message,
    bot: telebot.TeleBot,
    sec: Security,
    settings: SettingsConfig,
) -> None:
    """Main text handler for the bot using Command Pattern."""
    user_id = message.chat.id if message.chat else None
    if not sec.user_check(message.chat.id):
        logger.warning(
            "[UNAUTHORIZED_ACCESS] Unauthorized user %s tried to access the bot",
            user_id,
        )
        bot.send_message(message.chat.id, texts.PRIVATE_BOT_TEXT)
        return

    # Use command handler to execute commands
    command_handler = _get_command_handler(settings.owner_name)
    if command_handler.execute(message, bot, sec, settings):
        return

    # Default: show available actions if no command matched
    bot.send_message(
        message.chat.id,
        texts.MAIN_MENU,
        reply_markup=InlineMenu.main_menu(sec, message.chat.id),
    )


def _handle_get_game(message: Message, bot: telebot.TeleBot, sec: Security) -> None:
    """Handle getgame command - query and format game information."""
    if not message.text:
        return
    if not message.from_user:
        return

    try:
        get_from_db = game_service.query_game(message.text)
    except DatabaseError as e:
        logger.error(
            "Database error querying game '%s': %s",
            message.text,
            str(e),
            exc_info=True,
        )
        bot.send_message(
            message.from_user.id,
            texts.GAME_QUERY_ERROR,
            reply_markup=InlineMenu.main_menu(sec, message.from_user.id),
        )
        return

    formatter = MessageFormatter()

    if len(get_from_db) > 1 and message.text[-1] != "#":
        game_db = formatter.format_multiple_games(get_from_db)
    elif message.text[-1] == "#":
        name = message.text.replace("getgame ", "").replace("#", "")
        game_db = texts.GAME_QUERY_ERROR
        for row in get_from_db:
            if row[0].lower() == name.lower():
                game_db = formatter.format_game_info(row)
                break
    elif len(get_from_db) < 1:
        game_db = texts.GAME_NOT_FOUND
    else:
        game_db = formatter.format_game_info(get_from_db[0])

        bot.send_message(
            message.from_user.id,
            game_db,
            reply_markup=InlineMenu.main_menu(sec, message.from_user.id),
        )


def _handle_remove_file(
    message: Message,
    bot: telebot.TeleBot,
    sec: Security,
    settings: SettingsConfig,
) -> None:
    """Handle removefile command - safely delete a file."""
    user_id = message.chat.id if message.chat else None
    if not sec.admin_check(message.chat.id):
        logger.warning(
            "[UNAUTHORIZED_ACCESS] Non-admin user %s tried to remove file",
            user_id,
        )
        bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
        return

    if not message.text:
        return
    file_name = message.text.replace("removefile ", "").strip()

    logger.info(
        "[FILE_DELETION] User %s requested file deletion: %s",
        user_id,
        file_name,
    )

    # Validate file name to prevent path traversal attacks
    if not validate_file_name(file_name):
        logger.warning(
            "[FILE_DELETION] Invalid file name provided by user %s: %s",
            user_id,
            file_name,
        )
        bot.send_message(
            message.chat.id,
            "Invalid file name",
            reply_markup=menu.BotMenu.file_menu(message, sec),
        )
        return

    target_path = settings.paths.files_dir / file_name

    # Use safe file deletion with path validation
    if safe_delete_file(target_path, settings.paths.files_dir):
        logger.info(
            "[FILE_DELETION] File deleted successfully " "(user: %s, file: %s)",
            user_id,
            target_path,
        )
        bot.send_message(
            message.chat.id,
            texts.FILE_DELETED,
            reply_markup=menu.BotMenu.file_menu(message, sec),
        )
    else:
        logger.warning(
            "[FILE_DELETION] Failed to delete file: %s (user: %s)",
            target_path,
            user_id,
            exc_info=True,
        )
        bot.send_message(
            message.chat.id,
            "Failed to delete file",
            reply_markup=menu.BotMenu.file_menu(message, sec),
        )


def _handle_get_file(
    message: Message,
    bot: telebot.TeleBot,
    sec: Security,
    settings: SettingsConfig,
) -> None:
    """Handle getfile command - safely retrieve a file."""
    if not sec.admin_check(message.chat.id):
        bot.send_message(message.chat.id, texts.NICE_TRY_TEXT)
        return

    if not message.text:
        return
    file_name = message.text.replace("getfile ", "").strip()

    # Validate file name to prevent path traversal attacks
    if not validate_file_name(file_name):
        logger.warning(
            "Invalid file name provided by user %s: %s",
            message.chat.id,
            file_name,
        )
        bot.send_message(
            message.chat.id,
            "Invalid file name",
            reply_markup=menu.BotMenu.file_menu(message, sec),
        )
        return

    target_path = settings.paths.files_dir / file_name

    # Check if path is safe (within allowed directory)
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
                reply_markup=menu.BotMenu.file_menu(message, sec),
            )
    else:
        bot.send_message(message.chat.id, texts.FILE_NOT_FOUND)


def _handle_count_games(
    message: Message,
    bot: telebot.TeleBot,
    platforms: list[str],
    settings: SettingsConfig,
) -> None:
    """Handle count games command - format completed games statistics."""
    platform_counts = {}
    for platform in platforms:
        try:
            platform_counts[platform] = game_service.count_complete_games(platform)
        except DatabaseError as e:
            logger.error(
                "Database error counting games for platform '%s': %s",
                platform,
                str(e),
                exc_info=True,
            )
            platform_counts[platform] = 0

    formatter = MessageFormatter()
    count_complete_text = formatter.format_completed_games_stats(
        platform_counts, settings.owner_name
    )
    if not message.from_user:
        return
    bot.send_message(
        message.from_user.id,
        count_complete_text,
        reply_markup=menu.BotMenu.next_game(message, settings.owner_name),
    )


def _handle_count_time(
    message: Message,
    bot: telebot.TeleBot,
    platforms: list[str],
    settings: SettingsConfig,
) -> None:
    """Handle count time command - format time statistics."""
    # Collect time data for completed games
    platform_times = {}
    for platform in platforms:
        try:
            expected, real = game_service.count_spend_time(platform, 0)
            platform_times[platform] = (expected, real)
        except DatabaseError as e:
            logger.error(
                "Database error counting time for platform '%s': %s",
                platform,
                str(e),
                exc_info=True,
            )
            platform_times[platform] = (None, None)

    # Calculate total real time by summing real_time from all platforms
    # real_time is in hours, so we convert to seconds for format_time_stats
    total_real_hours = 0.0
    for platform, (expected, real) in platform_times.items():
        if real is not None:
            total_real_hours += real

    # Convert hours to seconds for format_time_stats
    total_real_seconds = total_real_hours * 3600

    formatter = MessageFormatter()
    # For overall statistics, show total line
    count_complete_text = formatter.format_time_stats(
        platform_times, total_real_seconds, settings.owner_name, show_total=True
    )

    if not message.from_user:
        return
    bot.send_message(
        message.from_user.id,
        count_complete_text,
        reply_markup=menu.BotMenu.next_game(message, settings.owner_name),
    )


def handle_file_upload(
    message: Message,
    bot: telebot.TeleBot,
    sec: Security,
    settings: SettingsConfig,
) -> None:
    """Handle file uploads from admin users."""
    user_id = message.chat.id if message.chat else None
    if not sec.admin_check(message.chat.id):
        logger.warning(
            "[UNAUTHORIZED_ACCESS] Non-admin user %s tried to upload a file",
            user_id,
        )
        bot.send_message(
            message.chat.id,
            texts.PERMISSION_DENIED_TEXT,
            reply_markup=InlineMenu.main_menu(sec, message.chat.id),
        )
        return

    if not message.document or not message.document.file_name:
        logger.warning(
            "[FILE_UPLOAD] User %s uploaded file without document or file_name",
            user_id,
        )
        bot.send_message(
            message.chat.id,
            "Error: file does not contain a name",
            reply_markup=InlineMenu.main_menu(sec, message.chat.id),
        )
        return

    file_name = message.document.file_name

    # Validate file name to prevent path traversal attacks
    if not validate_file_name(file_name):
        logger.warning(
            "Invalid file name provided by user %s: %s",
            message.chat.id,
            file_name,
        )
        bot.send_message(
            message.chat.id,
            "Invalid file name",
            reply_markup=InlineMenu.main_menu(sec, message.chat.id),
        )
        return

    logger.info(
        "[FILE_UPLOAD] User %s uploading file: %s",
        user_id,
        file_name,
    )

    # Check file type for non-Excel files
    if file_name != "games.xlsx":
        if not is_file_type_allowed(file_name):
            logger.warning(
                "[FILE_UPLOAD] User %s tried to upload file with disallowed extension: %s",
                user_id,
                file_name,
            )
            bot.send_message(
                message.chat.id,
                "File type not allowed",
                reply_markup=InlineMenu.main_menu(sec, message.chat.id),
            )
            return

    if not message.document or not message.document.file_id:
        return
    try:
        file_info = bot.get_file(message.document.file_id)
        if not file_info.file_path:
            return
        downloaded_file = bot.download_file(file_info.file_path)
    except Exception as e:
        # Telegram API can raise various exceptions (telebot.apihelper.ApiTelegramException, etc.)
        # Catch all to provide user-friendly error message
        logger.error(
            "[FILE_UPLOAD] Failed to download file '%s' from user %s: %s",
            file_name,
            user_id,
            str(e),
            exc_info=True,
        )
        bot.send_message(
            message.chat.id,
            "Error uploading file",
            reply_markup=InlineMenu.main_menu(sec, message.chat.id),
        )
        return

    update_db_dir = settings.paths.update_db_dir
    files_dir = settings.paths.files_dir

    # Determine target path based on file name
    if file_name == "games.xlsx":
        target_path = update_db_dir / file_name
        # Ensure target is within allowed directory
        if not is_path_safe(target_path, update_db_dir):
            logger.error(
                "[FILE_UPLOAD] Path traversal attempt detected " "(user: %s, path: %s)",
                user_id,
                target_path,
                exc_info=True,
            )
            bot.send_message(
                message.chat.id,
                texts.PERMISSION_DENIED_TEXT,
                reply_markup=InlineMenu.main_menu(sec, message.chat.id),
            )
            return
    else:
        target_path = files_dir / file_name
        # Ensure target is within allowed directory
        if not is_path_safe(target_path, files_dir):
            logger.error(
                "[FILE_UPLOAD] Path traversal attempt detected " "(user: %s, path: %s)",
                user_id,
                target_path,
                exc_info=True,
            )
            bot.send_message(
                message.chat.id,
                texts.PERMISSION_DENIED_TEXT,
                reply_markup=InlineMenu.main_menu(sec, message.chat.id),
            )
            return

    try:
        with open(target_path, "wb") as new_file:
            new_file.write(downloaded_file)
        logger.info(
            "[FILE_UPLOAD] Successfully saved uploaded file " "(user: %s, file: %s)",
            user_id,
            target_path,
        )
    except OSError as e:
        logger.error(
            "[FILE_UPLOAD] Failed to save uploaded file " "(user: %s, file: %s): %s",
            user_id,
            target_path,
            str(e),
            exc_info=True,
        )
        bot.send_message(
            message.chat.id,
            "Error saving file",
            reply_markup=InlineMenu.main_menu(sec, message.chat.id),
        )
        return

    # Process Excel files for database updates
    if file_name == "games.xlsx":
        update_db(message, "recreate", bot, sec, settings)

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        # Telegram API can raise various exceptions when deleting messages
        # This is non-critical, so we just log and continue
        logger.warning(
            "Failed to delete uploaded message: %s",
            str(e),
        )


def game_list(message: Message, platform: str) -> tuple[Message, str]:
    """Return list of next games for a given platform.

    Returns:
        Tuple of (updated_message, formatted_game_list_string)
    """
    if not message.text:
        return (message, "")
    message_text: list[str] = []
    for part in message.text.split(","):
        message_text.append(part)
    if len(message_text) < 3:
        return (message, "")
    try:
        next_game_list = game_service.get_next_game_list(
            int(message_text[1]), int(message_text[2]), platform
        )
    except DatabaseError as e:
        logger.error(
            "Database error getting game list for platform '%s': %s",
            platform,
            str(e),
            exc_info=True,
        )
        return (message, texts.GAME_QUERY_ERROR)

    formatter = MessageFormatter()
    platform_game_list = formatter.format_game_list(next_game_list)
    message.text = f"{platform},{int(message_text[1]) + 10},{int(message_text[2])}"
    return (message, platform_game_list)


def update_db(
    message: Message,
    mode: str,
    bot: telebot.TeleBot,
    sec: Security,
    settings: SettingsConfig,
) -> None:
    """Update database based on uploaded Excel file."""
    user_id = message.chat.id if message.chat else None
    if sec.admin_check(message.chat.id):
        if not message.document or not message.document.file_name:
            return
        update_path = settings.paths.update_db_dir / message.document.file_name
        if update_path.is_file():
            db = db_module.ChangeDB()
            if mode == "recreate":
                logger.info(
                    "[DB_RECREATION] User %s initiated database recreation from file: %s",
                    user_id,
                    update_path,
                )
                if db.recreate_db(str(update_path)):
                    logger.info(
                        "[DB_RECREATION] Database recreation completed successfully "
                        "(user: %s, file: %s)",
                        user_id,
                        update_path,
                    )
                    bot.send_message(
                        message.chat.id,
                        texts.DB_RECREATED,
                        reply_markup=InlineMenu.main_menu(sec, message.chat.id),
                    )
                else:
                    logger.error(
                        "[DB_RECREATION] Database recreation failed "
                        "(user: %s, file: %s)",
                        user_id,
                        update_path,
                        exc_info=True,
                    )
                    bot.send_message(
                        message.chat.id,
                        texts.DB_RECREATE_ERROR,
                        reply_markup=InlineMenu.main_menu(sec, message.chat.id),
                    )
            backup_path = settings.paths.backup_dir / "games.xlsx"
            update_path.replace(backup_path)
        else:
            bot.send_message(
                message.chat.id,
                f"File {message.document.file_name} not found",
                reply_markup=InlineMenu.main_menu(sec, message.chat.id),
            )
    else:
        logger.warning(
            "Non-admin user %s tried to update DB via file upload",
            message.chat.id,
        )
        bot.send_message(
            message.chat.id,
            texts.PERMISSION_DENIED_TEXT,
            reply_markup=InlineMenu.main_menu(sec, message.chat.id),
        )
