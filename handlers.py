# handlers.py
# Обработчики команд и сообщений.

import random
import string
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from utils import (load_questions, get_random_question, format_question_with_answers, save_answer_to_file,
                   get_bot_share_text, get_message_text, get_social_share_links, get_club_info, save_totem_info_to_file, reset_quiz_state)

from keyboards import get_quiz_start_keyboard, get_quiz_keyboard
from feedback import FeedbackHandler, ContactForm

user_name = None
quiz_started = False
questions = None
answers = None
txt_file = None
current_question_id = None
current_question_text = None
current_answer_details = None
totem_animal_details = None
question_count = 0

async def start(message: types.Message):
    global quiz_started, answers, txt_file, questions, question_count
    quiz_started = False
    answers = []
    questions = load_questions()  # Загружаем вопросы при старте
    question_count = 0

    # Отправка логотипа
    with open('logo.jpg', 'rb') as photo:
        await message.bot.send_photo(message.chat.id, photo)

    await message.bot.send_message(message.chat.id,
                                   "Привет! \nЯ бот-викторина Московского зоопарка.\n\nНапишите Ваше имя?")

async def process_name(message: types.Message, state: FSMContext):
    global user_name, txt_file, quiz_started
    if quiz_started:
        return  # Игнорируем ввод имени, если викторина уже начата

    user_name = message.text

    random_numbers = ''.join(random.choices(string.digits, k=6))
    txt_file = f"{user_name.replace(' ', '_')}_{random_numbers}.txt"

    with open(txt_file, 'w', encoding='utf-8') as file:
        file.write(f"{user_name}\n\n")

    await message.bot.send_message(
        message.chat.id,
        f"Приятно познакомиться, {user_name}!\n"
        f"Викторина поможет вам узнать какое у вас тотемное животное.\n"
        f"Нажмите на кнопку ниже, чтобы начать викторину.",
        reply_markup=get_quiz_start_keyboard("Начало викторины", "quiz_start")
    )
    await state.finish()  # Завершение состояния, чтобы не конфликтовало с другими

async def process_quiz_start(callback_query: types.CallbackQuery):
    global quiz_started, question_numbers, questions, question_count, totem_animal_details
    quiz_started = True
    question_count = 0  # Сброс счетчика вопросов
    totem_animal_details = None  # Сброс тотемного животного

    # Проверяем, что вопросы были загружены
    if questions is None:
        questions = load_questions()

    question_numbers = list(questions.keys())  # Восстанавливаем полный список вопросов
    await callback_query.answer()
    await callback_query.bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                                       reply_markup=None)
    await send_question(callback_query.from_user.id, callback_query.bot)

async def send_question(user_id, bot):
    global answers, current_question_id, current_question_text, current_answer_details, question_count
    if question_count >= 20:  # Объявляем окончание викторины после 20 вопросов
        await announce_totem_animal(user_id, bot)
        return

    question_count += 1
    current_question_id, current_question_text = get_random_question()
    if current_question_id and current_question_text:
        question_text_with_answers, current_answer_details = format_question_with_answers(current_question_text)
        answers = [detail['answer'] for detail in current_answer_details]
        await bot.send_message(user_id, f"{question_text_with_answers}", reply_markup=get_quiz_keyboard())
    else:
        await announce_totem_animal(user_id, bot)

async def process_quiz_answer(message: types.Message):
    global answers, txt_file, current_question_id, current_question_text, current_answer_details, totem_animal_details, question_count
    try:
        selected_index = int(message.text) - 1
        selected_answer = answers[selected_index]
        selected_detail = current_answer_details[selected_index]

        if question_count == 8:  # Устанавливаем тотемное животное на 8-й вопрос
            totem_animal_details = selected_detail

    except IndexError:
        await message.answer("Некорректный выбор. Пожалуйста, выберите один из предложенных вариантов.")
        return

    save_answer_to_file(txt_file, current_question_id, current_question_text, selected_answer, selected_detail)

    await message.answer(f"Вы выбрали ответ [{selected_answer}]")
    await send_question(message.from_user.id, message.bot)

async def announce_totem_animal(user_id, bot):
    global totem_animal_details, user_name, txt_file, quiz_started, questions, answers, current_question_id, current_question_text, current_answer_details, question_count

    try:
        if totem_animal_details:
            animal_name = totem_animal_details['animal']
            image_url = totem_animal_details.get('image_url', '')
            page_url = totem_animal_details.get('page_url', '')

            share_text = get_bot_share_text(animal_name)
            message_text = get_message_text(user_name, animal_name, page_url)
            message_text += get_social_share_links(share_text, page_url)
            message_text += get_club_info()

            # Добавляем инлайн-кнопку "Связаться с сотрудником"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("Связаться с сотрудником", callback_data=f'contact:{txt_file}'))

            # Отправка фото и сообщения
            if image_url:
                await bot.send_photo(user_id, photo=image_url, caption=f"Ваше тотемное животное: {animal_name}")

            await bot.send_message(user_id, text=message_text, parse_mode='Markdown', reply_markup=keyboard)
            await bot.send_message(user_id, "Конец викторины.", reply_markup=types.ReplyKeyboardRemove())
            await bot.send_message(user_id, "Вы можете попробовать еще раз",
                                   reply_markup=get_quiz_start_keyboard("Начать снова", "quiz_restart"))

            save_totem_info_to_file(txt_file, animal_name, page_url, image_url)
            reset_quiz_state()
    except Exception as e:
        await bot.send_message(user_id, f"Произошла ошибка: {e}")
        raise

async def restart_quiz(callback_query: types.CallbackQuery):
    global txt_file
    with open(txt_file, 'a', encoding='utf-8') as file:
        file.write("\n\nНовая викторина\n\n")

    await callback_query.bot.send_message(callback_query.from_user.id, "\n\nНовая викторина\n")
    await process_quiz_start(callback_query)

def register_handlers(dp: Dispatcher, bot):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(process_name,
                                lambda message: message.text and not message.text.startswith('/') and not quiz_started, state='*')
    dp.register_callback_query_handler(process_quiz_start, lambda c: c.data == 'quiz_start')
    dp.register_callback_query_handler(restart_quiz, lambda c: c.data == 'quiz_restart')
    dp.register_message_handler(process_quiz_answer,
                                lambda message: quiz_started and message.text in ["1", "2", "3", "4"], state='*')

    # Регистрация обработчиков для контактной формы
    dp.register_callback_query_handler(FeedbackHandler.start_contact_form, lambda c: c.data.startswith('contact'))
    dp.register_message_handler(FeedbackHandler.process_fullname, state=ContactForm.fullname, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(FeedbackHandler.process_phone, state=ContactForm.phone, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(FeedbackHandler.process_email, state=ContactForm.email, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(FeedbackHandler.process_telegram, state=ContactForm.telegram, content_types=types.ContentTypes.TEXT)

