# fill_animals.py
import sqlite3
import json

def fill_animals():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Очищаем таблицу animals
    cursor.execute('DELETE FROM animals')

    # Список животных (35)
    animals = [
        {"id": 1, "name": "ИНДИЙСКИЙ ЛЕВ", "name_en": "Indian Lion", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/indiyskiy-lev", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/8f122f5c-7463-42b7-980f-bb5f7f05646a.jpeg"},
        {"id": 2, "name": "СНЕЖНЫЙ БАРС", "name_en": "Snow Leopard", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/snezhnyy-bars", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/5a1458c5-8a8b-4b2b-a59b-d1071d8c7a9c.jpeg"},
        {"id": 3, "name": "КРАСНЫЙ ФЛАМИНГО", "name_en": "Red Flamingo", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/krasnyy_flamingo", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/8ca2cadd-ac28-4222-873c-c30b050e8e31.jpeg"},
        {"id": 4, "name": "МАЛАЯ ПАНДА", "name_en": "Small Panda", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/malaya-panda", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/0c83d9a1-20d2-418a-9c0c-9efc149f7c4e.jpeg"},
        {"id": 5, "name": "АМУРСКИЙ ТИГР", "name_en": "Amur Tiger", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/amurskiy_tigr", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/6e21c072-0b90-4ef9-b429-5b6dcbff6c7b.jpeg"},
        {"id": 6, "name": "БЕЛЫЙ МЕДВЕДЬ", "name_en": "Polar Bear", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/belyy_medved", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/fd6a0e97-8424-4b09-8b54-8c3e3ef69361.jpeg"},
        {"id": 7, "name": "СЕТЧАТЫЙ ЖИРАФ", "name_en": "Reticulated Giraffe", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/setchatyy-giraf", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/48a49f8e-91e7-46b1-8e82-df568f2a5f80.jpeg"},
        {"id": 8, "name": "ПУМА", "name_en": "Puma", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/puma", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/3d63489c-d078-4012-af8a-b6bba5f85726.jpeg"},
        {"id": 9, "name": "АЗИАТСКИЙ СЛОН", "name_en": "Asian Elephant", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/aziatskiy_slon", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/5c716198-b8c0-4f4e-b831-728f39a79009.jpeg"},
        {"id": 10, "name": "УССУРИЙСКИЙ БЕЛОГРУДЫЙ МЕДВЕДЬ", "name_en": "Ussuri White-chested Bear", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/ussuriyskiy-belogrudyy-medved", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/3b54e7d3-7ac0-4d58-ae6e-2e8e9e5f2c77.jpeg"},
        {"id": 11, "name": "ДАУРСКИЙ ЖУРАВЛЬ", "name_en": "Daurian Crane", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/daurskiy_zhuravl", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/412d11f9-cb9b-4d7c-9b4a-feb4d507bef2.jpeg"},
        {"id": 12, "name": "ВОСТОЧНЫЙ СЕДЛОКЛЮВЫЙ ЯБИРУ", "name_en": "Eastern Saddle-billed Stork", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/vostochnyy_sedloklyuvyy_yabiru", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/95ae565a-bcc4-48c5-93f4-ac6b41a9fcc3.jpeg"},
        {"id": 13, "name": "ДАЛЬНЕВОСТОЧНЫЙ ЛЕОПАРД", "name_en": "Far Eastern Leopard", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/dalnevostochnyy_leopard", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/5a1458c5-8a8b-4b2b-a59b-d1071d8c7a9c.jpeg"},
        {"id": 14, "name": "ГИМАЛАЙСКИЙ МЕДВЕДЬ", "name_en": "Himalayan Bear", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/gimalayskiy_medved", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/3b54e7d3-7ac0-4d58-ae6e-2e8e9e5f2c77.jpeg"},
        {"id": 15, "name": "ОБЫКНОВЕННЫЙ ПАВЛИН", "name_en": "Common Peafowl", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/obyknovennyy_pavlin", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/7d46bf28-e2df-4773-bc08-c216730e3800.jpeg"},
        {"id": 16, "name": "ЯПОНСКИЙ ЖУРАВЛЬ", "name_en": "Japanese Crane", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/yaponskiy_zhuravl", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/412d11f9-cb9b-4d7c-9b4a-feb4d507bef2.jpeg"},
        {"id": 17, "name": "ЧЕРНОШАПОЧНЫЙ СУРОК", "name_en": "Black-capped Marmot", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/chernoshapochnyy_surok", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/3b54e7d3-7ac0-4d58-ae6e-2e8e9e5f2c77.jpeg"},
        {"id": 18, "name": "СИБИРСКИЙ ГОРНЫЙ КОЗЁЛ", "name_en": "Siberian Ibex", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/sibirskiy_gornyy_kozyol", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/0a54da13-010f-4c28-aae8-97a4b21d2e74.jpeg"},
        {"id": 19, "name": "МАНУЛ", "name_en": "Pallas’s Cat", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/manul", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/5a1458c5-8a8b-4b2b-a59b-d1071d8c7a9c.jpeg"},
        {"id": 20, "name": "ОБЫКНОВЕННЫЙ КАКАДУ", "name_en": "Common Cockatoo", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/obyknovennyy_kakadu", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/69353a1f-35a1-42c7-8e49-fc0b9bbdf966.jpg"},
        {"id": 21, "name": "СТЕРВЯТНИК", "name_en": "Turkey Vulture", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/stervyatnik", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/36102208-b069-403e-8d84-31b2631010c9.jpeg"},
        {"id": 22, "name": "ГИГАНТСКАЯ ВЫДРА", "name_en": "Giant Otter", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/gigantskaya_vydra", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/0c83d9a1-20d2-418a-9c0c-9efc149f7c4e.jpeg"},
        {"id": 23, "name": "КИТАЙСКИЙ АЛЛИГАТОР", "name_en": "Chinese Alligator", "category": "Рептилии", "page_url": "https://moscowzoo.ru/animals/kinds/kitayskiy_alligator", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/bf1c7c71-b3d1-4f7b-968c-b0ff4f382382.jpeg"},
        {"id": 24, "name": "ВОСТОЧНАЯ КОБРА", "name_en": "Eastern Cobra", "category": "Рептилии", "page_url": "https://moscowzoo.ru/animals/kinds/vostochnaya_kobra", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/b51da33d-be96-4c8e-bc89-d0456aa1b74c.jpeg"},
        {"id": 25, "name": "СТЕПНОЙ ОРЁЛ", "name_en": "Steppe Eagle", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/stepnoy_oryol", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/36102208-b069-403e-8d84-31b2631010c9.jpeg"},
        {"id": 26, "name": "РОЗОВЫЙ ПЕЛИКАН", "name_en": "Rosy Pelican", "category": "Птицы", "page_url": "https://moscowzoo.ru/animals/kinds/rozovyy_pelikan", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/95ae565a-bcc4-48c5-93f4-ac6b41a9fcc3.jpeg"},
        {"id": 27, "name": "ОЧКОВЫЙ МЕДВЕДЬ", "name_en": "Spectacled Bear", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/ochkovyy_medved", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/3b54e7d3-7ac0-4d58-ae6e-2e8e9e5f2c77.jpeg"},
        {"id": 28, "name": "СИАМСКИЙ КРОКОДИЛ", "name_en": "Siamese Crocodile", "category": "Рептилии", "page_url": "https://moscowzoo.ru/animals/kinds/siamskiy_krokodil", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/87e4ec11-8d44-4e54-8e23-f572ffdc32ca.png"},
        {"id": 29, "name": "ТЁМНЫЙ ТИГРОВЫЙ ПИТОН", "name_en": "Dark Tiger Python", "category": "Рептилии", "page_url": "https://moscowzoo.ru/animals/kinds/temnyy_tigrovyy_piton", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/9ffa798f-2d10-42d9-b7f3-06262004e919.jpeg"},
        {"id": 30, "name": "ЛУЧИСТАЯ ЧЕРЕПАХА", "name_en": "Radiated Tortoise", "category": "Рептилии", "page_url": "https://moscowzoo.ru/animals/kinds/luchistaya_cherepaha", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/3e657b0d-1e2f-4d8f-8422-b520d90e80ad.jpeg"},
        {"id": 31, "name": "БОРНЕЙСКИЙ ОРАНГУТАН", "name_en": "Bornean Orangutan", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/borneyskiy_orangutan", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/0c83d9a1-20d2-418a-9c0c-9efc149f7c4e.jpeg"},
        {"id": 32, "name": "ЖЁЛТОЩЁКИЙ ГИББОН", "name_en": "Yellow-cheeked Gibbon", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/zhyoltoshchyokiy_gibbon", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/0c83d9a1-20d2-418a-9c0c-9efc149f7c4e.jpeg"},
        {"id": 33, "name": "КОЛЬЦЕХВОСТЫЙ ЛЕМУР", "name_en": "Ring-tailed Lemur", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/koltsekvostyy_lemur", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/0c83d9a1-20d2-418a-9c0c-9efc149f7c4e.jpeg"},
        {"id": 34, "name": "ЗОЛОТИСТЫЙ ЛЬВИНЫЙ ТАМАРИН", "name_en": "Golden Lion Tamarin", "category": "Млекопитающие", "page_url": "https://moscowzoo.ru/animals/kinds/zolotistyy_lvinnyy_tamarin", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/0c83d9a1-20d2-418a-9c0c-9efc149f7c4e.jpeg"},
        {"id": 35, "name": "ТРЁХПАЛАЯ АМФИУМА", "name_en": "Three-toed Amphiuma", "category": "Амфибии", "page_url": "https://moscowzoo.ru/animals/kinds/trehpalaya_amfiuma", "image_url": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/b68cfdaa-8f15-40c8-ac9f-6c55aa8ca2cb.jpeg"}
    ]

    # Временные пустые ответы (заполним позже)
    empty_answers = json.dumps({"ru": {str(i): "" for i in range(1, 21)}, "en": {str(i): "" for i in range(1, 21)}})

    # Заполняем таблицу animals
    for animal in animals:
        cursor.execute('''
            INSERT OR REPLACE INTO animals (id, name, category, page_url, image_url, answers)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (animal["id"], animal["name"], animal["category"], animal["page_url"], animal["image_url"], empty_answers))

    conn.commit()
    conn.close()
    print("Animals table filled with 35 animals.")

if __name__ == "__main__":
    fill_animals()