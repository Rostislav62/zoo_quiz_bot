# update_image_urls.py
import sqlite3
import requests
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_image_urls():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Получаем всех животных из базы
    cursor.execute('SELECT id, name, page_url, image_url FROM animals')
    animals = cursor.fetchall()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for animal in animals:
        animal_id, name, page_url, current_image_url = animal
        logger.info(f"Обновляем изображение для {name}...")

        try:
            # Загружаем страницу животного
            response = requests.get(page_url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Не удалось загрузить страницу для {name}: {response.status_code}")
                continue

            # Парсим HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем изображение (обычно в <img> с классом, связанным с главной картинкой)
            img_tag = soup.find('img', class_='animal-page__image')  # Пример класса, нужно проверить на сайте
            if not img_tag:
                # Если класс не найден, ищем первый <img> в секции контента
                img_tag = soup.find('div', class_='animal-page__content').find('img') if soup.find('div', class_='animal-page__content') else None

            if img_tag and 'src' in img_tag.attrs:
                new_image_url = img_tag['src']
                # Если ссылка относительная, добавляем базовый URL
                if new_image_url.startswith('/'):
                    new_image_url = f"https://moscowzoo.ru{new_image_url}"

                # Проверяем, отличается ли новая ссылка от текущей
                if new_image_url != current_image_url:
                    cursor.execute('UPDATE animals SET image_url = ? WHERE id = ?', (new_image_url, animal_id))
                    logger.info(f"Обновлён URL для {name}: {new_image_url}")
                else:
                    logger.info(f"URL для {name} уже актуален: {current_image_url}")
            else:
                logger.warning(f"Не найдено изображение на странице для {name}")

        except requests.RequestException as e:
            logger.error(f"Ошибка при загрузке страницы для {name}: {e}")

    conn.commit()
    conn.close()
    logger.info("Обновление URL изображений завершено.")

if __name__ == "__main__":
    update_image_urls()