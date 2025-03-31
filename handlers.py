# handlers.py
import random
import sqlite3
import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import hlink
import requests
from urllib.parse import quote
from datetime import datetime
from utils import (load_mini_questions, get_random_mini_question, format_mini_question_with_answers,
                  reset_mini_quiz_state, load_main_questions, get_random_main_question,
                  format_main_question_with_answers, save_answer_to_db, write_totem_animal_to_db,
                  reset_quiz_state, save_user, save_feedback_to_db, START_PROMPT, TOTEM_ANIMAL_MESSAGE_TEMPLATE)
from keyboards import get_quiz_start_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuizStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_language = State()
    waiting_for_quiz_start = State()
    waiting_for_mini_answer = State()
    waiting_for_main_start = State()
    waiting_for_main_answer = State()

user_name = None
user_language = 'ru'
user_id = None
mini_quiz_started = False
main_quiz_started = False
current_mini_question_id = None
current_mini_question_text = None
current_mini_answer_details = None
current_main_question_id = None
current_main_question_text = None
current_main_answer_details = None
mini_question_count = 0
main_question_count = 0
category_scores = {'Млекопитающие': 0, 'Птицы': 0, 'Рептилии': 0, 'Амфибии': 0}
chosen_category = None
animal_scores = {}
from config import ADMIN_ID

async def start(message: types.Message, state: FSMContext):
    global mini_quiz_started, main_quiz_started, user_language
    mini_quiz_started = False
    main_quiz_started = False
    user_language = 'ru'

    welcome_message = {
        'ru': (
            "Р-р-р! Привет, любитель зверей! \n Я бот Московского зоопарка, и у меня есть миссия:\n "
            "найти твоё тотемное животное! \n Готов узнать, кто ты — хитрый лис \nили, может, гордый павлин? \n\n"
            "Сначала выбери язык!"
        ),
        'en': (
            "Roar! Hello, animal lover!\n I’m the Moscow Zoo bot, and I’m on a mission: \n"
            "to find your totem animal! \nReady to discover if you’re a cunning fox \nor a proud peacock?\n \n"
            "First, choose your language!"
        )
    }

    try:
        with open('logo.jpg', 'rb') as photo:
            await message.bot.send_photo(
                message.chat.id,
                photo,
                caption=welcome_message['ru'],
                reply_markup=None
            )
    except FileNotFoundError:
        await message.bot.send_message(
            message.chat.id,
            welcome_message['ru']
        )

    await QuizStates.waiting_for_language.set()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Русский", callback_data="lang_ru"))
    markup.add(types.InlineKeyboardButton("English", callback_data="lang_en"))
    await message.bot.send_message(
        message.chat.id,
        "Выберите язык / Choose language:",
        reply_markup=markup
    )

async def set_language(callback_query: types.CallbackQuery, state: FSMContext):
    global user_language
    user_language = callback_query.data.split('_')[1]
    await QuizStates.waiting_for_name.set()
    await callback_query.bot.send_message(
        callback_query.from_user.id,
        START_PROMPT[user_language]
    )
    await callback_query.answer()

async def process_name(message: types.Message, state: FSMContext):
    global user_name, user_id
    user_name = message.text
    user_id = save_user(user_name)
    await QuizStates.waiting_for_quiz_start.set()
    await message.bot.send_message(
        message.chat.id,
        "Нажмите, чтобы начать мини-викторину!" if user_language == 'ru' else "Press to start the mini-quiz!",
        reply_markup=get_quiz_start_keyboard("Начать" if user_language == 'ru' else "Start", "mini_quiz_start")
    )

async def process_mini_quiz_start(callback_query: types.CallbackQuery, state: FSMContext):
    global mini_quiz_started, mini_question_count, category_scores
    mini_quiz_started = True
    mini_question_count = 0
    category_scores = {'Млекопитающие': 0, 'Птицы': 0, 'Рептилии': 0, 'Амфибии': 0}
    load_mini_questions(user_language)
    logger.info(f"Mini-quiz started for user {user_name}")
    await QuizStates.waiting_for_mini_answer.set()
    await callback_query.bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=None)
    await send_mini_question(callback_query.from_user.id, callback_query.bot, state)

async def send_mini_question(user_id, bot, state: FSMContext):
    global current_mini_question_id, current_mini_question_text, current_mini_answer_details, mini_question_count
    if mini_question_count >= 5:
        await finish_mini_quiz(user_id, bot, state)
        return

    mini_question_count += 1
    current_mini_question_id, current_mini_question_text = get_random_mini_question()
    if current_mini_question_id and current_mini_question_text:
        question_text, current_mini_answer_details = format_mini_question_with_answers(
            current_mini_question_id, f"Вопрос {mini_question_count}/5: {current_mini_question_text}", user_language
        )
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton("1", callback_data="mini_answer_0"),
                types.InlineKeyboardButton("2", callback_data="mini_answer_1"),
                types.InlineKeyboardButton("3", callback_data="mini_answer_2"),
                types.InlineKeyboardButton("4", callback_data="mini_answer_3")
            ]
        ])
        await bot.send_message(user_id, question_text, reply_markup=markup)

