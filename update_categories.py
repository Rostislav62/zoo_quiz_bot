# update_categories.py
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_categories():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Ограничиваем до 40 животных для теста
    # cursor.execute('DELETE FROM animals WHERE id > 293')
    cursor.execute('SELECT id, name FROM animals ORDER BY id LIMIT 293')
    animals = cursor.fetchall()

    # Простое правило распределения по категориям (можно улучшить)
    for animal_id, name in animals:
        name_lower = name.lower()
        if any(word in name_lower for word in ["попугай", "фазан", "орёл", "гусь", "какаду", "павлин", "журавль", "аист",
                                               "сова", "фламинго", "орлан", "утка", "марабу", "сип", "беркут", "выпь",
                                               "кукушка", "кроншнеп", "неясыть", "бородач", "ибис", "вяхирь", "турако",
                                               "монал", "сорока", "голубь", "неясыть", "амазон", "китоглав", "коростель",
                                               "жако", "кумай", "подорлик", "ара", "сыч", "колпица", "канюк", "калао",
                                               "пеликан", "секретарь", "цапля", "трубач", "сойка", "трагопан", "лебедь",
                                               "турухтан", "филин", "ходулочник", "гриф", "шилоклювка", "казуар", "кондор",
                                               "скворец", "сипуха", "пингвин", "ябиру", "орел", "ворон", "могильник", "тукан" ]):
            category = "Птицы"
        elif any(word in name_lower for word in ["змей", "змея", "крокодил", "кобра", "питон", "черепаха", "гадюка", "бушмейстер",
                                                 "кайман", "гюрза", "кайсака", "щитомордник",  "аллигатор", "медянка",
                                                 "удав", "куфия", "тайпан", "хабу", "ботропис", "игуана", "василиск", "анаконда" ]):
            category = "Рептилии"
        elif any(word in name_lower for word in ["лягушка", "жаба", "квакша", "амфиума", "веслоног", "древолаз", "саламандра"]):
            category = "Амфибии"

        elif any(word in name_lower for word in ["капибара"]):
            category = "Млекопитающие"
        else:
            category = "Млекопитающие"  # По умолчанию

        cursor.execute('UPDATE animals SET category = ? WHERE id = ?', (category, animal_id))
        logger.info(f"Обновлена категория для {name}: {category}")

    conn.commit()
    conn.close()
    logger.info("Категории обновлены для 293 животных.")

if __name__ == "__main__":
    update_categories()