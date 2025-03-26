# handlers.py
import random
import sqlite3
import string
import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import hlink
import requests  # Уже добавлен для проверки URL
from datetime import datetime  # Добавляем импорт
from utils import load_questions, get_random_question, format_question_with_answers, save_answer_to_db, \
    write_totem_animal_to_db, reset_quiz_state, save_user, TOTEM_ANIMAL_MESSAGE_TEMPLATE, START_MESSAGE_TEMPLATE, START_PROMPT
from keyboards import get_quiz_start_keyboard, get_quiz_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для FSM
class QuizStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_language = State()
    waiting_for_quiz_start = State()
    waiting_for_answer = State()
    waiting_for_feedback = State()

# Глобальные переменные
user_name = None
quiz_started = False
questions = None
answers = None
txt_file = None
current_question_id = None
current_question_text = None
current_answer_details = None
totem_animal_scores = {}
animal_details_map = {}
totem_animal_details = None
question_count = 0
user_id = None
user_language = 'ru'
from config import ADMIN_ID  # Импорт ADMIN_ID из config.py

async def start(message: types.Message, state: FSMContext):
    global quiz_started, user_language
    quiz_started = False
    user_language = 'ru'
    await QuizStates.waiting_for_language.set()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Русский", callback_data="lang_ru"))
    markup.add(types.InlineKeyboardButton("English", callback_data="lang_en"))
    await message.answer("Выберите язык / Choose language:", reply_markup=markup)

async def set_language(callback_query: types.CallbackQuery, state: FSMContext):
    global user_language
    user_language = callback_query.data.split('_')[1]
    await QuizStates.waiting_for_name.set()
    await callback_query.bot.send_message(callback_query.from_user.id, START_PROMPT[user_language])
    await callback_query.answer()

async def process_name(message: types.Message, state: FSMContext):
    global user_name, user_id
    user_name = message.text
    user_id = save_user(user_name)
    await QuizStates.waiting_for_quiz_start.set()
    start_message = START_MESSAGE_TEMPLATE[user_language].format(user_name=user_name)
    await message.bot.send_message(
        message.chat.id, start_message,
        reply_markup=get_quiz_start_keyboard("Начать викторину" if user_language == 'ru' else "Start Quiz", "quiz_start")
    )

# handlers.py (фрагмент изменений)
async def process_quiz_start(callback_query: types.CallbackQuery, state: FSMContext):
    global quiz_started, questions, question_count, totem_animal_details, totem_animal_scores, animal_details_map
    quiz_started = True
    question_count = 0
    totem_animal_details = None
    totem_animal_scores = {}
    animal_details_map = {}
    questions = load_questions(user_language)  # Загружаем вопросы на нужном языке
    logger.info(f"Quiz started for user {user_name}, questions reloaded: {len(questions)}")
    await QuizStates.waiting_for_answer.set()
    await callback_query.bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=None)
    await send_question(callback_query.from_user.id, callback_query.bot, state)

async def send_question(user_id, bot, state: FSMContext):
    global answers, current_question_id, current_question_text, current_answer_details, question_count
    if question_count >= 20:
        await bot.send_message(user_id, "Викторина окончена! Сейчас узнаем твоё тотемное животное..." if user_language == 'ru' else "Quiz finished! Let's find out your totem animal...",
                               reply_markup=types.ReplyKeyboardRemove())
        await announce_totem_animal(user_id, bot, state)
        return

    question_count += 1
    current_question_id, current_question_text = get_random_question()
    if current_question_id and current_question_text:
        question_text_with_answers, current_answer_details = format_question_with_answers(current_question_text, question_count, user_language)  # Передаём язык
        answers = [detail['answer'] for detail in current_answer_details]
        for detail in current_answer_details:
            animal_details_map[detail['animal_id']] = detail
        await bot.send_message(user_id, f"{question_text_with_answers}", reply_markup=get_quiz_keyboard())


async def process_quiz_answer(message: types.Message, state: FSMContext):
    global answers, current_question_id, current_question_text, current_answer_details, totem_animal_details, question_count, totem_animal_scores
    try:
        selected_index = int(message.text) - 1
        selected_answer = answers[selected_index]
        selected_detail = current_answer_details[selected_index]
        animal_id = selected_detail['animal_id']
        totem_animal_scores[animal_id] = totem_animal_scores.get(animal_id, 0) + 1
        save_answer_to_db(user_id, current_question_id, selected_answer, selected_detail)
        if question_count == 20:
            max_animal_id = max(totem_animal_scores, key=totem_animal_scores.get)
            totem_animal_details = animal_details_map[max_animal_id]
            await state.set_state(QuizStates.waiting_for_feedback)
        await message.answer(f"Вы выбрали ответ [{selected_answer}]" if user_language == 'ru' else f"You chose answer [{selected_answer}]")
        await send_question(message.from_user.id, message.bot, state)  # Передаём state
    except IndexError:
        await message.answer("Некорректный выбор. Выберите 1-4." if user_language == 'ru' else "Invalid choice. Choose 1-4.")


