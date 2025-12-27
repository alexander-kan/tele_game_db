"""Tests for service layer functions in game_service."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from game_db.services import game_service


def test_query_game_success() -> None:
    """query_game delegates to repository and returns its result."""
    with patch("game_db.services.game_service._repository") as repo:
        repo.query_game.return_value = [("Game",)]

        result = game_service.query_game("Test")

        repo.query_game.assert_called_once_with("Test")
        assert result == [("Game",)]


def test_get_next_game_list_success() -> None:
    """get_next_game_list delegates to repository."""
    with patch("game_db.services.game_service._repository") as repo:
        repo.get_next_game_list.return_value = [("Game", "Steam", None, None)]

        result = game_service.get_next_game_list(0, 10, "Steam")

        repo.get_next_game_list.assert_called_once_with(0, 10, "Steam")
        assert result == [("Game", "Steam", None, None)]


def test_count_complete_games_success() -> None:
    """count_complete_games returns integer from repository."""
    with patch("game_db.services.game_service._repository") as repo:
        repo.count_complete_games.return_value = 5

        result = game_service.count_complete_games("Steam")

        repo.count_complete_games.assert_called_once_with("Steam")
        assert result == 5


def test_count_spend_time_success() -> None:
    """count_spend_time returns tuple from repository."""
    with patch("game_db.services.game_service._repository") as repo:
        repo.count_spend_time.return_value = (1.5, 2.5)

        result = game_service.count_spend_time("Steam", 0)

        repo.count_spend_time.assert_called_once_with("Steam", 0)
        assert result == (1.5, 2.5)


def test_get_platforms_success() -> None:
    """get_platforms returns list from repository."""
    with patch("game_db.services.game_service._repository") as repo:
        repo.get_platforms.return_value = ["Steam", "Switch"]

        result = game_service.get_platforms()

        repo.get_platforms.assert_called_once_with()
        assert result == ["Steam", "Switch"]


def test_query_game_propagates_gamedb_error() -> None:
    """query_game should re-raise GameDBError from repository unchanged."""
    from game_db.exceptions import GameDBError

    with patch("game_db.services.game_service._repository") as repo:
        repo.query_game.side_effect = GameDBError("boom")

        try:
            game_service.query_game("Test")
        except GameDBError as exc:
            assert str(exc) == "boom"
        else:
            raise AssertionError("GameDBError was not propagated")


def test_count_complete_games_propagates_gamedb_error() -> None:
    """count_complete_games should re-raise GameDBError."""
    from game_db.exceptions import GameDBError

    with patch("game_db.services.game_service._repository") as repo:
        repo.count_complete_games.side_effect = GameDBError("fail")

        try:
            game_service.count_complete_games("Steam")
        except GameDBError as exc:
            assert str(exc) == "fail"
        else:
            raise AssertionError("GameDBError was not propagated")


def test_count_spend_time_propagates_gamedb_error() -> None:
    """count_spend_time should re-raise GameDBError."""
    from game_db.exceptions import GameDBError

    with patch("game_db.services.game_service._repository") as repo:
        repo.count_spend_time.side_effect = GameDBError("time error")

        try:
            game_service.count_spend_time("Steam", 0)
        except GameDBError as exc:
            assert str(exc) == "time error"
        else:
            raise AssertionError("GameDBError was not propagated")


def test_get_platforms_propagates_gamedb_error() -> None:
    """get_platforms should re-raise GameDBError."""
    from game_db.exceptions import GameDBError

    with patch("game_db.services.game_service._repository") as repo:
        repo.get_platforms.side_effect = GameDBError("platforms error")

        try:
            game_service.get_platforms()
        except GameDBError as exc:
            assert str(exc) == "platforms error"
        else:
            raise AssertionError("GameDBError was not propagated")


def test_get_next_game_list_wraps_generic_exception() -> None:
    """get_next_game_list should wrap unexpected exceptions in DatabaseError."""
    from game_db.exceptions import DatabaseError

    with patch("game_db.services.game_service._repository") as repo:
        repo.get_next_game_list.side_effect = ValueError("boom")

        with pytest.raises(DatabaseError) as exc_info:
            game_service.get_next_game_list(0, 10, "Steam")

        assert "Unexpected error getting game list" in str(exc_info.value)


def test_count_spend_time_wraps_generic_exception() -> None:
    """count_spend_time should wrap unexpected exceptions in DatabaseError."""
    from game_db.exceptions import DatabaseError

    with patch("game_db.services.game_service._repository") as repo:
        repo.count_spend_time.side_effect = RuntimeError("time boom")

        with pytest.raises(DatabaseError) as exc_info:
            game_service.count_spend_time("Steam", 0)

        assert "Unexpected error counting time" in str(exc_info.value)
