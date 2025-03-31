# setup_main_quiz_animals.py
import sqlite3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_main_quiz_animals():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Добавляем столбец is_active, если его нет
    try:
        cursor.execute('ALTER TABLE animals ADD COLUMN is_active INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Столбец уже существует

    # Очищаем таблицу answers от старых данных
    cursor.execute('DELETE FROM answers')
    logger.info("Таблица answers очищена от старых данных.")

    # Список 40 животных (по 10 из каждой категории)
    selected_animals = [
        # Млекопитающие
        (1, "АМУРСКИЙ ТИГР"), (2, "БЕЛЫЙ МЕДВЕДЬ"), (3, "МАЛАЯ ПАНДА"), (4, "ДАЛЬНЕВОСТОЧНЫЙ ЛЕОПАРД"),
        (5, "ПУМА"), (6, "КАПИБАРА"), (7, "МАНУЛ"), (8, "ФЕНЕК"), (9, "ИРБИС, СНЕЖНЫЙ БАРС"), (10, "ЕНОТ-ПОЛОСКУН"),
        # Птицы
        (11, "КРАСНЫЙ ФЛАМИНГО"), (12, "ЯПОНСКИЙ ЖУРАВЛЬ"), (13, "БЕЛЫЙ КАКАДУ"), (14, "АЛЕКСАНДРИЙСКИЙ ПОПУГАЙ"),
        (15, "АЛМАЗНЫЙ ФАЗАН"), (16, "СТЕПНОЙ ОРЕЛ"), (17, "КИТОГЛАВ"), (18, "РОЗОВЫЙ ПЕЛИКАН"),
        (19, "БЕЛОГОЛОВЫЙ ОРЛАН"), (20, "ЖУРАВЛЬ-КРАСАВКА"),
        # Рептилии
        (21, "КИТАЙСКИЙ АЛЛИГАТОР"), (22, "ТЕМНЫЙ ТИГРОВЫЙ ПИТОН"), (23, "ИНДИЙСКАЯ КОБРА"), (24, "ЛУЧИСТАЯ ЧЕРЕПАХА"),
        (25, "ГАВИАЛОВЫЙ КРОКОДИЛ"), (26, "СИАМСКИЙ КРОКОДИЛ"), (27, "ГЛАДКОЛОБЫЙ КАЙМАН"), (28, "СЕТЧАТЫЙ ПИТОН"),
        (29, "ГАБОНСКАЯ ГАДЮКА"), (30, "ШЛЕМОНОСНЫЙ ВАСИЛИСК"),
        # Амфибии
        (31, "КРАСНОГЛАЗАЯ КВАКША"), (32, "ЖАБА-АГА"), (33, "АФРИКАНСКИЙ ВОДОНОС (РОЮЩАЯ ЛЯГУШКА)"), (34, "ЗЕЛЁНАЯ ЖАБА"),
        (35, "ТРЁХПАЛАЯ АМФИУМА"), (36, "МОНГОЛЬСКАЯ ЖАБА"), (37, "ДАЛЬНЕВОСТОЧНАЯ КВАКША"), (38, "СВЕРЧКОВАЯ ЖАБА"),
        (39, "ОГНЕННАЯ САЛАМАНДРА"), (40, "ГОЛУБОЙ ДРЕВОЛАЗ")
    ]

    # Проверяем, что все животные есть в базе, и помечаем их как активные
    for animal_id, name in selected_animals:
        cursor.execute('SELECT COUNT(*) FROM animals WHERE name = ?', (name,))
        if cursor.fetchone()[0] == 0:
            logger.error(f"Животное {name} не найдено в базе!")
            continue
        cursor.execute('UPDATE animals SET is_active = 1 WHERE name = ?', (name,))
        logger.info(f"Животное {name} помечено как активное.")

    # Проверяем, что все неактивные животные имеют is_active = 0
    cursor.execute('UPDATE animals SET is_active = 0 WHERE is_active IS NULL OR is_active != 1')

    # Генерируем ответы (пример для одного животного, полный список позже)
    sample_answers = {
        "ru": {
            "1": "Рычу на весь лес, как АМУРСКИЙ ТИГР!",
            "2": "Бросаюсь на добычу, как АМУРСКИЙ ТИГР!",
            # ... и так далее до 20
        },
        "en": {
            "1": "I roar across the forest like an AMUR TIGER!",
            "2": "I pounce on prey like an AMUR TIGER!",
            # ... и так далее до 20
        }
    }
    # Полные 800 ответов добавим после твоего подтверждения
    cursor.execute('UPDATE animals SET answers = ? WHERE name = ?', (json.dumps(sample_answers), "АМУРСКИЙ ТИГР"))

    conn.commit()
    conn.close()
    logger.info("База подготовлена для второго этапа: выбраны 40 животных, очищена таблица answers.")

if __name__ == "__main__":
    setup_main_quiz_animals()