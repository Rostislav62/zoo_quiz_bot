# keyboards.py
# Создаёт кнопки

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_quiz_start_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Начало викторины", callback_data='quiz_start'))
    return keyboard

def get_quiz_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = ["1", "2", "3", "4"]
    keyboard.add(*buttons)
    return keyboard

def get_main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/sponsorship"))
    return keyboard
