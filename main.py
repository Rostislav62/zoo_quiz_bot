# main.py
# Python 3.8.10
# для корректной работы этого бота я загнузил эти пакеты
# pip install aiogram==2.21 aiohttp==3.8.1
# содержит только тот код который нужен для старта и управления ботом.
# API_TOKEN = '7148692650:AAGgk9MkQJKicsPsK3GD-QhTku5u1XILIfQ'

import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from images import API_TOKEN

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния
class QuizStates(StatesGroup):
    NAME = State()
    AGE = State()
    CHILDREN = State()
    CHILDREN_NUMBER = State()
    ANIMAL_TYPE = State()
    QUESTION = State()

# Обработчик команды /start
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("Привет!\nЯ бот-викторина Московского зоопарка.\nКаково Ваше имя?")
    await QuizStates.NAME.set()

# Обработчик имени
@dp.message_handler(state=QuizStates.NAME)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer(f"Приятно познакомиться, {message.text}!\nСколько вам лет?\nПишите только цифру.")
    await QuizStates.AGE.set()

# Обработчик возраста
@dp.message_handler(state=QuizStates.AGE)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
        name = data['name']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Начало викторины"))
    await message.answer(f"{name}, давай начнем викторину!", reply_markup=markup)
    await QuizStates.CHILDREN.set()

# Обработчик начала викторины
@dp.message_handler(lambda message: message.text == "Начало викторины", state=QuizStates.CHILDREN)
async def process_quiz_start(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()
    await message.answer("Викторина началась!", reply_markup=markup)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    await message.answer("Есть ли у тебя дети?", reply_markup=markup)

# Обработчик ответа о детях
@dp.message_handler(lambda message: message.text in ["Да", "Нет"], state=QuizStates.CHILDREN)
async def process_children(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['children'] = message.text.lower() == 'да'
    markup = types.ReplyKeyboardRemove()
    if data['children']:
        await message.answer("Сколько у вас детей?\nПишите только цифру.", reply_markup=markup)
        await QuizStates.CHILDREN_NUMBER.set()
    else:
        await message.answer("Какой вид обитателей Московского зоопарка вы выбираете?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Животные", "Птицы", "Рыбы", "Земноводные", "Змеи"))
        await QuizStates.ANIMAL_TYPE.set()

# Обработчик количества детей
@dp.message_handler(state=QuizStates.CHILDREN_NUMBER)
async def process_children_number(message: types.Message, state: FSMContext):
    await message.answer("Какой вид обитателей Московского зоопарка вы выбираете?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Животные", "Птицы", "Рыбы", "Земноводные", "Змеи"))
    await QuizStates.ANIMAL_TYPE.set()

# Обработчик выбора типа животных
@dp.message_handler(state=QuizStates.ANIMAL_TYPE)
async def process_animal_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        animal_type_key = None
        if message.text.lower() == 'животные':
            animal_type_key = 'animals'
        elif message.text.lower() == 'птицы':
            animal_type_key = 'birds'
        elif message.text.lower() == 'рыбы':
            animal_type_key = 'fishes'
        elif message.text.lower() == 'земноводные':
            animal_type_key = 'amphibians'
        elif message.text.lower() == 'змеи':
            animal_type_key = 'snakes'

        if animal_type_key:
            with open('quiz_text.json', 'r', encoding='utf-8') as file:
                quiz_data = json.load(file)
            if animal_type_key in quiz_data:
                questions_data = quiz_data[animal_type_key]
                questions = questions_data['questions'].replace("{name}", data['name'])
                options = questions_data['options']
                data['questions'] = questions
                data['options'] = options
                await QuizStates.QUESTION.set()
                await message.answer(questions)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.row(*[types.KeyboardButton(str(i + 1)) for i in range(len(options))])
                await message.answer("\n".join(options), reply_markup=markup)
            else:
                await message.answer("Извините, не удалось найти вопросы для выбранного типа обитателей.")
        else:
            await message.answer("Пожалуйста, выберите один из предложенных типов обитателей.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

