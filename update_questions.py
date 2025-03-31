# update_questions.py
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_questions():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Очищаем таблицу questions
    cursor.execute('DELETE FROM questions')

    # 20 вопросов на русском и английском
    questions = [
        ("Как ты приветствуешь утро?", "How do you greet the morning?"),
        ("Что ты делаешь, увидев вкусняшку?", "What do you do when you see a treat?"),
        ("Где ты прячешь свои сокровища?", "Where do you hide your treasures?"),
        ("Как ты здороваешься с друзьями?", "How do you greet your friends?"),
        ("Как ты спасаешься от жары?", "How do you escape the heat?"),
        ("Как ты отдыхаешь в свободное время?", "How do you relax in your free time?"),
        ("Что ты делаешь, забравшись повыше?", "What do you do when you climb up high?"),
        ("Как ты справляешься с холодом?", "How do you deal with the cold?"),
        ("Как ты развлекаешься ночью?", "How do you have fun at night?"),
        ("Какой у тебя коронный номер?", "What’s your signature move?"),
        ("Как ты собираешь компанию?", "How do you gather your crew?"),
        ("Что ты делаешь, промокнув?", "What do you do when you get wet?"),
        ("Как ты демонстрируешь свою крутость?", "How do you show off your coolness?"),
        ("Где бы ты устроил своё жилище?", "Where would you set up your home?"),
        ("Как ты реагируешь на громкие звуки?", "How do you react to loud noises?"),
        ("Как ты ведёшь себя в воде?", "How do you behave in water?"),
        ("Как ты провожаешь день?", "How do you bid the day farewell?"),
        ("Что ты делаешь, когда лень шевелиться?", "What do you do when you’re too lazy to move?"),
        ("Как ты охраняешь своё пространство?", "How do you guard your space?"),
        ("Какой у тебя скрытый талант?", "What’s your hidden talent?")
    ]

    # Заполняем таблицу questions
    for i, (text_ru, text_en) in enumerate(questions, 1):
        cursor.execute('INSERT INTO questions (id, text_ru, text_en) VALUES (?, ?, ?)', (i, text_ru, text_en))
        logger.info(f"Добавлен вопрос {i}: {text_ru} / {text_en}")

    conn.commit()
    conn.close()
    logger.info("20 вопросов добавлены в таблицу questions.")

if __name__ == "__main__":
    update_questions()