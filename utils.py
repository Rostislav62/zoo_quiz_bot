# utils.py
import sqlite3
import json
import random
from datetime import datetime

questions = None
answers = None
question_numbers = []
mini_questions = None
mini_question_numbers = []
main_questions = None
main_question_numbers = []

def load_mini_questions(language='ru'):
    global mini_questions, mini_question_numbers
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT id, text_{language} FROM mini_quiz_questions')
    mini_questions = {row[0]: {'question': row[1]} for row in cursor.fetchall()}
    mini_question_numbers = list(mini_questions.keys())
    conn.close()
    return mini_questions

def get_random_mini_question():
    global mini_question_numbers
    if mini_question_numbers:
        question_id = random.choice(mini_question_numbers)
        question_text = mini_questions[question_id]['question']
        mini_question_numbers.remove(question_id)
        return question_id, question_text
    return None, None

def format_mini_question_with_answers(question_id, question_text, language='ru'):
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT category, text_{language} FROM mini_quiz_answers WHERE question_id = ?', (question_id,))
    answers_data = cursor.fetchall()
    conn.close()

    answers = []
    answer_details = []
    for i, (category, text) in enumerate(answers_data, 1):
        answers.append(f"{i}. {text}")
        answer_details.append({"category": category, "answer": text})

    formatted_text = f"{question_text}\n" + "\n".join(answers)
    return formatted_text, answer_details

def reset_mini_quiz_state():
    global mini_questions, mini_question_numbers
    mini_questions = None
    mini_question_numbers = []

def load_main_questions(language='ru'):
    global main_questions, main_question_numbers
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT id, text_{language} FROM questions')
    main_questions = {row[0]: {'question': row[1]} for row in cursor.fetchall()}
    main_question_numbers = list(main_questions.keys())
    conn.close()
    return main_questions

def get_random_main_question():
    global main_question_numbers
    if main_question_numbers:
        question_id = random.choice(main_question_numbers)
        question_text = main_questions[question_id]['question']
        main_question_numbers.remove(question_id)
        return question_id, question_text
    return None, None

def format_main_question_with_answers(question_id, question_count, category, language='ru', max_questions=20):
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, category, page_url, image_url, answers FROM animals WHERE is_active = 1 AND category = ?', (category,))
    animals_data = cursor.fetchall()
    conn.close()

    selected_animals = random.sample(animals_data, 4)
    answers = []
    answer_details = []

    for animal in selected_animals:
        animal_answers = json.loads(animal[5])[language]
        answer = animal_answers.get(str(question_id), "")
        answers.append(answer)
        answer_details.append({
            "category": animal[2],
            "animal": animal[1],
            "answer": answer,
            "animal_id": animal[0],
            "image_url": animal[4],
            "page_url": animal[3]
        })

    formatted_text = f"Вопрос {question_count}/{max_questions}: {main_questions[question_id]['question']}\n" if language == 'ru' else f"Question {question_count}/{max_questions}: {main_questions[question_id]['question']}\n"
    for i, answer in enumerate(answers, start=1):
        formatted_text += f"{i}. {answer}\n"
    return formatted_text.strip(), answer_details

def save_answer_to_db(user_id, question_id, selected_answer, selected_detail):
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO answers (user_id, question_id, answer, animal_id) VALUES (?, ?, ?, ?)',
                   (user_id, question_id, selected_answer, selected_detail['animal_id']))
    conn.commit()
    conn.close()

def write_totem_animal_to_db(user_id, animal_name, page_url, image_url):
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE statistics SET count = count + 1 WHERE animal_id = (SELECT id FROM animals WHERE name = ?)', (animal_name,))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO statistics (animal_id, count) VALUES ((SELECT id FROM animals WHERE name = ?), 1)', (animal_name,))
    conn.commit()
    conn.close()

def reset_quiz_state():
    global questions, answers, main_questions, main_question_numbers
    questions = None
    answers = None
    main_questions = None
    main_question_numbers = []

def save_user(name):
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, start_date) VALUES (?, ?)', (name, datetime.now().isoformat()))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

TOTEM_ANIMAL_MESSAGE_TEMPLATE = {
    'ru': (
        "{user_name}\n"
        "Поздравляем! Вы прошли викторину\n"
        "Ваше тотемное животное: {animal_name}\n\n"
        "Посмотрите изображение вашего тотемного животного и узнайте больше о нём на странице Московского зоопарка.\n"
        "[Посмотреть страницу]({page_url})\n\n"
        "[«Клуб друзей зоопарка»](https://moscowzoo.ru/about/guardianship) — это помощь в содержании наших "
        "обитателей, а также ваш личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка.\n"
        "Кликните на [«Клуб друзей зоопарка»](https://moscowzoo.ru/about/guardianship) чтобы узнать больше"
    ),
    'en': (
        "{user_name}\n"
        "Congratulations! You've completed the quiz\n"
        "Your totem animal is: {animal_name}\n\n"
        "Check out the image of your totem animal and learn more about it on the Moscow Zoo page.\n"
        "[View page]({page_url})\n\n"
        "[«Friends of the Zoo Club»](https://moscowzoo.ru/about/guardianship) — this is help in maintaining our "
        "inhabitants, as well as your personal contribution to preserving Earth's biodiversity and developing our zoo.\n"
        "Click [«Friends of the Zoo Club»](https://moscowzoo.ru/about/guardianship) to learn more"
    )
}

START_MESSAGE_TEMPLATE = {
    'ru': (
        "Приятно познакомиться, {user_name}!\n"
        "Викторина поможет вам узнать какое у вас тотемное животное.\n"
        "Нажмите на кнопку ниже, чтобы начать викторину."
    ),
    'en': (
        "Nice to meet you, {user_name}!\n"
        "The quiz will help you find out your totem animal.\n"
        "Press the button below to start the quiz."
    )
}

START_PROMPT = {
    'ru': (
        "Добро пожаловать в викторину Московского зоопарка! Узнай своё тотемное животное из 293 обитателей.\n"
        "У нас есть 4 вида: Млекопитающие, Птицы, Рептилии и Амфибии.\n"
        "Сначала определим твой вид, а затем найдём твоего тотема!\n\n"
        "Напишите ваше имя:"
    ),
    'en': (
        "Welcome to the Moscow Zoo quiz! Discover your totem animal from 293 inhabitants.\n"
        "We have 4 types: Mammals, Birds, Reptiles, and Amphibians.\n"
        "First, we’ll determine your type, then find your totem!\n\n"
        "Please enter your name:"
    )
}


def save_feedback_to_db(user_id, text):  # Замени feedback_text на text
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (user_id, text, date) VALUES (?, ?, ?)',
                   (user_id, text, datetime.now().isoformat()))  # Добавляем дату
    conn.commit()
    conn.close()