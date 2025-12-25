"""Text constants for Telegram bot messages (for easier localization)."""

USER_COMMANDS_HELP = (
    "1) getgame:\n"
    'Введи "getgame" затем, через пробел, любую часть названия игры.'
)

ADMIN_COMMANDS_HELP = (
    "1) removefile:\n"
    'Введи "removefile" затем, через пробел, точное название файла, '
    "для удаления его из папки files\n"
    "2) getfile:\n"
    'Введи "getfile" затем, через пробел, точное название файла(с '
    "расширением), для получения его из папки files\n"
    "3) Загрузить файлы с именами:\n"
    "games.xlsx - для переналивки базы\n"
    "update_games.xlsx - для обновления строк базы\n"
    "games_add_new.xlsx - для добавления новой игры"
)

PRIVATE_BOT_TEXT = "Sorry, this is private bot of @HailToTheKan"

PERMISSION_DENIED_TEXT = "permission denied"

NICE_TRY_TEXT = "Nice try"

# Menu texts
MENU_CLEARED = "Меню очищено"
MAIN_MENU = "Главное меню"
FILE_MENU = "Меню управления файлами"
GAME_LISTS_MENU = "Меню просмотра списков игр"
AVAILABLE_ACTIONS = "Доступные действия"

# File operation texts
FILE_DELETED = "файл удалён"
FILE_NOT_FOUND = "Файл не найден"

# Game query texts
GAME_QUERY_ERROR = "Что-то пошло не так"
GAME_NOT_FOUND = "Извиняй - совпадений в базе не найдено"

# Steam sync texts
STEAM_SYNC_SUCCESS = "synchronized"
STEAM_SYNC_ERROR = "Something is going wrong"
STEAM_SYNC_FILE_NOT_FOUND = (
    "Не найден исходный файл games.xlsx для синхронизации"
)
STEAM_SYNC_FILESYSTEM_ERROR = (
    "Ошибка файловой системы при синхронизации"
)
STEAM_SYNC_ALL_UNIQUE = (
    "Было проведено исследование по математическому алгоритму "
    "Дамерау–Левенштейна и все значения уникальны."
)

# Metacritic sync texts
METACRITIC_SYNC_SUCCESS = "Синхронизация Metacritic завершена"
METACRITIC_SYNC_ERROR = "Ошибка при синхронизации Metacritic"
METACRITIC_SYNC_NO_DATA = "Данных для синхронизации нет"
METACRITIC_SYNC_FILE_NOT_FOUND = (
    "Не найден исходный файл games.xlsx для синхронизации"
)
METACRITIC_SYNC_FILESYSTEM_ERROR = (
    "Ошибка файловой системы при синхронизации"
)

# HowLongToBeat sync texts
HLTB_SYNC_SUCCESS = "Синхронизация HowLongToBeat завершена"
HLTB_SYNC_ERROR = "Ошибка при синхронизации HowLongToBeat"
HLTB_SYNC_NO_DATA = "Данных для синхронизации нет"
HLTB_SYNC_FILE_NOT_FOUND = (
    "Не найден исходный файл games.xlsx для синхронизации"
)
HLTB_SYNC_FILESYSTEM_ERROR = (
    "Ошибка файловой системы при синхронизации"
)

# Database update texts
DB_RECREATED = "База пересоздана"
DB_RECREATE_ERROR = (
    "База не пересоздана из-за внутренней ошибки, "
    "обратитесь к @HailToTheKan"
)
GAME_UPDATED = "Игра обновлена"
GAME_UPDATE_ERROR = (
    "Игра не обновлена из-за внутренней ошибки, "
    "обратитесь к @HailToTheKan"
)
GAMES_ADDED = "Игры добавлены"
GAMES_ADD_ERROR = (
    "Игры не добавлены из-за внутренней ошибки, "
    "обратитесь к @HailToTheKan"
)

# Game info formatting texts
GAME_TIME_IS_NONE = "отсутствует"
GAME_NEVER_PLAYED = "не запускалась"
GAME_HAVE_NEXT_GAME = "Есть ещё игры, листай дальше."
GAME_IN_DB = "Игра в базе"
