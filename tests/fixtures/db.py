"""Database fixtures for testing."""

from __future__ import annotations

import sqlite3
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def temp_db() -> Iterator[Path]:
    """Create a temporary SQLite database with test data.

    Yields:
        Path to temporary database file
    """
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = Path(db_file.name)
    db_file.close()

    # Create minimal schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        """
        CREATE TABLE status_dictionary (
            status_dictionary_id INTEGER PRIMARY KEY,
            status_name TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE platform_dictionary (
            platform_dictionary_id INTEGER PRIMARY KEY,
            platform_name TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE games (
            game_id TEXT PRIMARY KEY,
            game_name TEXT,
            status INTEGER,
            release_date TEXT,
            press_score TEXT,
            user_score TEXT,
            my_score TEXT,
            metacritic_url TEXT,
            trailer_url TEXT,
            average_time_beat TEXT,
            my_time_beat TEXT,
            last_launch_date TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE games_on_platforms (
            platform_id INTEGER,
            reference_game_id TEXT,
            FOREIGN KEY (platform_id) REFERENCES
                platform_dictionary(platform_dictionary_id),
            FOREIGN KEY (reference_game_id) REFERENCES games(game_id)
        )
        """
    )

    # Insert test data
    cursor.execute(
        (
            "INSERT INTO status_dictionary "
            "(status_dictionary_id, status_name) VALUES (1, 'Пройдена')"
        )
    )
    cursor.execute(
        (
            "INSERT INTO status_dictionary "
            "(status_dictionary_id, status_name) VALUES (2, 'Не начата')"
        )
    )
    cursor.execute(
        (
            "INSERT INTO platform_dictionary "
            "(platform_dictionary_id, platform_name) VALUES (2, 'Steam')"
        )
    )
    cursor.execute(
        (
            "INSERT INTO platform_dictionary "
            "(platform_dictionary_id, platform_name) VALUES (3, 'Switch')"
        )
    )

    # Insert test games
    cursor.execute(
        """
        INSERT INTO games (
            game_id, game_name, status, press_score,
            average_time_beat, my_time_beat
        )
        VALUES ('game1', 'Test Game 1', 1, '8', '10.5', '12.0')
        """
    )
    cursor.execute(
        """
        INSERT INTO games (
            game_id, game_name, status, press_score,
            average_time_beat, my_time_beat
        )
        VALUES ('game2', 'Test Game 2', 1, '9', '15.0', '18.5')
        """
    )
    cursor.execute(
        """
        INSERT INTO games (
            game_id, game_name, status, press_score,
            average_time_beat, my_time_beat
        )
        VALUES ('game3', 'Another Game', 2, '7', '20.0', NULL)
        """
    )

    cursor.execute(
        (
            "INSERT INTO games_on_platforms "
            "(platform_id, reference_game_id) VALUES (2, 'game1')"
        )
    )
    cursor.execute(
        (
            "INSERT INTO games_on_platforms "
            "(platform_id, reference_game_id) VALUES (2, 'game2')"
        )
    )
    cursor.execute(
        (
            "INSERT INTO games_on_platforms "
            "(platform_id, reference_game_id) VALUES (3, 'game3')"
        )
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    db_path.unlink(missing_ok=True)


@pytest.fixture
def empty_db() -> Iterator[Path]:
    """Create an empty temporary SQLite database.

    Yields:
        Path to temporary database file
    """
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = Path(db_file.name)
    db_file.close()

    # Create minimal schema only
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE platform_dictionary (
            platform_dictionary_id INTEGER PRIMARY KEY,
            platform_name TEXT
        )
        """
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    db_path.unlink(missing_ok=True)