async def process_mini_answer(callback_query: types.CallbackQuery, state: FSMContext):
    global current_mini_answer_details, category_scores, mini_question_count
    try:
        selected_index = int(callback_query.data.split('_')[2])
        selected_detail = current_mini_answer_details[selected_index]
        category = selected_detail['category']
        category_scores[category] += 1
        await callback_query.bot.send_message(
            callback_query.from_user.id,
            f"Вы выбрали: {selected_detail['answer']}" if user_language == 'ru' else f"You chose: {selected_detail['answer']}"
        )
        await callback_query.bot.edit_message_reply_markup(
            callback_query.from_user.id,
            callback_query.message.message_id,
            reply_markup=None
        )
        await send_mini_question(callback_query.from_user.id, callback_query.bot, state)
    except (IndexError, ValueError) as e:
        logger.error(f"Ошибка обработки ответа: {e}")
        await callback_query.answer("Ошибка, попробуйте снова." if user_language == 'ru' else "Error, try again.")

async def finish_mini_quiz(user_id, bot, state: FSMContext):
    global category_scores, chosen_category
    chosen_category = max(category_scores, key=category_scores.get)
    result_message = (
        f"Ваш вид: {chosen_category}!\n"
        f"Теперь найдём ваше тотемное животное среди {chosen_category}!" if user_language == 'ru' else
        f"Your type: {chosen_category}!\n"
        f"Now let’s find your totem animal among {chosen_category}!"
    )
    await bot.send_message(user_id, result_message, reply_markup=get_quiz_start_keyboard(
        "Продолжить" if user_language == 'ru' else "Continue", "main_quiz_start"
    ))
    await QuizStates.waiting_for_main_start.set()
    reset_mini_quiz_state()

async def process_main_quiz_start(callback_query: types.CallbackQuery, state: FSMContext):
    global main_quiz_started, main_question_count, animal_scores
    main_quiz_started = True
    main_question_count = 0
    animal_scores = {}
    load_main_questions(user_language)
    logger.info(f"Main quiz started for user {user_name} in category {chosen_category}")
    await QuizStates.waiting_for_main_answer.set()
    await callback_query.bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=None)
    await send_main_question(callback_query.from_user.id, callback_query.bot, state)

async def send_main_question(user_id, bot, state: FSMContext):
    global current_main_question_id, current_main_question_text, current_main_answer_details, main_question_count
    if main_question_count >= 20:
        await finish_main_quiz(user_id, bot, state)
        return

    main_question_count += 1
    current_main_question_id, current_main_question_text = get_random_main_question()
    if current_main_question_id and current_main_question_text:
        question_text, current_main_answer_details = format_main_question_with_answers(
            current_main_question_id, main_question_count, chosen_category, user_language
        )
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton("1", callback_data="main_answer_0"),
                types.InlineKeyboardButton("2", callback_data="main_answer_1"),
                types.InlineKeyboardButton("3", callback_data="main_answer_2"),
                types.InlineKeyboardButton("4", callback_data="main_answer_3")
            ]
        ])
        await bot.send_message(user_id, question_text, reply_markup=markup)

async def process_main_answer(callback_query: types.CallbackQuery, state: FSMContext):
    global current_main_answer_details, animal_scores, main_question_count
    try:
        selected_index = int(callback_query.data.split('_')[2])
        selected_detail = current_main_answer_details[selected_index]
        animal_name = selected_detail['animal']
        animal_scores[animal_name] = animal_scores.get(animal_name, 0) + 1
        save_answer_to_db(user_id, current_main_question_id, selected_detail['answer'], selected_detail)
        await callback_query.bot.send_message(
            callback_query.from_user.id,
            f"Вы выбрали: {selected_detail['answer']}" if user_language == 'ru' else f"You chose: {selected_detail['answer']}"
        )
        await callback_query.bot.edit_message_reply_markup(
            callback_query.from_user.id,
            callback_query.message.message_id,
            reply_markup=None
        )
        await send_main_question(callback_query.from_user.id, callback_query.bot, state)
    except (IndexError, ValueError) as e:
        logger.error(f"Ошибка обработки ответа: {e}")
        await callback_query.answer("Ошибка, попробуйте снова." if user_language == 'ru' else "Error, try again.")

