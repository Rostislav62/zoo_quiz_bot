# # - Контактный механизм в файле contacts.py
#
#
# from aiogram import types, Dispatcher
#
# async def contact_support(message: types.Message):
#     await message.answer("Свяжитесь с нами по телефону +7 (495) 123-45-67 или email: info@moscowzoo.ru")
#
# def register_contact_handlers(dp: Dispatcher):
#     dp.register_message_handler(contact_support, commands="contact")


import logging
import random
import string
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

# Установка логгера для отладочных сообщений
logging.basicConfig(level=logging.INFO)

# Загрузка токена API
from images import API_TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Глобальные переменные для хранения состояния
user_name = None
quiz_started = False
question_numbers = []  # Список для хранения номеров вопросов
questions = None
answers = None
txt_file = None
selected_question = None  # Переменная для хранения текущего выбранного вопроса


# Загрузка вопросов из файла JSON и инициализация списка номеров вопросов
def load_questions():
    global questions, question_numbers
    with open('questions.json', 'r', encoding='utf-8') as file:
        questions = json.load(file)
        question_numbers = list(questions.keys())  # Получаем список всех номеров вопросов


# Функция для получения случайного вопроса
def get_random_question():
    global question_numbers, selected_question
    if question_numbers:
        question_id = random.choice(question_numbers)
        selected_question = questions[question_id]  # Сохраняем выбранный вопрос
        question_numbers.remove(question_id)  # Удаляем выбранный вопрос из списка
        return question_id, selected_question['question']
    else:
        return None, None


def load_animal_data():
    with open('quiz_text.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def get_random_animal_answers(animal_data):
    categories = ['Млекопитающие', 'Птицы', 'Рептилии', 'Амфибии']
    questions_and_answers = []
    for category in categories:
        animals = list(animal_data[category].items())
        animal_name, animal_info = random.choice(animals)
        answer = random.choice(animal_info['answers'])
        category_id = animal_info['category_id']
        animal_id = animal_info['animal_id']
        questions_and_answers.append((animal_name, answer, category_id, animal_id))
    return questions_and_answers


# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    global quiz_started, answers, txt_file
    quiz_started = False
    answers = []
    load_questions()  # Загружаем вопросы при старте

    # Отправка приветственного сообщения
    await bot.send_message(message.chat.id, "Привет! \nЯ бот-викторина Московского зоопарка.\n\nНапишите Ваше имя?")


# Обработка введенного имени
@dp.message_handler(lambda message: message.text and not message.text.startswith('/') and not quiz_started)
async def process_name(message: types.Message):
    global user_name, txt_file
    user_name = message.text

    # Создание имени файла с именем пользователя и 6 случайными числами
    random_numbers = ''.join(random.choices(string.digits, k=6))
    txt_file = f"{user_name.replace(' ', '_')}_{random_numbers}.txt"

    # Запись в файл информации
    with open(txt_file, 'w', encoding='utf-8') as file:
        file.write(f"{user_name}\n\n")

    # Отправка сообщения о создании файла и начале викторины
    await bot.send_message(message.chat.id, f"Я создал файл\n{txt_file}\n\nПриятно познакомиться, {user_name}!\n"
                                            f"Викторина поможет вам узнать какое у вас тотемное животное.\n"
                                            f"Нажмите на кнопку ниже, чтобы начать викторину.",
                           reply_markup=get_quiz_start_keyboard())


# Функция для создания клавиатуры с кнопкой "Начало викторины"
def get_quiz_start_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Начало викторины", callback_data='quiz_start'))
    return keyboard


# Обработка нажатия на кнопку "Начало викторины"
@dp.callback_query_handler(lambda c: c.data == 'quiz_start')
async def process_quiz_start(callback_query: types.CallbackQuery):
    global quiz_started, question_numbers
    quiz_started = True
    question_numbers = list(questions.keys())  # Восстанавливаем полный список вопросов
    await callback_query.answer()
    # Удаление кнопки "Начало викторины" после нажатия
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=None)
    # Отправка первого вопроса
    await send_question(callback_query.from_user.id)


# # Функция для отправки вопроса
# async def send_question(user_id):
#     global questions
#     question_id, question_text = get_random_question()
#     if question_id and question_text:
#         question_text_with_answers = format_question_with_answers(question_text)
#         await bot.send_message(user_id, question_text_with_answers,
#                                reply_markup=get_quiz_keyboard())
#     else:
#         await bot.send_message(user_id, "Конец викторины.", reply_markup=types.ReplyKeyboardRemove())
#
#
# # Функция для форматирования вопроса с вариантами ответов на новых строках
# def format_question_with_answers(question_text):
#     global answers
#     answers = ["1 ответ", "2 ответ", "3 ответ", "4 ответ"]
# # random.shuffle(answers)  # Строка удалена для сохранения порядка ответов
#     formatted_text = f"{question_text}\n"
#     for i, answer in enumerate(answers, start=1):
#         formatted_text += f"{i}. {answer}\n"
#     return formatted_text.strip()

# Функция для отправки вопроса
async def send_question(user_id):
    global questions, animal_data  # Добавьте animal_data в глобальные переменные, если это необходимо

    # Загрузка данных о животных и выбор ответов
    animal_data = load_animal_data()
    qa_pairs = get_random_animal_answers(animal_data)

    # Подготовка вопроса и ответов
    question_id, question_text = get_random_question()
    if question_id and question_text:
        # Использовать данные животных для формирования текста вопроса и ответов
        question_text_with_answers = format_question_with_answers(question_text, qa_pairs)
        await bot.send_message(user_id, f"{question_text_with_answers}",
                               reply_markup=get_quiz_keyboard())
    else:
        await bot.send_message(user_id, "Конец викторины.", reply_markup=types.ReplyKeyboardRemove())


# Модифицированная функция format_question_with_answers для включения животных и ответов
def format_question_with_answers(question_text, qa_pairs):
    formatted_text = f"{question_text}\n"
    for i, (name, answer, cid, aid) in enumerate(qa_pairs, start=1):
        formatted_text += f"{i}. {answer} (Животное: {name}, category_id: {cid}, animal_id: {aid})\n"
    return formatted_text.strip()


# Функция для создания обычной клавиатуры с вариантами ответов (в одном ряду)
def get_quiz_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = ["1", "2", "3", "4"]
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(lambda message: quiz_started and message.text in ["1", "2", "3", "4"])
async def process_quiz_answer(message: types.Message):
    global answers, txt_file
    selected_answer = answers[int(message.text) - 1]
    question_id, question_text = get_random_question()

    if question_id and question_text:
        with open(txt_file, 'a', encoding='utf-8') as file:
            file.write(f"{question_id}. {question_text}\n")
            file.write(f"{question_id}. Выбран ответ: {selected_answer}\n\n")

    await message.answer(f"Вы выбрали ответ [{selected_answer}]")
    await send_question(message.from_user.id)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
