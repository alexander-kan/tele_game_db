# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-26
св
### Added

- **Metacritic synchronization** - Full and partial sync modes to update game data (release date, press score, user score, Metacritic URL) from Metacritic.com
- **HowLongToBeat synchronization** - Full and partial sync modes to update average completion times from HowLongToBeat.com
- **Inline keyboard menus** - Modern multi-level inline keyboard interface replacing reply keyboards
- **Callback query handlers** - Dedicated handlers for inline menu interactions with graceful error handling for expired queries
- **Steam data checking** - "Check Steam Data" feature to find games from Steam not in database with similarity matching
- **Add missing Steam games** - Ability to add missing Steam games to database with automatic field population
- **Similarity search** - Damerau-Levenshtein distance algorithm to find similar game names when exact matches aren't found
- **Dynamic dictionary generation** - Status and platform dictionaries now generated dynamically from `values_dictionaries.ini`
- **Dynamic DML generation** - SQL DML files (`dml_games.sql`, `dml_games_on_platforms.sql`) now generated dynamically from Excel on database recreation
- **Owner name configuration** - Configurable owner name in `settings/settings.ini` (defaults to "Alexander")
- **Database Sync menu** - Centralized menu for all synchronization operations (Steam, Metacritic, HowLongToBeat)
- **Test coverage** - Added tests for HowLongToBeat synchronizer, formatter, and DML generation
- **Screenshots** - Added comprehensive screenshots section to README.md
- **Author's note** - Added "About This Project" section explaining project motivation

### Changed

- **Menu system** - Complete refactoring from reply keyboards to inline keyboards with multi-level navigation
- **Message ordering** - Results now appear first, menu appears at the bottom for better UX
- **Status values** - Translated from Russian ("Пройдена", "Не начата", "Брошена") to English ("Completed", "Not Started", "Dropped")
- **All menus and messages** - Translated from Russian to English throughout the application
- **Test data** - All test files translated to English (headers, assertions, test data)
- **Excel headers** - Updated to match actual Excel file structure
- **Steam synchronization** - Enhanced with similarity matching and improved game addition logic
- **Expected time calculation** - Fixed to only sum `average_time_beat` for games that have been launched (have `my_time_beat`)
- **Date format** - Metacritic sync now uses "Month DD, YYYY" format in Excel (matching existing format)
- **Architecture diagram** - Updated to reflect current structure with inline menus, callback handlers, and all synchronizers
- **Repository name** - Updated from `game_db` to `tele_game_db` across all documentation and configuration

### Fixed

- **Database recreation** - DML files now properly regenerated from Excel on each database recreation
- **Metacritic sync** - Fixed to update all fields (release date, press score, user score) in both database and Excel
- **Date parsing** - Fixed cross-platform date parsing issue (macOS compatibility)
- **Callback query expiration** - Added graceful handling for expired Telegram callback queries
- **Excel row finding** - Steam sync now correctly finds first empty row when adding games
- **Game launch detection** - Improved logic to detect if game was launched and apply appropriate update logic

### Removed

- **genres.py** - Removed Metacritic genres extraction utility (no longer used in bot menu)
- **suffix() function** - Removed Russian suffix function from `utils.py` (not used)
- **Russian text normalization** - Removed ё→е replacement from `normalize_string()` (games are Latin-only)
- **new_games and update_games sheets** - Removed deprecated Excel sheet functionality

### Architecture

- **Telegram Bot Layer**: Added `callback_handlers.py`, `inline_menu.py`, `menu_callbacks.py` for inline menu support
- **Service Layer**: Added `synchronize_metacritic_games()` and `synchronize_hltb_games()` methods
- **Data Layer**: Added `MetacriticSynchronizer`, `HowLongToBeatSynchronizer`, `MetaCriticScraper`, `metacritic_search`, `HowLongToBeatClient`, `similarity_search`
- **Excel Formatters**: Added `MetacriticExcelFormatter` and `HowLongToBeatExcelFormatter`

### Dependencies

- Added `howlongtobeatpy ^1.0.19` for HowLongToBeat.com integration
- Added `pyxdameraulevenshtein ^1.7.0` for similarity search

### Documentation

- Updated README.md with comprehensive synchronization documentation
- Added screenshots section with placeholders for all menu screens
- Added "About This Project" section with author's motivation
- Updated architecture diagram and component overview
- Updated all menu references to English

## [0.1.0] - 2025-12-16

### Added

- Initial release of game-db project
- Telegram bot for managing personal video games database
- SQLite database integration with Excel import/export
- Steam Web API integration for playtime synchronization
- Metacritic parser for genre extraction
- User authentication and admin access control
- Comprehensive test suite (22 tests covering unit and integration scenarios)
- Repository pattern for database queries
- Service layer with message formatting
- Dependency injection for testability
- Poetry-based dependency management
- Code quality tools (black, isort, flake8, mypy)

### Architecture

- **Telegram Bot Layer**: `bot.py`, `handlers.py`, `menu.py`, `texts.py`
- **Service Layer**: `game_service.py`, `message_formatter.py`
- **Repository Layer**: `game_repository.py` with SQL queries in separate files
- **Data Layer**: `db.py` (facade), `db_excel.py`, `db_dictionaries.py`, `steam_api.py`
- **Storage**: SQLite database and Excel files

### Features

- Search games by name
- View game lists by platform
- Statistics about completed games and play time
- File management for admins
- Steam playtime synchronization
- Excel-based game data management

### Testing

- Unit tests for utility functions
- Integration tests for game service and repository
- Integration tests for Steam synchronizer with mocked dependencies
- Integration tests for Telegram bot handlers

### Documentation

- Comprehensive README with Quick Start guide
- Architecture diagram
- Test documentation
- Contributing guidelines
- Code of Conduct
