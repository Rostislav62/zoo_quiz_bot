# main.py
# Python 3.8.10
# для корректной работы этого бота я загнузил эти пакеты
# pip install aiogram==2.21 aiohttp==3.8.1
# содержит только тот код который нужен для старта и управления ботом.
# API_TOKEN = '7148692650:AAGgk9MkQJKicsPsK3GD-QhTku5u1XILIfQ'

import logging
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from config import API_TOKEN
from handlers import register_handlers

# Установка логгера для отладочных сообщений
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Регистрация обработчиков
register_handlers(dp, bot)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
