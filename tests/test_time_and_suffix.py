"""Unit tests for time formatting helpers."""

from __future__ import annotations

import pathlib
import sys

from game_db.utils import float_to_time

# Ensure project root is on sys.path when running tests directly
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_float_to_time_zero() -> None:
    """Test float_to_time with zero values."""
    assert float_to_time(0) == "0 hours 0 minutes"
    assert float_to_time(0.0) == "0 hours 0 minutes"
    assert float_to_time("0") == "0 hours 0 minutes"
    assert float_to_time("0.0") == "0 hours 0 minutes"


def test_float_to_time_zero_minutes() -> None:
    """Test float_to_time with whole hours (no minutes)."""
    assert float_to_time(1.0) == "1 hours 0 minutes"
    assert float_to_time(10.0) == "10 hours 0 minutes"
    assert float_to_time("5.0") == "5 hours 0 minutes"


def test_float_to_time_with_minutes() -> None:
    """Test float_to_time with fractional hours."""
    # 1.5 hours = 1 hour 30 minutes
    assert float_to_time(1.5) == "1 hours 30 minutes"
    # 2.25 hours = 2 hours 15 minutes
    assert float_to_time(2.25) == "2 hours 15 minutes"
    # 10.75 hours = 10 hours 45 minutes
    assert float_to_time(10.75) == "10 hours 45 minutes"
    # 0.5 hours = 0 hours 30 minutes
    assert float_to_time(0.5) == "0 hours 30 minutes"


def test_float_to_time_string_input() -> None:
    """Test float_to_time with string inputs."""
    assert float_to_time("1.5") == "1 hours 30 minutes"
    assert float_to_time("2.25") == "2 hours 15 minutes"
    assert float_to_time("10.75") == "10 hours 45 minutes"
    assert float_to_time("100.33") == "100 hours 19 minutes"


def test_float_to_time_large_numbers() -> None:
    """Test float_to_time with large numbers."""
    # Very large hours
    assert float_to_time(1000.5) == "1000 hours 30 minutes"
    assert float_to_time(9999.25) == "9999 hours 15 minutes"
    # Large fractional part
    assert float_to_time(1.99) == "1 hours 59 minutes"


def test_float_to_time_edge_cases() -> None:
    """Test float_to_time with edge cases."""
    # Very small fractional part
    assert float_to_time(1.01) == "1 hours 0 minutes"  # 0.01 * 60 = 0.6, int = 0
    assert float_to_time(1.02) == "1 hours 1 minutes"  # 0.02 * 60 = 1.2, int = 1
    # Close to 59 minutes (59/60 = 0.983333...)
    # Using 59/60 for exact calculation
    assert float_to_time(1 + 59 / 60) == "1 hours 59 minutes"
    # Negative numbers (should be treated as 0)
    assert float_to_time(-1.5) == "0 hours 0 minutes"
    assert float_to_time(-10) == "0 hours 0 minutes"


def test_float_to_time_invalid_input() -> None:
    """Test float_to_time with invalid inputs (should default to 0)."""
    # Invalid strings should default to 0
    assert float_to_time("invalid") == "0 hours 0 minutes"
    assert float_to_time("abc") == "0 hours 0 minutes"
    assert float_to_time("") == "0 hours 0 minutes"
    # None should cause error, but we test with string "None"
    # (actual None would cause TypeError, which is acceptable)
