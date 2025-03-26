# utils.py
import sqlite3
import json
import random
from datetime import datetime

questions = None
answers = None
question_numbers = []

def load_questions(language='ru'):
    global questions, question_numbers
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT id, text_{language} FROM questions')
    questions = {row[0]: {'question': row[1]} for row in cursor.fetchall()}
    question_numbers = list(questions.keys())
    conn.close()
    return questions

def get_random_question():
    global question_numbers
    if question_numbers:
        question_id = random.choice(question_numbers)
        question_text = questions[question_id]['question']
        question_numbers.remove(question_id)
        return question_id, question_text
    return None, None

def format_question_with_answers(question_text, question_count, language='ru'):
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, category, page_url, image_url, answers FROM animals')
    animals_data = cursor.fetchall()
    conn.close()

    categories = ["Млекопитающие", "Птицы", "Рептилии", "Амфибии"]
    answers = []
    answer_details = []

    for category_id, category in enumerate(categories, start=1):
        category_animals = [a for a in animals_data if a[2] == category]
        if not category_animals:
            print(f"Warning: No animals found for category {category}")
            continue
        animal = random.choice(category_animals)
        animal_answers = json.loads(animal[5])[language]
        answer = random.choice(animal_answers)
        answers.append(answer)
        answer_details.append({
            "category": category,
            "animal": animal[1],
            "answer": answer,
            "category_id": category_id,
            "animal_id": animal[0],
            "image_url": animal[4],
            "page_url": animal[3]
        })

    formatted_text = f"Вопрос {question_count}/20: {question_text}\n" if language == 'ru' else f"Question {question_count}/20: {question_text}\n"
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
    global quiz_started, questions, answers, current_question_id, current_question_text, current_answer_details, totem_animal_details, question_count
    quiz_started = False
    questions = None
    answers = None
    current_question_id = None
    current_question_text = None
    current_answer_details = None
    totem_animal_details = None
    question_count = 0

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
        "Посмотрите изображение вашего тотемного животного и узнайте больше о нем на странице Московского зоопарка.\n"
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
    'ru': "Привет! \nЯ бот-викторина Московского зоопарка.\n\nНапишите Ваше имя?",
    'en': "Hello! \nI’m the Moscow Zoo quiz bot.\n\nPlease enter your name:"
}