async def announce_totem_animal(user_id, bot, state: FSMContext):
    try:
        if totem_animal_details:
            animal_name = totem_animal_details['animal']
            image_url = totem_animal_details.get('image_url', '')  # Получаем URL или пустую строку
            page_url = totem_animal_details.get('page_url', '')
            description = "Этот обитатель ждёт своего опекуна в Московском зоопарке." if user_language == 'ru' else "This inhabitant is waiting for its guardian at the Moscow Zoo."
            if animal_name.upper() == "КРАСНЫЙ ФЛАМИНГО":
                description = "Эта грациозная птица обожает стоять на одной ноге и красоваться перед всеми!" if user_language == 'ru' else "This graceful bird loves standing on one leg and showing off!"
            message_text = TOTEM_ANIMAL_MESSAGE_TEMPLATE[user_language].format(user_name=user_name,
                                                                               animal_name=animal_name,
                                                                               page_url=page_url)

            # Улучшенная проверка image_url
            send_photo = False
            if image_url:  # Проверяем, что строка не пустая
                try:
                    response = requests.head(image_url, timeout=10)  # Увеличиваем таймаут до 10 секунд
                    if response.status_code == 200:
                        send_photo = True
                    else:
                        logger.warning(
                            f"Image URL unavailable for {animal_name}: {image_url}, status: {response.status_code}")
                except requests.RequestException as e:
                    logger.warning(f"Failed to check image URL for {animal_name}: {image_url}, error: {e}")

            if send_photo:
                await bot.send_photo(user_id, photo=image_url, caption=message_text, parse_mode='Markdown')
            else:
                await bot.send_message(user_id, message_text, parse_mode='Markdown')

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Начать снова" if user_language == 'ru' else "Start Again",
                                                  callback_data="quiz_restart"))
            markup.add(
                types.InlineKeyboardButton("Узнать об опеке" if user_language == 'ru' else "Learn About Guardianship",
                                           url="https://moscowzoo.ru/about/guardianship"))
            markup.add(types.InlineKeyboardButton("Поделиться" if user_language == 'ru' else "Share",
                                                  switch_inline_query=f"Моё тотемное животное — {animal_name}! Попробуй и ты: @ZooQuizBot2025_bot" if user_language == 'ru' else f"My totem animal is {animal_name}! Try it: @ZooQuizBot2025_bot"))
            markup.add(types.InlineKeyboardButton("Оставить отзыв" if user_language == 'ru' else "Leave Feedback",
                                                  callback_data="feedback"))
            await bot.send_message(user_id,
                                   "Конец викторины. Что дальше?" if user_language == 'ru' else "End of quiz. What's next?",
                                   reply_markup=markup)
            write_totem_animal_to_db(user_id, animal_name, page_url, image_url)
    except Exception as e:
        await bot.send_message(user_id,
                               f"Произошла ошибка: {e}" if user_language == 'ru' else f"An error occurred: {e}")


async def restart_quiz(callback_query: types.CallbackQuery, state: FSMContext):
    global txt_file, quiz_started
    logger.info(f"Restart quiz triggered for user {user_name}")
    reset_quiz_state()
    quiz_started = False
    await QuizStates.waiting_for_quiz_start.set()
    start_message = START_MESSAGE_TEMPLATE[user_language].format(user_name=user_name)
    await callback_query.bot.send_message(
        callback_query.from_user.id, start_message,
        reply_markup=get_quiz_start_keyboard("Начать викторину" if user_language == 'ru' else "Start Quiz", "quiz_start")
    )
    await callback_query.answer()

async def start_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    await QuizStates.waiting_for_feedback.set()
    await callback_query.bot.send_message(
        callback_query.from_user.id,
        "Напишите ваш отзыв о викторине:" if user_language == 'ru' else "Write your feedback about the quiz:"
    )
    await callback_query.answer()

async def process_feedback(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (user_id, text, date) VALUES (?, ?, ?)',
                   (user_id, message.text, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    await message.answer("Спасибо за ваш отзыв!" if user_language == 'ru' else "Thank you for your feedback!")
    await state.finish()

async def admin_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён." if user_language == 'ru' else "Access denied.")
        return
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT a.name, s.count FROM statistics s JOIN animals a ON s.animal_id = a.id ORDER BY s.count DESC')
    stats = cursor.fetchall()
    conn.close()
    stats_text = "Статистика выбора животных:\n" if user_language == 'ru' else "Animal selection statistics:\n"
    for name, count in stats:
        stats_text += f"{name}: {count}\n"
    await message.answer(stats_text)

async def admin_feedback(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён." if user_language == 'ru' else "Access denied.")
        return
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT u.name, f.text, f.date FROM feedback f JOIN users u ON f.user_id = u.id ORDER BY f.date DESC LIMIT 5')
    feedback = cursor.fetchall()
    conn.close()
    feedback_text = "Последние отзывы:\n" if user_language == 'ru' else "Recent feedback:\n"
    for name, text, date in feedback:
        feedback_text += f"{name} ({date}): {text}\n"
    await message.answer(feedback_text)

def register_handlers(dp: Dispatcher, bot):
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_callback_query_handler(set_language, lambda c: c.data.startswith('lang_'), state=QuizStates.waiting_for_language)
    dp.register_message_handler(process_name, lambda message: message.text and not message.text.startswith('/'), state=QuizStates.waiting_for_name)
    dp.register_callback_query_handler(process_quiz_start, lambda c: c.data == 'quiz_start', state=QuizStates.waiting_for_quiz_start)
    dp.register_message_handler(process_quiz_answer, lambda message: quiz_started and message.text in ["1", "2", "3", "4"], state=QuizStates.waiting_for_answer)
    dp.register_callback_query_handler(restart_quiz, lambda c: c.data == 'quiz_restart', state='*')
    dp.register_callback_query_handler(start_feedback, lambda c: c.data == 'feedback', state='*')
    dp.register_message_handler(process_feedback, state=QuizStates.waiting_for_feedback)
    dp.register_message_handler(admin_stats, commands=['stats'])
    dp.register_message_handler(admin_feedback, commands=['feedback'])