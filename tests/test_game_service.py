"""Integration tests for game_service using GameRepository."""

# pylint: disable=redefined-outer-name

from __future__ import annotations

import pathlib
import sqlite3
import sys
from pathlib import Path

import pytest

from game_db.repositories.game_repository import GameRepository

# Ensure project root is on sys.path when running tests directly
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Fixture temp_db is now imported from conftest.py


def test_query_game_found(temp_db: Path) -> None:
    """Test query_game finds games by name."""
    repo = GameRepository(temp_db)
    results = repo.query_game("getgame Test")
    assert len(results) >= 1
    assert any("Test Game" in str(row[0]) for row in results)


def test_query_game_not_found(temp_db: Path) -> None:
    """Test query_game returns empty list for non-existent game."""
    repo = GameRepository(temp_db)
    results = repo.query_game("getgame NonExistentGame")
    assert len(results) == 0


def test_count_complete_games(temp_db: Path) -> None:
    """Test count_complete_games returns correct count."""
    repo = GameRepository(temp_db)
    count = repo.count_complete_games("Steam")
    assert count == 2  # game1 and game2 are completed on Steam
    count_switch = repo.count_complete_games("Switch")
    assert count_switch == 0  # game3 is not completed


def test_count_spend_time_completed(temp_db: Path) -> None:
    """Test count_spend_time for completed games."""
    repo = GameRepository(temp_db)
    expected, real = repo.count_spend_time("Steam", mode=0)
    # game1: 10.5 + 12.0, game2: 15.0 + 18.5
    assert expected is not None
    assert real is not None
    assert float(expected) == pytest.approx(25.5, abs=0.1)  # 10.5 + 15.0
    assert float(real) == pytest.approx(30.5, abs=0.1)  # 12.0 + 18.5


def test_get_next_game_list(temp_db: Path) -> None:
    """Test get_next_game_list returns games for platform."""
    repo = GameRepository(temp_db)
    results = repo.get_next_game_list(0, 10, "Switch")
    # game3 is not started and has press_score >= 7
    assert len(results) >= 1
    assert results[0][0] == "Another Game"


def test_get_platforms(temp_db: Path) -> None:
    """Test get_platforms returns list of platforms."""
    repo = GameRepository(temp_db)
    platforms = repo.get_platforms()
    assert isinstance(platforms, list)
    assert "Steam" in platforms
    assert "Switch" in platforms


def test_get_platforms_empty_db(tmp_path: Path) -> None:
    """Test get_platforms returns empty list for empty database."""
    import sqlite3

    # Create empty database
    db_path = tmp_path / "empty.db"
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

    repo = GameRepository(db_path)
    platforms = repo.get_platforms()
    assert platforms == []


def test_query_game_empty_string(temp_db: Path) -> None:
    """Test query_game handles empty string."""
    repo = GameRepository(temp_db)
    results = repo.query_game("getgame ")
    # Should return all games or handle gracefully
    assert isinstance(results, list)


def test_count_spend_time_all_games(temp_db: Path) -> None:
    """Test count_spend_time with mode=1 (all games)."""
    repo = GameRepository(temp_db)
    expected, real = repo.count_spend_time("Steam", mode=1)
    # Should return time for all games, not just completed
    assert expected is not None or real is not None


def test_repository_sql_caching(temp_db: Path) -> None:
    """Test that SQL queries are cached."""
    repo1 = GameRepository(temp_db)
    repo2 = GameRepository(temp_db)

    # Both should use cached SQL
    results1 = repo1.query_game("getgame Test")
    results2 = repo2.query_game("getgame Test")

    assert len(results1) == len(results2)
