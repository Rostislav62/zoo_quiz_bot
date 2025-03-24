# keyboards.py
# Создаёт кнопки

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


def get_quiz_start_keyboard(button_text="Начало викторины", callback_data="quiz_start"):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))
    return keyboard


def get_quiz_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = ["1", "2", "3", "4"]
    keyboard.add(*buttons)
    return keyboard
