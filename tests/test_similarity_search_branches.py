"""Tests for similarity_search module to cover missing branches."""

from __future__ import annotations

from game_db.similarity_search import (
    calculate_similarity_score,
    damerau_levenshtein_distance,
    find_closest_match,
    is_acceptable_match,
    normalize_string,
)


def test_damerau_levenshtein_distance_empty_strings() -> None:
    """Test damerau_levenshtein_distance with empty strings."""
    assert damerau_levenshtein_distance("", "") == 0
    assert damerau_levenshtein_distance("abc", "") == 3
    assert damerau_levenshtein_distance("", "abc") == 3


def test_damerau_levenshtein_distance_same_strings() -> None:
    """Test damerau_levenshtein_distance with identical strings."""
    assert damerau_levenshtein_distance("test", "test") == 0
    assert damerau_levenshtein_distance("hello", "hello") == 0


def test_damerau_levenshtein_distance_transposition() -> None:
    """Test damerau_levenshtein_distance with transposition."""
    # "ab" -> "ba" should be 1 (transposition)
    assert damerau_levenshtein_distance("ab", "ba") == 1
    assert damerau_levenshtein_distance("abc", "bac") == 1


def test_damerau_levenshtein_distance_substitution() -> None:
    """Test damerau_levenshtein_distance with substitution."""
    assert damerau_levenshtein_distance("abc", "axc") == 1
    assert damerau_levenshtein_distance("test", "best") == 1


def test_damerau_levenshtein_distance_insertion() -> None:
    """Test damerau_levenshtein_distance with insertion."""
    assert damerau_levenshtein_distance("abc", "abxc") == 1
    assert damerau_levenshtein_distance("test", "tests") == 1


def test_damerau_levenshtein_distance_deletion() -> None:
    """Test damerau_levenshtein_distance with deletion."""
    assert damerau_levenshtein_distance("abc", "ac") == 1
    assert damerau_levenshtein_distance("test", "est") == 1


def test_damerau_levenshtein_distance_complex() -> None:
    """Test damerau_levenshtein_distance with complex cases."""
    assert damerau_levenshtein_distance("kitten", "sitting") == 3
    assert damerau_levenshtein_distance("saturday", "sunday") == 3


def test_normalize_string() -> None:
    """Test normalize_string function."""
    assert normalize_string("  TEST  ") == "test"
    assert normalize_string("Test   String") == "test string"
    assert normalize_string("Test\nString") == "test string"


def test_calculate_similarity_score() -> None:
    """Test calculate_similarity_score function."""
    assert calculate_similarity_score(0, 5, 5) == 1.0
    assert calculate_similarity_score(2, 5, 5) == 0.6
    assert calculate_similarity_score(0, 0, 0) == 1.0


def test_is_acceptable_match() -> None:
    """Test is_acceptable_match function."""
    from game_db.config import SimilarityThresholdsConfig

    thresholds = SimilarityThresholdsConfig(
        short_length_max=10,
        short_length_distance=2,
        medium_length_max=20,
        medium_length_distance=3,
        medium_length_score=0.8,
        long_length_distance=4,
        long_length_score=0.7,
    )

    # Short string, acceptable distance
    assert is_acceptable_match(1, 0.9, 5, thresholds) is True
    # Short string, unacceptable distance
    assert is_acceptable_match(5, 0.5, 5, thresholds) is False
    # Medium string, acceptable by distance
    assert is_acceptable_match(2, 0.7, 15, thresholds) is True
    # Medium string, acceptable by score
    assert is_acceptable_match(5, 0.85, 15, thresholds) is True
    # Long string, acceptable by distance
    assert is_acceptable_match(3, 0.6, 25, thresholds) is True
    # Long string, acceptable by score
    assert is_acceptable_match(10, 0.75, 25, thresholds) is True


def test_find_closest_match_empty_candidates() -> None:
    """Test find_closest_match with empty candidates."""
    from game_db.config import SimilarityThresholdsConfig

    thresholds = SimilarityThresholdsConfig(
        short_length_max=10,
        short_length_distance=2,
        medium_length_max=20,
        medium_length_distance=3,
        medium_length_score=0.8,
        long_length_distance=4,
        long_length_score=0.7,
    )

    result = find_closest_match("test", [], thresholds)
    assert result.original == "test"
    assert result.closest_match is None
    assert result.distance == 0
    assert result.score == 0.0


def test_find_closest_match_exact() -> None:
    """Test find_closest_match with exact match."""
    from game_db.config import SimilarityThresholdsConfig

    thresholds = SimilarityThresholdsConfig(
        short_length_max=10,
        short_length_distance=2,
        medium_length_max=20,
        medium_length_distance=3,
        medium_length_score=0.8,
        long_length_distance=4,
        long_length_score=0.7,
    )

    result = find_closest_match("test", ["test", "example"], thresholds)
    assert result.original == "test"
    assert result.closest_match == "test"
    assert result.distance == 0
    assert result.score == 1.0


def test_find_closest_match_no_acceptable() -> None:
    """Test find_closest_match with no acceptable match."""
    from game_db.config import SimilarityThresholdsConfig

    thresholds = SimilarityThresholdsConfig(
        short_length_max=10,
        short_length_distance=0,  # Very strict
        medium_length_max=20,
        medium_length_distance=0,
        medium_length_score=1.0,
        long_length_distance=0,
        long_length_score=1.0,
    )

    result = find_closest_match("test", ["xyz", "abc"], thresholds)
    assert result.original == "test"
    assert result.closest_match is None
