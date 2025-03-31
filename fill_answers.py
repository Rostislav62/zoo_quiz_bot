# fill_answers.py
import sqlite3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fill_answers():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Ограничиваем до 40 животных (первые 40 по ID)
    cursor.execute('DELETE FROM animals WHERE id > 40')
    cursor.execute('SELECT id, name FROM animals ORDER BY id LIMIT 40')
    animals = cursor.fetchall()

    # 20 вопросов и шаблоны ответов
    questions = [
        "Как ты рычишь по утрам?",
        "Что ты делаешь, когда видишь вкусный обед?",
        "Где бы ты спрятал свою добычу?",
        "Какой у тебя танец приветствия?",
        "Что ты делаешь в жару, чтобы не растаять?",
        "Какой у тебя стиль отдыха в тени?",
        "Что ты делаешь на высоте?",
        "Как ты согреваешь лапы в мороз?",
        "Как ты охотился бы ночью?",
        "Какой твой фирменный трюк?",
        "Как ты зовёшь друзей на вечеринку?",
        "Что ты делаешь с мокрыми лапами?",
        "Как ты показываешь свою силу?",
        "Где бы ты построил своё логово?",
        "Как ты реагируешь на шум?",
        "Что ты делаешь в воде?",
        "Как ты встречаешь закат?",
        "Что ты делаешь, когда лень двигаться?",
        "Как ты защищаешь свою территорию?",
        "Какой у тебя секретный талант?"
    ]

    # Пример шаблонов ответов (на русском и английском)
    templates_ru = [
        "Рычу громко, как {name}!",
        "Хватаю еду лапами, как {name}!",
        "Прячу в гнезде, как {name}!",
        "Танцую с перьями, как {name}!",
        "Прячусь в тени, как {name}!",
        "Лежу важно, как {name}!",
        "Взлетаю высоко, как {name}!",
        "Греюсь у костра, как {name}!",
        "Крадусь тихо, как {name}!",
        "Показываю крылья, как {name}!",
        "Кричу звонко, как {name}!",
        "Трясу перья, как {name}!",
        "Рычу на всех, как {name}!",
        "В норе, как {name}!",
        "Шиплю громко, как {name}!",
        "Плаваю грациозно, как {name}!",
        "Смотрю вдаль, как {name}!",
        "Сплю весь день, как {name}!",
        "Охраняю с рыком, как {name}!",
        "Пою красиво, как {name}!"
    ]

    templates_en = [
        "I roar loudly like {name}!",
        "I grab food with my paws like {name}!",
        "I hide it in my nest like {name}!",
        "I dance with feathers like {name}!",
        "I hide in the shade like {name}!",
        "I rest proudly like {name}!",
        "I soar high like {name}!",
        "I warm up by the fire like {name}!",
        "I sneak quietly like {name}!",
        "I show off my wings like {name}!",
        "I call out loudly like {name}!",
        "I shake my feathers like {name}!",
        "I growl at everyone like {name}!",
        "In a burrow like {name}!",
        "I hiss loudly like {name}!",
        "I swim gracefully like {name}!",
        "I gaze into the distance like {name}!",
        "I sleep all day like {name}!",
        "I guard with a roar like {name}!",
        "I sing beautifully like {name}!"
    ]

    # Заполняем ответы для каждого животного
    for animal_id, name in animals:
        answers = {
            "ru": {str(i+1): templates_ru[i].format(name=name) for i in range(20)},
            "en": {str(i+1): templates_en[i].format(name=name) for i in range(20)}
        }
        answers_json = json.dumps(answers)
        cursor.execute('UPDATE animals SET answers = ? WHERE id = ?', (answers_json, animal_id))
        logger.info(f"Заполнены ответы для {name}")

    conn.commit()
    conn.close()
    logger.info("Ответы для 40 животных добавлены в базу.")

if __name__ == "__main__":
    fill_answers()