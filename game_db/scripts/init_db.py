"""CLI wrapper to recreate the database from Excel.

This script provides a command-line interface for recreating the database
from an Excel file. It uses the DatabaseService for all database operations,
ensuring consistency with other entry points.
"""

from __future__ import annotations

import sys
from pathlib import Path

from game_db.config import load_settings_config, load_tokens_config
from game_db.logging_config import configure_logging
from game_db.services.database_service import DatabaseService


def main() -> None:
    """Recreate SQLite database from Excel file.

    The Excel file path can be provided as a command-line argument,
    or the default path from settings will be used.

    Usage:
        game-db-init [excel_file_path]
    """
    configure_logging()

    # Parse command-line arguments
    excel_file: Path | None = None
    if len(sys.argv) > 1:
        excel_file = Path(sys.argv[1])
        if not excel_file.exists():
            print(f"Error: Excel file not found: {excel_file}", file=sys.stderr)
            sys.exit(1)

    # Load configuration
    settings = load_settings_config()
    tokens = load_tokens_config()

    # Use default path if not provided
    if excel_file is None:
        excel_file = settings.paths.games_excel_file

    # Create service and execute operation
    service = DatabaseService(settings, tokens)
    success = service.recreate_db(excel_file)

    if not success:
        print("Error: Failed to recreate database", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
