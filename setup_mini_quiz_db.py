# setup_mini_quiz_db.py
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_mini_quiz_db():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Создаём таблицу для вопросов мини-викторины
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mini_quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_ru TEXT NOT NULL,
            text_en TEXT NOT NULL
        )
    ''')

    # Создаём таблицу для ответов мини-викторины
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mini_quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            category TEXT NOT NULL,
            text_ru TEXT NOT NULL,
            text_en TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES mini_quiz_questions(id)
        )
    ''')

    # Очищаем таблицы (если нужно перезаписать)
    cursor.execute('DELETE FROM mini_quiz_questions')
    cursor.execute('DELETE FROM mini_quiz_answers')

    # Вопросы мини-викторины
    questions = [
        ("Где ты чувствуешь себя лучше всего?", "Where do you feel most at home?"),
        ("Как ты любишь передвигаться?", "How do you like to get around?"),
        ("Что ты делаешь, чтобы согреться?", "What do you do to stay warm?"),
        ("Какой у тебя любимый перекус?", "What’s your favorite snack?"),
        ("Как ты общаешься с друзьями?", "How do you chat with friends?")
    ]

    # Добавляем вопросы
    for i, (text_ru, text_en) in enumerate(questions, 1):
        cursor.execute('INSERT INTO mini_quiz_questions (id, text_ru, text_en) VALUES (?, ?, ?)', (i, text_ru, text_en))
        logger.info(f"Добавлен вопрос: {text_ru}")

    # Ответы мини-викторины
    answers = [
        # Вопрос 1: Где ты чувствуешь себя лучше всего?
        (1, "Млекопитающие", "В густом лесу среди деревьев", "In a dense forest among trees"),
        (1, "Птицы", "В небе над землёй", "In the sky above the ground"),
        (1, "Рептилии", "На тёплой сухой земле", "On warm, dry land"),
        (1, "Амфибии", "У воды или в болоте", "By the water or in a swamp"),

        # Вопрос 2: Как ты любишь передвигаться?
        (2, "Млекопитающие", "Бегать или прыгать по земле", "Run or jump on the ground"),
        (2, "Птицы", "Летать или планировать", "Fly or glide"),
        (2, "Рептилии", "Ползать или скользить", "Crawl or slither"),
        (2, "Амфибии", "Плавать или прыгать в воде", "Swim or hop in water"),

        # Вопрос 3: Что ты делаешь, чтобы согреться?
        (3, "Млекопитающие", "Греюсь в шерсти или мехе", "Warm up in fur or wool"),
        (3, "Птицы", "Расправляю перья на солнце", "Fluff my feathers in the sun"),
        (3, "Рептилии", "Лежу на горячем камне", "Bask on a hot rock"),
        (3, "Амфибии", "Прячусь во влажной тени", "Hide in damp shade"),

        # Вопрос 4: Какой у тебя любимый перекус?
        (4, "Млекопитающие", "Сочная трава или мясо", "Juicy grass or meat"),
        (4, "Птицы", "Зёрна или мелкие насекомые", "Grains or small insects"),
        (4, "Рептилии", "Мелкая добыча, проглоченная целиком", "Small prey swallowed whole"),
        (4, "Амфибии", "Водные букашки или растения", "Water bugs or plants"),

        # Вопрос 5: Как ты общаешься с друзьями?
        (5, "Млекопитающие", "Рычу, вою или мяукаю", "Growl, howl, or meow"),
        (5, "Птицы", "Чирикаю или кричу с высоты", "Chirp or call from above"),
        (5, "Рептилии", "Шиплю или молчу", "Hiss or stay silent"),
        (5, "Амфибии", "Квакаю или издаю влажные звуки", "Croak or make wet sounds"),
    ]

    # Добавляем ответы
    for question_id, category, text_ru, text_en in answers:
        cursor.execute('INSERT INTO mini_quiz_answers (question_id, category, text_ru, text_en) VALUES (?, ?, ?, ?)',
                       (question_id, category, text_ru, text_en))
        logger.info(f"Добавлен ответ для вопроса {question_id}, категория {category}: {text_ru}")

    conn.commit()
    conn.close()
    logger.info("База данных для мини-викторины готова.")

if __name__ == "__main__":
    setup_mini_quiz_db()