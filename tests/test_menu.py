"""Tests for menu module."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from game_db.menu import BotMenu
from game_db.security import Security


class TestBotMenu:
    """Test BotMenu class."""

    # Fixtures are now imported from conftest.py
    # mock_message, admin_security, user_security

    def test_main_menu_admin(self, mock_message: Mock, admin_security: Security) -> None:
        """Test main_menu for admin user."""
        markup = BotMenu.main_menu(mock_message, admin_security)

        assert markup is not None
        assert hasattr(markup, "keyboard")
        assert len(markup.keyboard) > 0
        
        # Check that admin buttons are present by checking keyboard structure
        all_buttons = []
        for row in markup.keyboard:
            for button in row:
                if isinstance(button, dict):
                    all_buttons.append(button.get("text", ""))
                else:
                    all_buttons.append(getattr(button, "text", ""))

        assert "Убрать меню" in all_buttons
        assert "Показать доступные команды" in all_buttons
        assert "Списки игр" in all_buttons
        assert "Меню управления файлами" in all_buttons
        assert "Показать доступные команды админа" in all_buttons
        assert "Synchronize games to Steam" in all_buttons

    def test_main_menu_regular_user(
        self, mock_message: Mock, user_security: Security
    ) -> None:
        """Test main_menu for regular user."""
        markup = BotMenu.main_menu(mock_message, user_security)

        assert markup is not None
        assert hasattr(markup, "keyboard")
        
        all_buttons = []
        for row in markup.keyboard:
            for button in row:
                if isinstance(button, dict):
                    all_buttons.append(button.get("text", ""))
                else:
                    all_buttons.append(getattr(button, "text", ""))

        assert "Убрать меню" in all_buttons
        assert "Показать доступные команды" in all_buttons
        assert "Списки игр" in all_buttons
        # Admin buttons should not be present
        assert "Меню управления файлами" not in all_buttons
        assert "Показать доступные команды админа" not in all_buttons
        assert "Synchronize games to Steam" not in all_buttons

    def test_file_menu_admin(self, mock_message: Mock, admin_security: Security) -> None:
        """Test file_menu for admin user."""
        markup = BotMenu.file_menu(mock_message, admin_security)

        assert markup is not None
        assert hasattr(markup, "keyboard")
        
        all_buttons = []
        for row in markup.keyboard:
            for button in row:
                if isinstance(button, dict):
                    all_buttons.append(button.get("text", ""))
                else:
                    all_buttons.append(getattr(button, "text", ""))

        assert "Получить список файлов на сервере" in all_buttons
        assert "Получить файл для заполнения игр" in all_buttons
        assert "В главное меню" in all_buttons

    def test_file_menu_regular_user(
        self, mock_message: Mock, user_security: Security
    ) -> None:
        """Test file_menu for regular user returns ReplyKeyboardRemove."""
        from telebot.types import ReplyKeyboardRemove

        markup = BotMenu.file_menu(mock_message, user_security)

        assert isinstance(markup, ReplyKeyboardRemove)

    def test_next_game_default(self, mock_message: Mock) -> None:
        """Test next_game with default message."""
        mock_message.text = "test message"
        markup = BotMenu.next_game(mock_message)

        assert markup is not None
        assert hasattr(markup, "keyboard")
        
        all_buttons = []
        for row in markup.keyboard:
            for button in row:
                if isinstance(button, dict):
                    all_buttons.append(button.get("text", ""))
                else:
                    all_buttons.append(getattr(button, "text", ""))

        assert "Cписок Steam игр на прохождение,1,10" in all_buttons
        assert "Cписок Switch игр на прохождение,1,10" in all_buttons
        assert "Сколько игр прошёл Александр" in all_buttons
        assert "Сколько времени Александр потратил на игры" in all_buttons
        assert "В главное меню" in all_buttons

    def test_next_game_steam_message(self, mock_message: Mock) -> None:
        """Test next_game with Steam message containing pagination."""
        mock_message.text = "Cписок Steam игр на прохождение,5,20"
        markup = BotMenu.next_game(mock_message)

        assert markup is not None
        assert hasattr(markup, "keyboard")
        
        all_buttons = []
        for row in markup.keyboard:
            for button in row:
                if isinstance(button, dict):
                    all_buttons.append(button.get("text", ""))
                else:
                    all_buttons.append(getattr(button, "text", ""))

        assert "Cписок Steam игр на прохождение,5,20" in all_buttons
        assert "Cписок Switch игр на прохождение,1,10" in all_buttons

    def test_next_game_switch_message(self, mock_message: Mock) -> None:
        """Test next_game with Switch message containing pagination."""
        mock_message.text = "Cписок Switch игр на прохождение,3,15"
        markup = BotMenu.next_game(mock_message)

        assert markup is not None
        assert hasattr(markup, "keyboard")
        
        all_buttons = []
        for row in markup.keyboard:
            for button in row:
                if isinstance(button, dict):
                    all_buttons.append(button.get("text", ""))
                else:
                    all_buttons.append(getattr(button, "text", ""))

        assert "Cписок Steam игр на прохождение,1,10" in all_buttons
        assert "Cписок Switch игр на прохождение,3,15" in all_buttons

    def test_clear_menu(self) -> None:
        """Test clear_menu returns ReplyKeyboardRemove."""
        from telebot.types import ReplyKeyboardRemove

        markup = BotMenu.clear_menu()

        assert isinstance(markup, ReplyKeyboardRemove)
