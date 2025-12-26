# Tests

This directory contains unit and integration tests for the game_db project.

## Test Structure

### Test Files
- `test_time_and_suffix.py` - Unit tests for utility functions (`float_to_time`)
- `test_file_safety.py` - Unit tests for file safety utilities (path validation, safe deletion, file type checking, OS error paths)
- `test_excel_importer_mappings.py` - Unit tests for ExcelImporter mapping logic (status/platform IDs, date formatting, spend time calculation)
- `test_dml_generation.py` - Unit tests for DML SQL file generation from Excel files (`generate_dml_games_sql`, `generate_dml_games_on_platforms_sql`)
- `test_excel_reader_writer.py` - Unit tests for Excel reader/writer helpers (sheet selection, row read/write, search by game name)
- `test_game_service.py` - Integration tests for `GameRepository` (database queries, statistics)
- `test_game_service_layer.py` - Unit tests for service layer (`game_service`) including success paths, error propagation and wrapping
- `test_steam_synchronizer.py` - Integration tests for `SteamSynchronizer` with mocked Steam API and Excel files
- `test_metacritic_synchronizer.py` - Integration tests for `MetacriticSynchronizer` with mocked Metacritic scraper and Excel files
- `test_metacritic_search.py` - Unit tests for Metacritic search functionality (`search_metacritic_game_url`)
- `test_metacritic_formatter.py` - Unit tests for Metacritic Excel formatter (`MetacriticExcelFormatter`)
- `test_hltb_synchronizer.py` - Integration tests for `HowLongToBeatSynchronizer` with mocked HowLongToBeat client and Excel files
- `test_hltb_formatter.py` - Unit tests for HowLongToBeat Excel formatter (`HowLongToBeatExcelFormatter`)
- `test_handlers.py` - Integration tests for Telegram bot handlers with mocked bot and dependencies (including DB update and Steam sync helpers)
- `test_file_commands.py` - Tests for file-related bot commands (`RemoveFileCommand`, `GetFileCommand`, `SyncSteamCommand`)
- `test_game_commands.py` - Tests for game-related bot commands (`GetGameCommand`, `CountGamesCommand`, `CountTimeCommand`, Steam/Switch lists)
- `test_bot.py` - Unit tests for `BotApplication` class with Dependency Injection
- `test_security.py` - Unit tests for security.py (user/admin checks, Singleton pattern)
- `test_config.py` - Unit tests for config.py (configuration loading, dataclasses)
- `test_message_formatter.py` - Unit tests for message_formatter.py
- `test_menu.py` - Unit tests for menu.py
- `test_db_dictionaries.py` - Unit tests for db_dictionaries.py
- `test_steam_api.py` - Unit tests for steam_api.py
- `test_error_handling.py` - Error handling tests for database, services, and edge cases
- `test_error_handling_formatters.py` - Error handling tests for formatters and validators
- `test_error_handling_handlers.py` - Error handling tests for handlers and commands
- `test_exceptions.py` - Unit tests for custom exception classes (DatabaseError, DatabaseQueryError, Game/Platform/SQL file not found)

### Shared Fixtures

Common test fixtures are organized in `fixtures/` directory and automatically available through `conftest.py`:

- `fixtures/db.py` - Database fixtures
  - `temp_db` - Temporary SQLite database with test data
  - `empty_db` - Empty temporary SQLite database
  
- `fixtures/excel.py` - Excel file fixtures
  - `temp_excel` - Temporary Excel file with test data
  - `empty_excel` - Empty temporary Excel file
  
- `fixtures/telegram.py` - Telegram bot fixtures
  - `mock_bot` - Mock Telegram bot
  - `mock_message` - Mock Telegram message
  - `mock_message_with_document` - Mock Telegram message with document
  - `admin_security` - Security instance for admin user
  - `user_security` - Security instance for regular user
  - `test_config` - SettingsConfig with test paths
  - `test_tokens` - TokensConfig with test tokens
  - `test_users` - UsersConfig with test users
  - `mock_steam_api` - Mock SteamAPI client
  - `bot_app` - BotApplication instance for testing

## Running Tests

### Basic Usage

```bash
# Run all tests (with coverage by default from pytest.ini)
poetry run pytest

# Run all tests without coverage (faster for quick checks)
poetry run pytest --no-cov

# Run specific test file
poetry run pytest tests/test_game_service.py

# Run specific test class
poetry run pytest tests/test_security.py::TestSecurity

# Run specific test function
poetry run pytest tests/test_handlers.py::test_handle_text_getgame

# Run with verbose output (already enabled by default in pytest.ini)
poetry run pytest -v
```

### Coverage Reports

