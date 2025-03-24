# utils.py
# Утилиты и вспомогательные функции.

import json
import random

questions = None
answers = None
question_numbers = []

def load_questions():
    global questions, question_numbers
    with open('questions.json', 'r', encoding='utf-8') as file:
        questions = json.load(file)
    question_numbers = list(questions.keys())  # Получаем список всех номеров вопросов
    return questions

def get_random_question():
    global question_numbers
    if question_numbers:
        question_id = random.choice(question_numbers)
        question_text = questions[question_id]['question']
        question_numbers.remove(question_id)  # Удаляем выбранный вопрос из списка
        return question_id, question_text
    else:
        return None, None

def format_question_with_answers(question_text, question_count):
    with open('quiz_text.json', 'r', encoding='utf-8') as file:
        quiz_data = json.load(file)

    categories = ["Млекопитающие", "Птицы", "Рептилии", "Амфибии"]
    answers = []
    answer_details = []

    for category_id, category in enumerate(categories, start=1):
        animal = random.choice(list(quiz_data[category].keys()))
        animal_data = quiz_data[category][animal]
        answer = random.choice(animal_data["answers"])
        animal_id = animal_data["animal_id"]
        image_url = animal_data["image_url"]
        page_url = animal_data["page_url"]
        answers.append(answer)
        answer_details.append({
            "category": category,
            "animal": animal,
            "answer": answer,
            "category_id": category_id,
            "animal_id": animal_id,
            "image_url": image_url,
            "page_url": page_url
        })

    # Форматируем текст с номером вопроса (Grok)
    formatted_text = f"Вопрос {question_count}/20: {question_text}\n"
    for i, answer in enumerate(answers, start=1):
        formatted_text += f"{i}. {answer}\n"
    return formatted_text.strip(), answer_details

def save_answer_to_file(txt_file, question_id, question_text, selected_answer, selected_detail):
    with open(txt_file, 'a', encoding='utf-8') as file:
        file.write(f"{question_id}. {question_text}\n")
        file.write(f"Животное: {selected_detail['animal']}\n")
        file.write(f"Ответ: {selected_answer}\n")
        file.write(f"category_id: {selected_detail['category_id']}\n")
        file.write(f"animal_id: {selected_detail['animal_id']}\n\n")

def write_totem_animal_to_file(txt_file, animal_name, page_url, image_url):
    """
    Запись информации о тотемном животном в файл.
    """
    with open(txt_file, 'a', encoding='utf-8') as file:
        file.write("Конец викторины\n")
        file.write(f"Ваше тотемное животное: {animal_name}\n")
        file.write(f"page_url: {page_url}\n")
        file.write(f"image_url: {image_url}\n\n")

def reset_quiz_state():
    """
    Сброс всех глобальных переменных, кроме user_name и txt_file.
    """
    global quiz_started, questions, answers, current_question_id, current_question_text, current_answer_details, totem_animal_details, question_count
    quiz_started = False
    questions = None
    answers = None
    current_question_id = None
    current_question_text = None
    current_answer_details = None
    totem_animal_details = None
    question_count = 0

TOTEM_ANIMAL_MESSAGE_TEMPLATE = (
    "{user_name}\n"
    "Поздравляем! Вы прошли викторину\n"
    "Ваше тотемное животное: {animal_name}\n\n"
    "Посмотрите изображение вашего тотемного животного и узнайте больше о нем на странице Московского зоопарка.\n"
    "[Посмотреть страницу]({page_url})\n\n"
    "[«Клуб друзей зоопарка»](https://moscowzoo.ru/about/guardianship) — это помощь в содержании наших "
    "обитателей, а также ваш личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка.\n"
    "Кликните на [«Клуб друзей зоопарка»](https://moscowzoo.ru/about/guardianship) чтобы узнать больше"
)

START_MESSAGE_TEMPLATE = (
    "Приятно познакомиться, {user_name}!\n"
    "Викторина поможет вам узнать какое у вас тотемное животное.\n"
    "Нажмите на кнопку ниже, чтобы начать викторину."
)

START_PROMPT = (
    "Р-р-р! Привет, любитель зверей! \nЯ бот Московского зоопарка, и у меня есть миссия: \n "
    "найти твоё тотемное животное! \n \n Готов узнать,  \nкто ты — хитрый лис или, \n может, гордый павлин? \n \n "
    "Напиши своё имя, и погнали в викторину!"
)