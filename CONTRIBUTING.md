## Contributing

Thank you for your interest in contributing to `game-db`!

### Development setup

- Install dependencies via Poetry:

  ```bash
  poetry install
  ```

- Run the Telegram bot locally:

  ```bash
  poetry run game-db-bot
  ```

### Code style and tests

Before opening a pull request, please make sure that:

```bash
# Run all tests with coverage (minimum 80% coverage required)
poetry run pytest --cov=game_db --cov-report=term-missing

# Code formatting
poetry run black game_db scripts tests
poetry run isort game_db scripts tests

# Linting
poetry run flake8 game_db scripts tests

# Type checking
poetry run mypy game_db
```

**Note:** All tests must pass and code coverage must be at least 80%. The CI pipeline will automatically check this when you open a pull request.

### Pull requests

- Keep changes focused and small when possible.
- Add tests for new functionality.
- Update documentation (`README.md`) if behavior or configuration changes.
