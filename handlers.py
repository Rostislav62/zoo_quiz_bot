# handlers.py
# Обработчики команд и сообщений.

import random
import string
import logging  # Добавлено для отладки (Grok)
from aiogram import types, Dispatcher
from aiogram.utils.markdown import hlink  # Добавлено для форматирования ссылок в Markdown
from utils import load_questions, get_random_question, format_question_with_answers, save_answer_to_file, \
    write_totem_animal_to_file, reset_quiz_state, TOTEM_ANIMAL_MESSAGE_TEMPLATE, START_MESSAGE_TEMPLATE, START_PROMPT
from keyboards import get_quiz_start_keyboard, get_quiz_keyboard

# Настройка логирования для отладки (Grok)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные для хранения состояния викторины и информации о пользователе
user_name = None  # Имя пользователя
quiz_started = False  # Флаг начала викторины
questions = None  # Список вопросов для викторины
answers = None  # Список ответов для текущего вопроса
txt_file = None  # Имя файла для записи ответов
current_question_id = None  # Идентификатор текущего вопроса
current_question_text = None  # Текст текущего вопроса
current_answer_details = None  # Детали ответов для текущего вопроса
totem_animal_scores = {}  # Словарь для подсчёта баллов животных (Grok)
animal_details_map = {}  # Словарь для хранения деталей всех животных (Grok)
totem_animal_details = None  # Детали тотемного животного
question_count = 0  # Счетчик вопросов


async def start(message: types.Message):
    """
    Инициализация викторины при запуске, загрузка вопросов, отправка логотипа и приветственного сообщения.
    """
    global quiz_started, answers, txt_file, questions, question_count, totem_animal_scores, animal_details_map
    quiz_started = False  # Сброс флага начала викторины
    answers = []  # Очистка списка ответов
    questions = load_questions()  # Загрузка вопросов
    question_count = 0  # Сброс счетчика вопросов
    totem_animal_scores = {}  # Сброс баллов животных (Grok)
    animal_details_map = {}  # Сброс деталей животных (Grok)

    # Новое приветствие в стиле зоопарка (Grok)
    welcome_message = (
        "Р-р-р! Привет, любитель зверей! Я бот Московского зоопарка, и у меня есть миссия: "
        "найти твоё тотемное животное! Готов узнать, кто ты — хитрый лис или, может, гордый павлин? "
        "Напиши своё имя, и погнали в викторину!"
    )

    # Отправка логотипа, если он есть
    try:
        with open('logo.jpg', 'rb') as photo:
            await message.bot.send_photo(message.chat.id, photo, caption=welcome_message)
    except FileNotFoundError:
        # Если логотипа нет, отправляем только текст (Grok)
        await message.bot.send_message(message.chat.id, welcome_message)


async def process_name(message: types.Message):
    """
    Обработка имени пользователя, создание файла для записи ответов и отправка сообщения с инструкциями.
    """
    global user_name, txt_file
    user_name = message.text  # Сохранение имени пользователя

    random_numbers = ''.join(random.choices(string.digits, k=6))  # Создание случайного числа из 6 цифр
    txt_file = f"{user_name.replace(' ', '_')}_{random_numbers}.txt"  # Создание имени файла для записи ответов

    # Создание и запись в файл информации о пользователе
    with open(txt_file, 'w', encoding='utf-8') as file:
        file.write(f"{user_name}\n\n")  # запись в файл информации о пользователе

    # Новое сообщение с кнопкой в стиле зоопарка (Grok)
    start_message = (
        f"Привет, {user_name}! Я готов провести тебя по джунглям вопросов и найти твоего тотемного зверя. "
        "Жми кнопку ниже, и начнём!"
    )
    await message.bot.send_message(
        message.chat.id, start_message,
        reply_markup=get_quiz_start_keyboard("Начать викторину", "quiz_start")  # кнопка старта викторины
    )


