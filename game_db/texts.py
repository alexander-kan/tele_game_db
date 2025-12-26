"""Text constants for Telegram bot messages (for easier localization)."""

USER_COMMANDS_HELP = (
    "1) getgame:\n"
    'Enter "getgame" followed by a space and any part of the game name.'
)

ADMIN_COMMANDS_HELP = (
    "1) removefile:\n"
    'Enter "removefile" followed by a space and the exact file name '
    "to delete it from the files folder\n"
    "2) getfile:\n"
    'Enter "getfile" followed by a space and the exact file name (with '
    "extension) to get it from the files folder\n"
    "3) Upload files with names:\n"
    "games.xlsx - to recreate the database"
)

PRIVATE_BOT_TEXT = "Sorry, this is private bot of @HailToTheKan"

PERMISSION_DENIED_TEXT = "permission denied"

NICE_TRY_TEXT = "Nice try"

# Menu texts
MENU_CLEARED = "Menu cleared"
MAIN_MENU = "Main Menu"
FILE_MENU = "File Management Menu"
GAME_LISTS_MENU = "Game Lists Menu"
AVAILABLE_ACTIONS = "Available Actions"

# File operation texts
FILE_DELETED = "File deleted"
FILE_NOT_FOUND = "File not found"

# Game query texts
GAME_QUERY_ERROR = "Something went wrong"
GAME_NOT_FOUND = "Sorry - no matches found in the database"

# Steam sync texts
STEAM_SYNC_SUCCESS = "synchronized"
STEAM_SYNC_ERROR = "Something is going wrong"
STEAM_SYNC_FILE_NOT_FOUND = (
    "Source file games.xlsx not found for synchronization"
)
STEAM_SYNC_FILESYSTEM_ERROR = (
    "Filesystem error during synchronization"
)
STEAM_SYNC_ALL_UNIQUE = (
    "Research was conducted using the Damerau-Levenshtein mathematical algorithm "
    "and all values are unique."
)

# Metacritic sync texts
METACRITIC_SYNC_SUCCESS = "Metacritic sync completed"
METACRITIC_SYNC_ERROR = "Error during Metacritic synchronization"
METACRITIC_SYNC_NO_DATA = "No data to sync"
METACRITIC_SYNC_FILE_NOT_FOUND = (
    "Source file games.xlsx not found for synchronization"
)
METACRITIC_SYNC_FILESYSTEM_ERROR = (
    "Filesystem error during synchronization"
)

# HowLongToBeat sync texts
HLTB_SYNC_SUCCESS = "HowLongToBeat sync completed"
HLTB_SYNC_ERROR = "Error during HowLongToBeat synchronization"
HLTB_SYNC_NO_DATA = "No data to sync"
HLTB_SYNC_FILE_NOT_FOUND = (
    "Source file games.xlsx not found for synchronization"
)
HLTB_SYNC_FILESYSTEM_ERROR = (
    "Filesystem error during synchronization"
)

# Database update texts
DB_RECREATED = "Database recreated"
DB_RECREATE_ERROR = (
    "Database was not recreated due to an internal error, "
    "please contact @HailToTheKan"
)
GAME_UPDATED = "Game updated"
GAME_UPDATE_ERROR = (
    "Game was not updated due to an internal error, "
    "please contact @HailToTheKan"
)
GAMES_ADDED = "Games added"
GAMES_ADD_ERROR = (
    "Games were not added due to an internal error, "
    "please contact @HailToTheKan"
)

# Game info formatting texts
GAME_TIME_IS_NONE = "not specified"
GAME_NEVER_PLAYED = "never played"
GAME_HAVE_NEXT_GAME = "There are more games, continue browsing."
GAME_IN_DB = "Game in database"
