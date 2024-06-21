# # utils.py
# # Утилиты и вспомогательные функции.

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

def format_question_with_answers(question_text):
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
        answers.append(answer)
        answer_details.append({
            "category": category,
            "animal": animal,
            "answer": answer,
            "category_id": category_id,
            "animal_id": animal_id,
            "image_url": animal_data.get('image_url', ''),
            "page_url": animal_data.get('page_url', '')
        })

    random.shuffle(answers)
    formatted_text = f"{question_text}\n"
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
