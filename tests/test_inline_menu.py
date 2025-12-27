"""Unit tests for inline_menu module."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from game_db.config import UsersConfig
from game_db.inline_menu import InlineMenu
from game_db.security import Security


@pytest.fixture
def admin_security() -> Security:
    """Create Security instance for admin user."""
    users_cfg = UsersConfig(users=["12345"], admins=["12345"])
    return Security(users_cfg)


@pytest.fixture
def user_security() -> Security:
    """Create Security instance for regular user."""
    users_cfg = UsersConfig(users=["12345"], admins=[])
    return Security(users_cfg)


def test_main_menu_admin(admin_security: Security) -> None:
    """Test main menu for admin user."""
    markup = InlineMenu.main_menu(admin_security, 12345)

    assert markup is not None
    assert len(markup.keyboard) > 0

    # Check that admin panel button is present
    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "🛠 Admin Panel" in button_texts
    assert "🎮 My Games" in button_texts
    assert "📋 Commands" in button_texts
    assert "🔄 Database Sync" in button_texts


def test_main_menu_user(user_security: Security) -> None:
    """Test main menu for regular user."""
    markup = InlineMenu.main_menu(user_security, 12345)

    assert markup is not None
    assert len(markup.keyboard) > 0

    # Check that admin panel button is NOT present
    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "🛠 Admin Panel" not in button_texts
    assert "🎮 My Games" in button_texts
    assert "📋 Commands" in button_texts
    assert "🔄 Database Sync" in button_texts


def test_my_games_menu() -> None:
    """Test my games menu."""
    markup = InlineMenu.my_games_menu()

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "💾 Steam Games" in button_texts
    assert "🎮 Switch Games" in button_texts
    assert "📊 Statistics" in button_texts
    assert "⬅️ Back to Main Menu" in button_texts


def test_platform_menu() -> None:
    """Test platform menu."""
    markup = InlineMenu.platform_menu("Steam")

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert any("Games" in btn for btn in button_texts)
    assert "📈 Completed Count" in button_texts
    assert "⏱ Time in Games" in button_texts
    assert "⬅️ Back" in button_texts


def test_statistics_menu() -> None:
    """Test statistics menu."""
    markup = InlineMenu.statistics_menu()

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "📈 Completed Games" in button_texts
    assert "⏱ Time Spent" in button_texts
    assert "⬅️ Back" in button_texts


def test_commands_menu(admin_security: Security) -> None:
    """Test commands menu."""
    markup = InlineMenu.commands_menu(admin_security, 12345)

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "📖 User Commands" in button_texts
    assert "⬅️ Back to Main Menu" in button_texts


def test_admin_panel_menu() -> None:
    """Test admin panel menu."""
    markup = InlineMenu.admin_panel_menu()

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "📁 File Management" in button_texts
    assert "🧰 Admin Commands" in button_texts
    assert "⬅️ Back to Main Menu" in button_texts


def test_platform_menu_with_pagination() -> None:
    """Test platform menu with pagination."""
    markup = InlineMenu.platform_menu_with_pagination("Steam", 11, 10)

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert any("Games" in btn for btn in button_texts)
    assert "📈 Completed Count" in button_texts


def test_file_management_menu() -> None:
    """Test file management menu."""
    markup = InlineMenu.file_management_menu()

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "📄 File List" in button_texts
    assert "⬇️ Download Game Template" in button_texts
    assert "⬅️ Back" in button_texts


def test_sync_menu() -> None:
    """Test sync menu."""
    markup = InlineMenu.sync_menu()

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert "Steam" in str(button_texts) or "🔍 Check Steam Data" in button_texts
    assert "Metacritic" in str(button_texts) or any(
        "Metacritic" in btn for btn in button_texts
    )
    assert "HowLongToBeat" in str(button_texts) or any(
        "HowLongToBeat" in btn for btn in button_texts
    )
    assert "⬅️ Back to Main Menu" in button_texts


def test_steam_check_menu_no_missing() -> None:
    """Test steam check menu with no missing games."""
    markup = InlineMenu.steam_check_menu(has_missing_games=False)

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    # Should not have "Add found games to DB" button when no missing games
    assert not any("Add" in btn for btn in button_texts)


def test_steam_check_menu_with_missing() -> None:
    """Test steam check menu with missing games."""
    markup = InlineMenu.steam_check_menu(has_missing_games=True)

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    # Should have "Add found games to DB" button when there are missing games
    assert any("Add" in btn for btn in button_texts)


def test_metacritic_sync_menu() -> None:
    """Test metacritic sync menu."""
    markup = InlineMenu.metacritic_sync_menu()

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert any("Full" in btn for btn in button_texts)
    assert any("Partial" in btn for btn in button_texts)
    assert any("Back" in btn for btn in button_texts)


def test_hltb_sync_menu() -> None:
    """Test HowLongToBeat sync menu."""
    markup = InlineMenu.hltb_sync_menu()

    assert markup is not None
    assert len(markup.keyboard) > 0

    button_texts = [btn.text for row in markup.keyboard for btn in row]
    assert any("Full" in btn for btn in button_texts)
    assert any("Partial" in btn for btn in button_texts)
    assert any("Back" in btn for btn in button_texts)
