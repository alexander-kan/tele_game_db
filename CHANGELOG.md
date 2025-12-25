# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