```bash
# Run tests with coverage (default from pytest.ini)
poetry run pytest

# View HTML coverage report
open htmlcov/index.html

# View coverage in terminal with missing lines
poetry run pytest --cov=game_db --cov-report=term-missing

# Generate only HTML report
poetry run pytest --cov=game_db --cov-report=html

# Generate only XML report (for CI/CD)
poetry run pytest --cov=game_db --cov-report=xml
```

### Using Markers

```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run only end-to-end tests
poetry run pytest -m e2e

# Run only error handling tests
poetry run pytest -m error_handling

# Run tests excluding a marker
poetry run pytest -m "not integration"

# Run multiple markers
poetry run pytest -m "unit or integration"

# Run unit tests excluding error handling
poetry run pytest -m "unit and not error_handling"
```

### Test Discovery

```bash
# List all available tests without running them
poetry run pytest --collect-only

# List tests matching a pattern
poetry run pytest --collect-only -k "security"

# Show test markers
poetry run pytest --markers
```

### Debugging and Output

```bash
# Run with extra verbose output
poetry run pytest -vv

# Show print statements
poetry run pytest -s

# Stop on first failure
poetry run pytest -x

# Show local variables on failure
poetry run pytest -l

# Run last failed tests only
poetry run pytest --lf

# Run failed tests first
poetry run pytest --ff
```

### Performance

```bash
# Run tests in parallel (requires pytest-xdist)
poetry run pytest -n auto

# Show slowest tests
poetry run pytest --durations=10
```

## Test Dependencies

Tests use:
- `pytest` - Testing framework (^8.0.0)
- `unittest.mock` - For mocking dependencies (Steam API, Telegram bot, file operations)
- Temporary files/databases for integration tests (isolated test data)

## Test Patterns

- **Unit tests**: Test individual functions/classes in isolation
  - Example: `test_time_and_suffix.py` tests utility functions without external dependencies
  - Example: `test_file_safety.py` tests file safety utilities (path validation, safe deletion) with temporary directories

- **Integration tests**: Test components working together with mocked external dependencies
  - Example: `test_steam_synchronizer.py` tests Steam sync with mocked Steam API client
  - Example: `test_handlers.py` tests bot handlers with mocked Telegram bot

- **Fixtures**: Reusable test data organized in `fixtures/` directory
  - Database fixtures: `temp_db`, `empty_db` (from `fixtures/db.py`)
  - Excel fixtures: `temp_excel`, `empty_excel` (from `fixtures/excel.py`)
  - Telegram fixtures: `mock_bot`, `mock_message`, `admin_security`, `user_security`, etc. (from `fixtures/telegram.py`)
  - All fixtures are automatically available through `conftest.py`
  - Local fixtures: `temp_dir`, `allowed_dir` in `test_file_safety.py` for file operations

## Test Coverage

Current test suite covers:
- ✅ Utility functions (time formatting)
- ✅ File safety utilities (path validation, safe deletion, file type checking, OS and filesystem error paths)
- ✅ Excel reader/writer helpers (sheet selection, row reading/writing, row lookup)
- ✅ Excel importer mappings and data transformations (status/platform IDs, month/text round‑trip, spend time calculation)
- ✅ DML SQL file generation from Excel (games and games_on_platforms tables, date conversion, status/platform ID mapping, value formatting, validation)
- ✅ Game repository queries (search, statistics, lists)
- ✅ Service layer (`game_service`) including successful flows and error propagation/wrapping into `DatabaseError`
- ✅ Steam synchronizer with dependency injection
- ✅ Metacritic synchronizer with dependency injection
- ✅ HowLongToBeat synchronizer with dependency injection
- ✅ Metacritic search functionality
- ✅ Metacritic Excel formatter
- ✅ HowLongToBeat Excel formatter
- ✅ Telegram bot handlers (commands, routing, authorization, DB update flows, Steam sync flows, Metacritic sync flows)
- ✅ File commands (`removefile`, `getfile`, `sync_steam`) including security checks and filesystem errors
- ✅ Game commands (game search, counters, time statistics, next games lists)
- ✅ BotApplication class with Dependency Injection
- ✅ Security module (user/admin checks, Singleton pattern)
- ✅ Configuration module (centralized INI loading in `config.py`, `Paths`/`DBFilesConfig`/`SettingsConfig` dataclasses)
- ✅ Message formatter (game info, statistics formatting)
- ✅ Menu builder (keyboard generation)
- ✅ Database dictionaries builder
- ✅ Steam API client
- ✅ Metacritic scraper (`MetaCriticScraper`)
- ✅ Metacritic search (`search_metacritic_game_url`)
- ✅ Metacritic Excel formatter (release date parsing, score conversion)
- ✅ Error handling (database errors, missing data, invalid input, external API errors, edge cases, custom exception classes)

## Notes

