# # handlers.py
# # Обработчики команд и сообщений.


import random
import string
from aiogram import types, Dispatcher
from utils import load_questions, get_random_question, format_question_with_answers, save_answer_to_file
from keyboards import get_quiz_start_keyboard, get_quiz_keyboard

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

    await message.bot.send_message(message.chat.id, "Привет! \nЯ бот-викторина Московского зоопарка.\n\nНапишите Ваше имя?")

async def process_name(message: types.Message):
    global user_name, txt_file
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
        reply_markup=get_quiz_start_keyboard()
    )

async def process_quiz_start(callback_query: types.CallbackQuery):
    global quiz_started, question_numbers, questions
    quiz_started = True

    # Проверяем, что вопросы были загружены
    if questions is None:
        questions = load_questions()

    question_numbers = list(questions.keys())  # Восстанавливаем полный список вопросов
    await callback_query.answer()
    await callback_query.bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=None)
    await send_question(callback_query.from_user.id, callback_query.bot)

async def send_question(user_id, bot):
    global answers, current_question_id, current_question_text, current_answer_details, question_count
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

    if question_count >= len(questions):
        await announce_totem_animal(message.from_user.id, message.bot)
    else:
        await message.answer(f"Вы выбрали ответ [{selected_answer}]")
        await send_question(message.from_user.id, message.bot)

async def announce_totem_animal(user_id, bot):
    global totem_animal_details
    if totem_animal_details:
        animal_name = totem_animal_details['animal']
        image_url = totem_animal_details.get('image_url', '')
        page_url = totem_animal_details.get('page_url', '')

        message_text = (
            f"Ваше тотемное животное: {animal_name}\n\n"
            f"Поздравляем! Вы прошли викторину и узнали, что ваше тотемное животное - {animal_name}.\n"
            f"Посмотрите изображение вашего тотемного животного и узнайте больше о нем на странице Московского зоопарка.\n"
            f"[Посмотреть страницу]({page_url})\n\n"
            f"[«Клуб друзей зоопарка»](https://moscowzoo.ru/about/guardianship) — это помощь в содержании наших обитателей, а также ваш личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка.\n"
            f"Кликните на [«Клуб друзей зоопарка»](https://moscowzoo.ru/about/guardianship) чтобы узнать больше"
        )

        await bot.send_photo(user_id, photo=image_url, caption=message_text, parse_mode='Markdown')
        await bot.send_message(user_id, "Конец викторины.", reply_markup=types.ReplyKeyboardRemove())

def register_handlers(dp: Dispatcher, bot):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(process_name, lambda message: message.text and not message.text.startswith('/') and not quiz_started)
    dp.register_callback_query_handler(process_quiz_start, lambda c: c.data == 'quiz_start')
    dp.register_message_handler(process_quiz_answer, lambda message: quiz_started and message.text in ["1", "2", "3", "4"])


