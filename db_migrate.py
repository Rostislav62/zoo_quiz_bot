# db_migrate.py
import sqlite3
import json

def migrate_data():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Загрузка данных из localized_data.json
    with open('localized_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Вставка вопросов
    for question in data['questions']:
        cursor.execute('INSERT OR REPLACE INTO questions (id, text_ru, text_en) VALUES (?, ?, ?)',
                       (question['id'], question['text_ru'], question['text_en']))
    print(f"Загружено вопросов: {len(data['questions'])}")

    # Вставка животных
    for animal in data['animals']:
        answers_json = json.dumps(animal['answers'])
        cursor.execute('INSERT OR REPLACE INTO animals (id, name, category, page_url, image_url, answers) VALUES (?, ?, ?, ?, ?, ?)',
                       (animal['id'], animal['name'], animal['category'], animal['page_url'], animal['image_url'], answers_json))
    print(f"Загружено животных: {len(data['animals'])}")

    conn.commit()
    conn.close()
    print("Миграция завершена. Проверьте базу с помощью check_db.py.")

if __name__ == '__main__':
    migrate_data()