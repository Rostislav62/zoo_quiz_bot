# db_setup.py
import sqlite3

def init_db():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL
        )
    ''')

    # Таблица ответов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id TEXT,
            answer TEXT,
            animal_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Таблица статистики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            animal_id INTEGER PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    ''')

    # Таблица вопросов (два языка)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT NOT NULL,
            text_ru TEXT NOT NULL,
            text_en TEXT NOT NULL,
            PRIMARY KEY (id)
        )
    ''')

    # Таблица животных (ответы в JSON с ru и en)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            page_url TEXT,
            image_url TEXT,
            answers TEXT  -- JSON с {"ru": [...], "en": [...]}
        )
    ''')

    # Таблица отзывов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("База данных создана.")

if __name__ == '__main__':
    init_db()