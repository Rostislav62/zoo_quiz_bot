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


def get_social_share_buttons(animal_name, page_url):
    share_text = f"Мое тотемное животное - {animal_name}! Узнай свое тотемное животное в викторине Московского зоопарка."
    share_url = f"{page_url}"

    buttons = [
        InlineKeyboardButton("Facebook",
                             url=f"https://www.facebook.com/sharer/sharer.php?u={share_url}&quote={share_text}"),
        InlineKeyboardButton("Twitter", url=f"https://twitter.com/intent/tweet?url={share_url}&text={share_text}"),
        InlineKeyboardButton("VK", url=f"https://vk.com/share.php?url={share_url}&title={share_text}")
    ]

    return InlineKeyboardMarkup().add(*buttons)


def get_messenger_share_buttons(animal_name, page_url):
    share_text = f"Мое тотемное животное - {animal_name}! Узнай свое тотемное животное в викторине Московского зоопарка: {page_url}"

    buttons = [
        InlineKeyboardButton("WhatsApp", url=f"https://wa.me/?text={share_text}"),
        InlineKeyboardButton("Telegram", url=f"https://t.me/share/url?url={page_url}&text={share_text}")
    ]

    return InlineKeyboardMarkup().add(*buttons)
