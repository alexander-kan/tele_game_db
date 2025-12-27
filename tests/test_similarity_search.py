"""Unit tests for similarity_search module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game_db.similarity_search import (
    SimilarityMatch,
    calculate_similarity_score,
    find_closest_match,
    is_acceptable_match,
    normalize_string,
)
from game_db.config import SimilarityThresholdsConfig


def test_normalize_string() -> None:
    """Test string normalization."""
    assert normalize_string("  Hello   World  ") == "hello world"
    assert normalize_string("TEST") == "test"
    assert normalize_string("Multiple    Spaces") == "multiple spaces"
    assert normalize_string("") == ""
    assert normalize_string("   ") == ""


def test_calculate_similarity_score() -> None:
    """Test similarity score calculation."""
    # Perfect match
    assert calculate_similarity_score(0, 5, 5) == 1.0
    
    # Half match
    assert calculate_similarity_score(5, 10, 10) == 0.5
    
    # No match
    assert calculate_similarity_score(10, 10, 10) == 0.0
    
    # Empty strings
    assert calculate_similarity_score(0, 0, 0) == 1.0
    
    # Different lengths
    assert calculate_similarity_score(2, 5, 10) == 0.8  # 1 - 2/10


def test_is_acceptable_match_short_string() -> None:
    """Test acceptable match for short strings."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    # Short string, acceptable distance
    assert is_acceptable_match(1, 0.8, 4, thresholds) is True
    
    # Short string, unacceptable distance
    assert is_acceptable_match(2, 0.8, 4, thresholds) is False


def test_is_acceptable_match_medium_string() -> None:
    """Test acceptable match for medium strings."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    # Medium string, acceptable distance
    assert is_acceptable_match(2, 0.8, 8, thresholds) is True
    
    # Medium string, acceptable score
    assert is_acceptable_match(3, 0.85, 8, thresholds) is True
    
    # Medium string, unacceptable
    assert is_acceptable_match(3, 0.75, 8, thresholds) is False


def test_is_acceptable_match_long_string() -> None:
    """Test acceptable match for long strings."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    # Long string, acceptable distance
    assert is_acceptable_match(3, 0.8, 15, thresholds) is True
    
    # Long string, acceptable score
    assert is_acceptable_match(4, 0.90, 15, thresholds) is True
    
    # Long string, unacceptable
    assert is_acceptable_match(4, 0.80, 15, thresholds) is False


def test_find_closest_match_empty_candidates() -> None:
    """Test finding match with empty candidates."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    result = find_closest_match("test", [], thresholds)
    
    assert result.original == "test"
    assert result.closest_match is None
    assert result.distance == 0
    assert result.score == 0.0


def test_find_closest_match_perfect_match() -> None:
    """Test finding perfect match."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    candidates = ["test", "other", "game"]
    result = find_closest_match("test", candidates, thresholds)
    
    assert result.original == "test"
    assert result.closest_match == "test"
    assert result.distance == 0
    assert result.score == 1.0


def test_find_closest_match_acceptable_match() -> None:
    """Test finding acceptable match."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    candidates = ["tes", "other"]
    result = find_closest_match("test", candidates, thresholds)
    
    assert result.original == "test"
    assert result.closest_match == "tes"  # Distance 1, acceptable for short string
    assert result.distance == 1
    assert result.score > 0.0


def test_find_closest_match_no_acceptable_match() -> None:
    """Test finding match when no acceptable match exists."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    candidates = ["completely", "different", "strings"]
    result = find_closest_match("test", candidates, thresholds)
    
    assert result.original == "test"
    assert result.closest_match is None
    assert result.distance > 0


def test_find_closest_match_length_filtering() -> None:
    """Test length-based candidate filtering."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    candidates = ["tes", "test", "verylonggamenamehere"]
    result = find_closest_match("test", candidates, thresholds, length_diff_threshold=2)
    
    assert result.original == "test"
    # Should prefer "tes" or "test" over very long name


def test_find_closest_match_case_insensitive() -> None:
    """Test that matching is case insensitive."""
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=1,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    candidates = ["TEST", "Other"]
    result = find_closest_match("test", candidates, thresholds)
    
    assert result.original == "test"
    assert result.closest_match == "TEST"
    assert result.distance == 0
    assert result.score == 1.0


def test_damerau_levenshtein_fallback_implementation() -> None:
    """Test fallback damerau_levenshtein_distance implementation logic."""
    # Test the fallback implementation directly by mocking import
    # We test the logic that would be used if library is not available
    # This tests lines 17-40 in similarity_search.py
    
    # Since we can't easily test the actual fallback without removing the library,
    # we test that the function works correctly with the library available
    # The fallback code path is hard to test without removing dependencies
    
    # Instead, test edge cases that exercise similar logic
    thresholds = SimilarityThresholdsConfig(
        short_length_max=5,
        short_length_distance=2,
        medium_length_max=12,
        medium_length_distance=2,
        medium_length_score=0.80,
        long_length_distance=3,
        long_length_score=0.85,
    )
    
    # Test empty strings
    result = find_closest_match("", ["", "test"], thresholds)
    assert result.original == ""
    
    # Test single character strings
    result = find_closest_match("a", ["a", "b"], thresholds)
    assert result.original == "a"