async def process_quiz_start(callback_query: types.CallbackQuery):
    """
    Инициализация состояния викторины, сброс счетчика вопросов и тотемного животного, отправка первого вопроса.
    """
    global quiz_started, questions, question_count, totem_animal_details, totem_animal_scores, animal_details_map
    quiz_started = True
    question_count = 0  # Сброс счетчика вопросов
    totem_animal_details = None  # Сброс тотемного животного
    totem_animal_scores = {}  # Сброс баллов животных (Grok)
    animal_details_map = {}  # Сброс деталей животных (Grok)

    # Перезагружаем вопросы при каждом старте (Grok)
    questions = load_questions()  # Это обновит question_numbers в utils.py
    logger.info(f"Quiz started for user {user_name}, questions reloaded: {len(questions)}")  # Отладка (Grok)

    await callback_query.answer()  # Отправка подтверждения нажатия кнопки пользователю
    await callback_query.bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                                       reply_markup=None)  # Удаление кнопки "Начать викторину"
    await send_question(callback_query.from_user.id, callback_query.bot)  # Отправка первого вопроса пользователю


async def send_question(user_id, bot):
    """
    Отправка вопроса пользователю, если количество вопросов не превышает 20.
    """
    global answers, current_question_id, current_question_text, current_answer_details, question_count
    if question_count >= 20:  # Объявление окончания викторины после 20 вопросов (Grok)
        await bot.send_message(user_id, "Викторина окончена! Сейчас узнаем твоё тотемное животное...",
                               reply_markup=types.ReplyKeyboardRemove())  # Удаление кнопок для ответов
        await announce_totem_animal(user_id, bot)  # Объявление тотемного животного
        return

    question_count += 1  # Увеличение счетчика вопросов
    current_question_id, current_question_text = get_random_question()  # Получение случайного вопроса и его ID
    if current_question_id and current_question_text:  # Проверка наличия ID и текста вопроса
        question_text_with_answers, current_answer_details = format_question_with_answers(
            current_question_text, question_count)  # Форматирование вопроса с номером (Grok)
        answers = [detail['answer'] for detail in current_answer_details]  # Извлечение списка ответов из деталей

        # Сохранение деталей всех животных в animal_details_map (Grok)
        for detail in current_answer_details:
            animal_details_map[detail['animal_id']] = detail

        await bot.send_message(user_id, f"{question_text_with_answers}",
                               reply_markup=get_quiz_keyboard())  # Отправка вопроса и клавиатуры с вариантами ответов пользователю
    else:
        logger.error(f"No questions available for user {user_name}")  # Отладка (Grok)
        await announce_totem_animal(user_id,
                                    bot)  # Объявление тотемного животного, если вопросы закончились или не найдены


async def process_quiz_answer(message: types.Message):
    """
    Обработка ответа пользователя, сохранение ответа в файл, подсчёт баллов для тотемного животного (Grok).
    """
    global answers, txt_file, current_question_id, current_question_text, current_answer_details, totem_animal_details, question_count, totem_animal_scores
    try:
        selected_index = int(
            message.text) - 1  # Преобразование индекса текста сообщения в целое число и уменьшение на 1
        selected_answer = answers[selected_index]  # Получение выбранного ответа из списка ответов по индексу
        selected_detail = current_answer_details[
            selected_index]  # Получение деталей выбранного ответа из текущих деталей ответов по индексу

        # Подсчёт баллов для животного (Grok)
        animal_id = selected_detail['animal_id']
        totem_animal_scores[animal_id] = totem_animal_scores.get(animal_id, 0) + 1
        if question_count == 20:  # На последнем вопросе определяем тотемное животное (Grok)
            max_animal_id = max(totem_animal_scores, key=totem_animal_scores.get)
            totem_animal_details = animal_details_map[max_animal_id]  # Берём детали из сохранённого словаря (Grok)

    except IndexError:  # Обработка исключения, если выбранный индекс выходит за пределы списка
        await message.answer(
            "Некорректный выбор. Пожалуйста, выберите один из предложенных вариантов.")  # Отправка сообщения пользователю о некорректном выборе
        return  # Завершение выполнения функции в случае исключения

    save_answer_to_file(txt_file, current_question_id, current_question_text, selected_answer,
                        selected_detail)  # Сохранение ответа пользователя в файл

    await message.answer(
        f"Вы выбрали ответ [{selected_answer}]")  # Отправка сообщения пользователю с подтверждением выбранного ответа
    await send_question(message.from_user.id, message.bot)  # Отправка следующего вопроса пользователю


