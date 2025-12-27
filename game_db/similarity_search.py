"""String similarity search using Damerau-Levenshtein distance.

This module provides functionality to find similar game names in the database
when exact matches are not found during Steam synchronization.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

try:
    from pyxdameraulevenshtein import damerau_levenshtein_distance
except ImportError:
    # Fallback to simple implementation if library not available
    def damerau_levenshtein_distance(seq1: str, seq2: str) -> int:  # type: ignore[misc]
        """Simple fallback implementation."""
        # This is a simplified version - for production use the library
        if seq1 == seq2:
            return 0
        if len(seq1) == 0:
            return len(seq2)
        if len(seq2) == 0:
            return len(seq1)
        # Simple Levenshtein distance (not full Damerau-Levenshtein)
        d = [[0] * (len(seq2) + 1) for _ in range(len(seq1) + 1)]
        for i in range(len(seq1) + 1):
            d[i][0] = i
        for j in range(len(seq2) + 1):
            d[0][j] = j
        for i in range(1, len(seq1) + 1):
            for j in range(1, len(seq2) + 1):
                cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
                d[i][j] = min(
                    d[i - 1][j] + 1,  # deletion
                    d[i][j - 1] + 1,  # insertion
                    d[i - 1][j - 1] + cost,  # substitution
                )
        return d[len(seq1)][len(seq2)]


if TYPE_CHECKING:
    from .config import SimilarityThresholdsConfig


@dataclass
class SimilarityMatch:
    """Result of similarity search for a game name."""

    original: str
    closest_match: str | None
    distance: int
    score: float


def normalize_string(s: str) -> str:
    """Normalize string for comparison.

    Performs:
    - trim whitespace
    - lowercase
    - compress multiple spaces to single space

    Args:
        s: Input string

    Returns:
        Normalized string
    """
    # Trim and lowercase
    normalized = s.strip().lower()

    # Compress multiple spaces to single space
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized


def calculate_similarity_score(distance: int, len_a: int, len_b: int) -> float:
    """Calculate normalized similarity score.

    Args:
        distance: Damerau-Levenshtein distance
        len_a: Length of first string
        len_b: Length of second string

    Returns:
        Similarity score (0.0 to 1.0, where 1.0 is perfect match)
    """
    max_len = max(len_a, len_b)
    if max_len == 0:
        return 1.0
    return 1.0 - (distance / max_len)


def is_acceptable_match(
    distance: int,
    score: float,
    string_length: int,
    thresholds: "SimilarityThresholdsConfig",
) -> bool:
    """Check if match is acceptable based on thresholds.

    Args:
        distance: Damerau-Levenshtein distance
        score: Normalized similarity score
        string_length: Length of the original string
        thresholds: Similarity thresholds configuration

    Returns:
        True if match is acceptable, False otherwise
    """
    if string_length <= thresholds.short_length_max:
        return distance <= thresholds.short_length_distance
    elif string_length <= thresholds.medium_length_max:
        return (
            distance <= thresholds.medium_length_distance
            or score >= thresholds.medium_length_score
        )
    else:
        return (
            distance <= thresholds.long_length_distance
            or score >= thresholds.long_length_score
        )


def find_closest_match(
    original: str,
    candidates: list[str],
    thresholds: "SimilarityThresholdsConfig",
    length_diff_threshold: int = 3,
) -> SimilarityMatch:
    """Find closest matching string from candidates.

    Args:
        original: Original string to find match for
        candidates: List of candidate strings to search in
        thresholds: Similarity thresholds configuration
        length_diff_threshold: Maximum length difference for pre-filtering

    Returns:
        SimilarityMatch object with best match or None if no acceptable match
    """
    if not candidates:
        return SimilarityMatch(
            original=original,
            closest_match=None,
            distance=0,
            score=0.0,
        )

    original_normalized = normalize_string(original)
    original_len = len(original_normalized)

    best_match: str | None = None
    best_distance = float("inf")
    best_score = 0.0

    # Pre-filter candidates by length difference
    filtered_candidates = [
        c
        for c in candidates
        if abs(len(normalize_string(c)) - original_len) <= length_diff_threshold
    ]

    if not filtered_candidates:
        # If no candidates pass length filter, try all
        filtered_candidates = candidates

    for candidate in filtered_candidates:
        candidate_normalized = normalize_string(candidate)
        candidate_len = len(candidate_normalized)

        # Calculate distance
        distance = damerau_levenshtein_distance(
            original_normalized, candidate_normalized
        )

        # Calculate score
        score = calculate_similarity_score(distance, original_len, candidate_len)

        # Check if this is the best match so far
        if distance < best_distance:
            best_distance = distance
            best_score = score
            best_match = candidate

    # Check if best match is acceptable
    if best_match is not None and is_acceptable_match(
        int(best_distance),
        best_score,
        original_len,
        thresholds,
    ):
        return SimilarityMatch(
            original=original,
            closest_match=best_match,
            distance=int(best_distance),
            score=best_score,
        )

    return SimilarityMatch(
        original=original,
        closest_match=None,
        distance=int(best_distance) if best_match else 0,
        score=best_score,
    )
