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

    # random.shuffle(answers)
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


# utils.py

def get_bot_share_text(animal_name):
    bot_url = "https://t.me/CryptoTutBot_test_bot"
    return (f"Мое тотемное животное -\n {animal_name}! \n"
            f"Узнай свое тотемное животное в викторине Московского зоопарка."
            f"Пройди викторину здесь: {bot_url}")

def get_message_text(user_name, animal_name, page_url):
    return (f"{user_name}\n\n"
            f"Мы ВАС Поздравляем!\n"
            f"Вы прошли викторину и узнали, что ваше тотемное животное:\n"
            f"{animal_name} \n"
            f"Посмотрите изображение вашего тотемного животного и узнайте больше о нем на странице [Московского "
            f"зоопарка.]({page_url})\n\n")

def get_social_share_links(share_text, page_url):
    return (f"Поделитесь своим результатом: \n"
            f"[WhatsApp](https://wa.me/?text={share_text}) "
            f"[Telegram](https://t.me/share/url?url={page_url}&text={share_text}) "
            f"[Facebook](https://www.facebook.com/sharer/sharer.php?u={page_url}&quote={share_text}) "
            f"[Twitter](https://twitter.com/intent/tweet?url={page_url}&text={share_text}) "
            f"[VK](https://vk.com/share.php?url={page_url}&title={share_text})\n\n")

def get_club_info():
    return (f"Кликните на [«Клуб друзей зоопарка»](https://moscowzoo.ru/about/guardianship), и вы узнаете "
            f"что это помощь в содержании наших обитателей, а также ваш личный вклад в дело сохранения "
            f"биоразнообразия Земли и развитие нашего зоопарка.\n")

def save_totem_info_to_file(txt_file, animal_name, page_url, image_url):
    with open(txt_file, 'a', encoding='utf-8') as file:
        file.write("Конец викторины\n")
        file.write(f"Ваше тотемное животное: {animal_name}\n")
        file.write(f"page_url: {page_url}\n")
        file.write(f"image_url: {image_url}\n\n")

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