async def finish_main_quiz(user_id, bot, state: FSMContext):
    global animal_scores
    totem_animal = max(animal_scores, key=animal_scores.get)
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT page_url, image_url FROM animals WHERE name = ?', (totem_animal,))
    page_url, image_url = cursor.fetchone()
    conn.close()

    write_totem_animal_to_db(user_id, totem_animal, page_url, image_url)
    result_message = TOTEM_ANIMAL_MESSAGE_TEMPLATE[user_language].format(
        user_name=user_name, animal_name=totem_animal, page_url=page_url
    )

    # Создаём клавиатуру с кнопками
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Начать снова" if user_language == 'ru' else "Start Again", callback_data="restart_quiz"),
        types.InlineKeyboardButton("Поделиться с друзьями" if user_language == 'ru' else "Share with Friends", callback_data="share_result"),
        types.InlineKeyboardButton("Узнать об опеке" if user_language == 'ru' else "Learn About Guardianship", url="https://moscowzoo.ru/about/guardianship"),
        types.InlineKeyboardButton("Оставить отзыв" if user_language == 'ru' else "Leave Feedback", callback_data="leave_feedback")
    )

    await bot.send_photo(user_id, image_url, caption=result_message, parse_mode='Markdown', reply_markup=markup)
    await state.finish()
    reset_quiz_state()

# Обработчик "Начать снова"
async def process_restart_quiz(callback_query: types.CallbackQuery, state: FSMContext):
    global mini_quiz_started, main_quiz_started, mini_question_count, category_scores, animal_scores
    mini_quiz_started = False
    main_quiz_started = False
    mini_question_count = 0
    category_scores = {'Млекопитающие': 0, 'Птицы': 0, 'Рептилии': 0, 'Амфибии': 0}
    animal_scores = {}
    await QuizStates.waiting_for_quiz_start.set()
    await callback_query.bot.send_message(
        callback_query.from_user.id,
        "Нажмите, чтобы начать мини-викторину!" if user_language == 'ru' else "Press to start the mini-quiz!",
        reply_markup=get_quiz_start_keyboard("Начать" if user_language == 'ru' else "Start", "mini_quiz_start")
    )
    await callback_query.bot.edit_message_reply_markup(
        callback_query.from_user.id, callback_query.message.message_id, reply_markup=None
    )
    await callback_query.answer()

# Обработчик "Поделиться с друзьями"
async def process_share_result(callback_query: types.CallbackQuery):
    share_text = (
        f"Я прошёл викторину Московского зоопарка и узнал, что моё тотемное животное — {max(animal_scores, key=animal_scores.get)}! "
        f"Пройди и ты: t.me/MoscowZooBot" if user_language == 'ru' else
        f"I completed the Moscow Zoo quiz and found out my totem animal is {max(animal_scores, key=animal_scores.get)}! "
        f"Try it yourself: t.me/MoscowZooBot"
    )
    await callback_query.bot.send_message(
        callback_query.from_user.id,
        "Поделитесь с друзьями:" if user_language == 'ru' else "Share with friends:",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Поделиться" if user_language == 'ru' else "Share", url=f"https://t.me/share/url?url={quote(share_text)}")
        )
    )
    await callback_query.answer()

# Обработчик "Оставить отзыв"
async def process_leave_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    await QuizStates.waiting_for_feedback.set()
    await callback_query.bot.send_message(
        callback_query.from_user.id,
        "Напишите ваш отзыв:" if user_language == 'ru' else "Write your feedback:"
    )
    await callback_query.answer()

# Обработчик ввода отзыва
async def process_feedback(message: types.Message, state: FSMContext):
    text = message.text  # Замени feedback_text на text
    save_feedback_to_db(message.from_user.id, text)
    await message.bot.send_message(
        message.chat.id,
        f"Ваш отзыв сохранён: {text}" if user_language == 'ru' else f"Your feedback is saved: {text}"
    )
    await state.finish()

# Добавь новое состояние в QuizStates
class QuizStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_language = State()
    waiting_for_quiz_start = State()
    waiting_for_mini_answer = State()
    waiting_for_main_start = State()
    waiting_for_main_answer = State()
    waiting_for_feedback = State()  # Новое состояние

# Обнови register_handlers
def register_handlers(dp: Dispatcher, bot):
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_callback_query_handler(set_language, lambda c: c.data.startswith('lang_'), state=QuizStates.waiting_for_language)
    dp.register_message_handler(process_name, lambda message: message.text and not message.text.startswith('/'), state=QuizStates.waiting_for_name)
    dp.register_callback_query_handler(process_mini_quiz_start, lambda c: c.data == 'mini_quiz_start', state=QuizStates.waiting_for_quiz_start)
    dp.register_callback_query_handler(process_mini_answer, lambda c: c.data.startswith('mini_answer_'), state=QuizStates.waiting_for_mini_answer)
    dp.register_callback_query_handler(process_main_quiz_start, lambda c: c.data == 'main_quiz_start', state=QuizStates.waiting_for_main_start)
    dp.register_callback_query_handler(process_main_answer, lambda c: c.data.startswith('main_answer_'), state=QuizStates.waiting_for_main_answer)
    dp.register_callback_query_handler(process_restart_quiz, lambda c: c.data == 'restart_quiz', state='*')
    dp.register_callback_query_handler(process_share_result, lambda c: c.data == 'share_result', state='*')
    dp.register_callback_query_handler(process_leave_feedback, lambda c: c.data == 'leave_feedback', state='*')
    dp.register_message_handler(process_feedback, state=QuizStates.waiting_for_feedback)