- All tests use dependency injection for external services (Steam API, file operations)
- Tests are isolated and don't require real API keys or database files
- Temporary files are automatically cleaned up after tests
- File safety tests use temporary directories to test path validation and safe deletion
- Pylint warnings about `redefined-outer-name` are suppressed (standard pytest pattern)
- Config tests ensure that all INI files are read only in `config.py`, and the rest of the code works with typed configuration objects instead of raw `ConfigParser`

## Security Testing

The `test_file_safety.py` test suite specifically tests security features:
- **Path traversal protection**: Tests verify that paths outside allowed directories cannot be accessed
- **File name validation**: Tests check for dangerous characters, null bytes, and path traversal attempts
- **Safe deletion**: Tests ensure files can only be deleted within allowed directories
- **File type validation**: Tests verify that only allowed file extensions are accepted

## Error Handling Testing

The error handling test suite (`test_error_handling.py`, `test_error_handling_formatters.py`, `test_error_handling_handlers.py`) comprehensively tests error scenarios:

### Database Error Handling (`test_error_handling.py`)
- **Connection errors**: Tests database connection failures and error propagation
- **Query errors**: Tests SQL query execution failures and invalid SQL syntax
- **Missing SQL files**: Tests validation of required SQL files at repository initialization
- **Service layer wrapping**: Tests that generic exceptions are properly wrapped in `DatabaseError`

### Missing Data Handling (`test_error_handling.py`)
- **Empty results**: Tests handling of empty query results
- **Empty platforms**: Tests counting games for platforms with no data
- **Empty databases**: Tests operations on empty databases
- **Missing time data**: Tests handling of missing time tracking data

### Invalid Input Handling (`test_error_handling.py`)
- **Empty strings**: Tests handling of empty input strings
- **Special characters**: Tests SQL injection attempts and special character handling
- **Invalid platform names**: Tests handling of invalid platform names with special characters
- **Negative/zero values**: Tests handling of negative and zero parameter values
- **Very long strings**: Tests handling of extremely long input strings

### External API Error Handling (`test_error_handling.py`)
- **Steam API timeouts**: Tests handling of Steam API timeout errors
- **Steam API connection errors**: Tests handling of Steam API connection failures
- **Metacritic timeouts**: Tests handling of Metacritic parser timeout errors
- **Metacritic connection errors**: Tests handling of Metacritic parser connection failures

### Edge Cases (`test_error_handling.py`)
- **Very long game names**: Tests handling of extremely long game names (1000+ characters)
- **Large parameter values**: Tests handling of very large offset/limit values
- **Invalid mode values**: Tests handling of invalid mode parameters
- **Unicode characters**: Tests handling of Unicode characters in game names and platforms
- **Non-existent database paths**: Tests repository behavior with invalid database paths

### Formatter Error Handling (`test_error_handling_formatters.py`)
- **Missing fields**: Tests `MessageFormatter` handling of missing optional fields
- **Empty strings**: Tests formatting with empty string values
- **Empty lists**: Tests formatting of empty game lists
- **None values**: Tests handling of None values in game data
- **Excel validator errors**: Tests `ExcelValidator` handling of invalid status/platform names, empty strings, and None values

### Handler/Command Error Handling (`test_error_handling_handlers.py`)
- **Database errors in handlers**: Tests that handlers gracefully handle database errors
- **Empty search results**: Tests handling of "game not found" scenarios
- **Partial failures**: Tests handling when some platforms fail but others succeed
- **File download errors**: Tests handling of file download failures
- **Invalid file types**: Tests rejection of invalid file extensions
- **Path traversal prevention**: Tests that handlers prevent path traversal attacks
- **Command error handling**: Tests error handling in command classes (GetGameCommand, CountGamesCommand, etc.)

### Running Error Handling Tests

```bash
# Run all error handling tests
poetry run pytest tests/test_error_handling*.py

# Run only database error tests
poetry run pytest tests/test_error_handling.py::TestDatabaseErrorHandling

# Run only external API error tests
poetry run pytest tests/test_error_handling.py::TestExternalAPIErrorHandling

# Run only edge case tests
poetry run pytest tests/test_error_handling.py::TestEdgeCases

# Run with error handling marker (if using markers)
poetry run pytest -m error_handling
```

### Error Handling Test Patterns

- **Exception propagation**: Tests verify that custom exceptions (`DatabaseError`, `DatabaseQueryError`, etc.) are properly raised and propagated
- **Error wrapping**: Tests verify that generic exceptions are wrapped in domain-specific exceptions with context
- **Graceful degradation**: Tests verify that partial failures don't crash the application (e.g., one platform fails but others succeed)
- **User-friendly messages**: Tests verify that error messages are sent to users when appropriate
- **Logging**: Tests verify that errors are properly logged with context
