"""Telegram bot menu building (moved from work_with_menu.py)."""

from __future__ import annotations

import telebot
from telebot.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from .security import Security


class BotMenu:
    """Build reply keyboards for the bot."""

    @staticmethod
    def main_menu(message: Message, security: Security) -> ReplyKeyboardMarkup:
        """Build main menu keyboard for the given user."""
        markup = telebot.types.ReplyKeyboardMarkup(
            row_width=1, resize_keyboard=True
        )
        show_commands = telebot.types.KeyboardButton(
            text="Показать доступные команды"
        )
        button_clear = telebot.types.KeyboardButton(text="Убрать меню")
        next_game_list = telebot.types.KeyboardButton(text="Списки игр")
        if security.admin_check(message.chat.id):
            file_menu = telebot.types.KeyboardButton(
                text="Меню управления файлами"
            )
            show_admin_commands = telebot.types.KeyboardButton(
                text="Показать доступные команды админа"
            )
            synchronize_steam_games = telebot.types.KeyboardButton(
                text="Synchronize games to Steam"
            )
            markup.add(
                button_clear,
                show_commands,
                show_admin_commands,
                next_game_list,
                file_menu,
                synchronize_steam_games,
            )
        else:
            markup.add(button_clear, show_commands, next_game_list)
        return markup

    @staticmethod
    def file_menu(
        message: Message, security: Security
    ) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
        """File management menu."""
        get_file_to_server_text = (
            "Получить список файлов на сервере"
        )

        markup = telebot.types.ReplyKeyboardMarkup(
            row_width=1, resize_keyboard=True
        )
        if security.admin_check(message.chat.id):
            get_file_to_server = telebot.types.KeyboardButton(
                text=get_file_to_server_text
            )
            get_excel = telebot.types.KeyboardButton(
                text="Получить файл для заполнения игр"
            )
            main_menu = telebot.types.KeyboardButton(text="В главное меню")
            markup.add(get_file_to_server, get_excel, main_menu)
            return markup
        return telebot.types.ReplyKeyboardRemove()

    @staticmethod
    def next_game(message: Message) -> ReplyKeyboardMarkup:
        """Menu for iterating over next games."""
        list_from_steam = 1
        how_much_row_steam = 10
        list_from_switch = 1
        how_much_row_switch = 10
        markup = telebot.types.ReplyKeyboardMarkup(
            row_width=1, resize_keyboard=True
        )
        if message.text and "Steam" in message.text:
            message_text: list[str] = []
            for i in message.text.split(","):
                message_text.append(i)
            if len(message_text) >= 3:
                list_from_steam = int(message_text[1])
                how_much_row_steam = int(message_text[2])
        elif message.text and "Switch" in message.text:
            message_text = []
            for i in message.text.split(","):
                message_text.append(i)
            if len(message_text) >= 3:
                list_from_switch = int(message_text[1])
                how_much_row_switch = int(message_text[2])

        list_of_steam_next_games = telebot.types.KeyboardButton(
            text=(
                "Cписок Steam игр на прохождение,"
                f"{list_from_steam},{how_much_row_steam}"
            )
        )
        list_of_switch_next_games = telebot.types.KeyboardButton(
            text=(
                "Cписок Switch игр на прохождение,"
                f"{list_from_switch},{how_much_row_switch}"
            )
        )
        count_overall = telebot.types.KeyboardButton(
            text="Сколько игр прошёл Александр"
        )
        count_overall_time = telebot.types.KeyboardButton(
            text="Сколько времени Александр потратил на игры"
        )
        main_menu = telebot.types.KeyboardButton(text="В главное меню")
        markup.add(
            list_of_steam_next_games,
            list_of_switch_next_games,
            count_overall,
            count_overall_time,
            main_menu,
        )
        return markup

    @staticmethod
    def clear_menu() -> ReplyKeyboardRemove:
        """Clear menu (remove keyboard)."""
        return telebot.types.ReplyKeyboardRemove()
