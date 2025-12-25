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
poetry run pytest
poetry run black game_db scripts tests
poetry run isort game_db scripts tests
poetry run flake8 game_db scripts tests
poetry run mypy game_db
```

### Pull requests

- Keep changes focused and small when possible.
- Add tests for new functionality.
- Update documentation (`README.md`) if behavior or configuration changes.
