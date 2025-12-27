"""Unit tests for hltb_client module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest


def test_hltb_client_init_success() -> None:
    """Test HowLongToBeatClient initialization when library is available."""
    with patch("game_db.hltb_client.HowLongToBeat") as mock_hltb:
        mock_instance = Mock()
        mock_hltb.return_value = mock_instance
        
        from game_db.hltb_client import HowLongToBeatClient
        
        client = HowLongToBeatClient()
        
        assert client is not None
        assert client.client == mock_instance
        mock_hltb.assert_called_once()


def test_hltb_client_init_import_error() -> None:
    """Test HowLongToBeatClient initialization when library is not available."""
    with patch("game_db.hltb_client.HowLongToBeat", None):
        from game_db.hltb_client import HowLongToBeatClient
        
        with pytest.raises(ImportError, match="howlongtobeatpy library is not installed"):
            HowLongToBeatClient()


@patch("game_db.hltb_client.HowLongToBeat")
def test_search_game_success(mock_hltb_class: Mock) -> None:
    """Test successful game search."""
    from game_db.hltb_client import HowLongToBeatClient
    
    # Create mock result
    mock_result = Mock()
    mock_result.game_name = "Test Game"
    mock_result.game_id = "12345"
    mock_result.main_story = 10.5
    mock_result.main_extra = 15.0
    mock_result.completionist = 20.0
    mock_result.all_styles = 12.5
    mock_result.similarity = 0.95
    
    mock_client = Mock()
    mock_client.search.return_value = [mock_result]
    mock_hltb_class.return_value = mock_client
    
    client = HowLongToBeatClient()
    result = client.search_game("Test Game")
    
    assert result is not None
    assert result["game_name"] == "Test Game"
    assert result["game_id"] == "12345"
    assert result["main_story"] == 10.5
    assert result["main_extra"] == 15.0
    assert result["completionist"] == 20.0
    assert result["all_styles"] == 12.5
    assert result["similarity"] == 0.95
    mock_client.search.assert_called_once_with("Test Game")


@patch("game_db.hltb_client.HowLongToBeat")
def test_search_game_no_results(mock_hltb_class: Mock) -> None:
    """Test game search with no results."""
    from game_db.hltb_client import HowLongToBeatClient
    
    mock_client = Mock()
    mock_client.search.return_value = []
    mock_hltb_class.return_value = mock_client
    
    client = HowLongToBeatClient()
    result = client.search_game("Non-existent Game")
    
    assert result is None
    mock_client.search.assert_called_once_with("Non-existent Game")


@patch("game_db.hltb_client.HowLongToBeat")
def test_search_game_multiple_results_picks_best(mock_hltb_class: Mock) -> None:
    """Test game search with multiple results picks best by similarity."""
    from game_db.hltb_client import HowLongToBeatClient
    
    # Create mock results with different similarities
    mock_result1 = Mock()
    mock_result1.game_name = "Test Game 1"
    mock_result1.game_id = "1"
    mock_result1.main_story = 10.0
    mock_result1.main_extra = 15.0
    mock_result1.completionist = 20.0
    mock_result1.all_styles = 12.0
    mock_result1.similarity = 0.80
    
    mock_result2 = Mock()
    mock_result2.game_name = "Test Game 2"
    mock_result2.game_id = "2"
    mock_result2.main_story = 12.0
    mock_result2.main_extra = 18.0
    mock_result2.completionist = 25.0
    mock_result2.all_styles = 15.0
    mock_result2.similarity = 0.95  # Better similarity
    
    mock_client = Mock()
    mock_client.search.return_value = [mock_result1, mock_result2]
    mock_hltb_class.return_value = mock_client
    
    client = HowLongToBeatClient()
    result = client.search_game("Test Game")
    
    # Should pick the one with highest similarity
    assert result is not None
    assert result["game_name"] == "Test Game 2"
    assert result["similarity"] == 0.95


@patch("game_db.hltb_client.HowLongToBeat")
def test_search_game_exception_handling(mock_hltb_class: Mock) -> None:
    """Test game search handles exceptions gracefully."""
    from game_db.hltb_client import HowLongToBeatClient
    
    mock_client = Mock()
    mock_client.search.side_effect = Exception("Network error")
    mock_hltb_class.return_value = mock_client
    
    client = HowLongToBeatClient()
    result = client.search_game("Test Game")
    
    # Should return None on exception
    assert result is None
    mock_client.search.assert_called_once_with("Test Game")


@patch("game_db.hltb_client.HowLongToBeat")
def test_search_game_with_none_values(mock_hltb_class: Mock) -> None:
    """Test game search handles None values in result."""
    from game_db.hltb_client import HowLongToBeatClient
    
    mock_result = Mock()
    mock_result.game_name = "Test Game"
    mock_result.game_id = "12345"
    mock_result.main_story = None
    mock_result.main_extra = None
    mock_result.completionist = None
    mock_result.all_styles = None
    mock_result.similarity = 0.90
    
    mock_client = Mock()
    mock_client.search.return_value = [mock_result]
    mock_hltb_class.return_value = mock_client
    
    client = HowLongToBeatClient()
    result = client.search_game("Test Game")
    
    assert result is not None
    assert result["game_name"] == "Test Game"
    assert result["main_story"] is None
    assert result["main_extra"] is None
    assert result["completionist"] is None
    assert result["all_styles"] is None
