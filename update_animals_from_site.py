# update_animals_from_site.py
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging
import json
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_animals_from_site():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Очищаем таблицу animals
    cursor.execute('DELETE FROM animals')

    # Настройка Selenium
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Без графического интерфейса
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    # URL страницы с животными, ждущими опекунства
    url = "https://moscowzoo.ru/about/guardianship/waiting-guardianship"

    try:
        # Загружаем страницу
        driver.get(url)
        # Даём время на выполнение JavaScript (5 секунд)
        time.sleep(5)

        # Получаем HTML после рендеринга
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Отладка: выводим первые 5000 символов HTML
        logger.info(f"HTML страницы (первые 5000 символов): {soup.prettify()[:5000]}")

        # Находим все карточки животных
        animal_cards = soup.find_all('a', class_='waiting-for-guardian-animals__item')

        # Отладка: проверяем, сколько карточек найдено
        logger.info(f"Найдено карточек животных: {len(animal_cards)}")
        if not animal_cards:
            logger.error("Не найдены карточки животных с классом 'waiting-for-guardian-animals__item'")
            driver.quit()
            return

        animals = []
        animal_id = 1

        for card in animal_cards:
            # Извлекаем название животного
            name_tag = card.find('span', class_='animal__name')
            if not name_tag:
                logger.warning("Не найдено название животного в карточке")
                continue
            name_ru = name_tag.text.strip()

            # Извлекаем ссылку на страницу животного
            page_url = card.get('href')
            if not page_url:
                logger.warning(f"Не найдена ссылка для {name_ru}")
                continue
            if page_url.startswith('/'):
                page_url = f"https://moscowzoo.ru{page_url}"

            # Извлекаем ссылку на изображение
            img_tag = card.find('img', class_='animal__image')
            image_url = img_tag.get('src') if img_tag else ''
            if image_url and image_url.startswith('/'):
                image_url = f"https://moscowzoo.ru{image_url}"

            # Категория (временно "Неизвестно")
            category = "Неизвестно"

            # Временные пустые ответы
            empty_answers = json.dumps(
                {"ru": {str(i): "" for i in range(1, 21)}, "en": {str(i): "" for i in range(1, 21)}})

            # Добавляем животное в список
            animals.append({
                "id": animal_id,
                "name": name_ru,
                "category": category,
                "page_url": page_url,
                "image_url": image_url,
                "answers": empty_answers
            })
            logger.info(f"Добавлено: {name_ru}, Image URL: {image_url}")
            animal_id += 1

        # Записываем в базу
        for animal in animals:
            cursor.execute('''
                INSERT OR REPLACE INTO animals (id, name, category, page_url, image_url, answers)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (animal["id"], animal["name"], animal["category"], animal["page_url"], animal["image_url"],
                  animal["answers"]))

        conn.commit()
        logger.info(f"Обновлено {len(animals)} животных в базе.")

    finally:
        driver.quit()
        conn.close()


if __name__ == "__main__":
    update_animals_from_site()