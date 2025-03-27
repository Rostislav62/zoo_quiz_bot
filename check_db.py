# check_db.py
import sqlite3

def check_db():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Проверка таблицы animals
    cursor.execute('SELECT COUNT(*) FROM animals')
    animals_count = cursor.fetchone()[0]
    print(f"Animals in database: {animals_count}")

    # Проверка таблицы questions
    cursor.execute('SELECT COUNT(*) FROM questions')
    questions_count = cursor.fetchone()[0]
    print(f"Questions in database: {questions_count}")

    # Пример данных из animals
    cursor.execute('SELECT id, name, category FROM animals LIMIT 5')
    animals = cursor.fetchall()
    print("Sample animals:", animals)

    conn.close()

if __name__ == '__main__':
    check_db()