async def announce_totem_animal(user_id, bot):
    """
    Объявление тотемного животного, отправка сообщения и фото, запись информации о тотемном животном в файл, сброс состояния викторины.
    """
    global totem_animal_details, user_name, txt_file, quiz_started, questions, answers, current_question_id, \
        current_question_text, current_answer_details, question_count

    try:
        if totem_animal_details:  # Проверка, что информация о тотемном животном существует
            animal_name = totem_animal_details['animal']  # Получение имени тотемного животного
            image_url = totem_animal_details.get('image_url', '')  # Получение URL изображения (пустая строка, если нет)
            page_url = totem_animal_details.get('page_url', '')  # Получение URL страницы (пустая строка, если нет)

            # Улучшено: добавлено описание животного и фото (Grok)
            if animal_name.upper() == "КРАСНЫЙ ФЛАМИНГО":
                description = "Эта грациозная птица обожает стоять на одной ноге и красоваться перед всеми!"
            else:
                description = "Этот обитатель ждёт своего опекуна в Московском зоопарке."

            message_text = (
                f"Ура, {user_name}! Твоё тотемное животное — **{animal_name}**! "
                f"{description} Хочешь помочь? Стань опекуном: "
                f"{hlink('подробности тут', 'https://moscowzoo.ru/about/guardianship')} "
                f"или пиши на zoofriends@moscowzoo.ru, +79629713875!"
            )

            # Отправка фото и сообщения
            if image_url:  # Проверка, что URL изображения не пустой
                await bot.send_photo(user_id, photo=image_url, caption=message_text, parse_mode='Markdown')
            else:
                await bot.send_message(user_id, message_text, parse_mode='Markdown')

            # Кнопки для взаимодействия (Grok)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Начать снова", callback_data="quiz_restart"))
            markup.add(types.InlineKeyboardButton("Узнать об опеке", url="https://moscowzoo.ru/about/guardianship"))
            markup.add(types.InlineKeyboardButton("Поделиться",
                                                  switch_inline_query=f"Моё тотемное животное — {animal_name}! Попробуй и ты: @ZooQuizBot2025_bot"))

            await bot.send_message(user_id, "Конец викторины. Что дальше?", reply_markup=markup)

            # Запись информации о тотемном животном в файл
            write_totem_animal_to_file(txt_file, animal_name, page_url, image_url)

    except Exception as e:  # Обработка исключений, если возникла ошибка
        await bot.send_message(user_id, f"Произошла ошибка: {e}")  # Отправка сообщения об ошибке


async def restart_quiz(callback_query: types.CallbackQuery):
    """
    Перезапуск викторины, запись в файл о начале новой викторины, эмуляция ввода имени (Grok).
    """
    global txt_file, quiz_started
    logger.info(f"Restart quiz triggered for user {user_name}")  # Отладка (Grok)

    reset_quiz_state()  # Сброс всех глобальных переменных, кроме user_name и txt_file
    quiz_started = False  # Убедимся, что флаг сброшен (Grok)

    with open(txt_file, 'a', encoding='utf-8') as file:  # Открытие текстового файла в режиме добавления (append)
        file.write("Новая викторина\n\n")  # Запись строки "Новая викторина" и двух переводов строки в файл

    # Эмуляция ввода имени: отправляем сообщение как в process_name (Grok)
    start_message = (
        f"Привет, {user_name}! Я готов провести тебя по джунглям вопросов и найти твоего тотемного зверя. "
        "Жми кнопку ниже, и начнём снова!"
    )
    await callback_query.bot.send_message(
        callback_query.from_user.id, start_message,
        reply_markup=get_quiz_start_keyboard("Начать викторину", "quiz_start")
    )
    await callback_query.answer()  # Подтверждение нажатия кнопки


def register_handlers(dp: Dispatcher, bot):
    """
    Регистрация всех обработчиков команд и сообщений.
    """
    dp.register_message_handler(start, commands=['start'])  # Регистрация обработчика для команды /start
    dp.register_message_handler(process_name,
                                lambda message: message.text and not message.text.startswith(
                                    '/') and not quiz_started)  # Регистрация обработчика для ввода имени
    dp.register_callback_query_handler(process_quiz_start, lambda
        c: c.data == 'quiz_start')  # Регистрация обработчика для кнопки "Начать викторину"
    dp.register_callback_query_handler(restart_quiz, lambda
        c: c.data == 'quiz_restart')  # Регистрация обработчика для кнопки "Начать снова"
    dp.register_message_handler(process_quiz_answer,
                                lambda message: quiz_started and message.text in ["1", "2", "3",
                                                                                  "4"])  # Регистрация обработчика для ответов на вопросы