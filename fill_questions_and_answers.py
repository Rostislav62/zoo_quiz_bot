# fill_questions_and_answers.py
import sqlite3
import json

def fill_questions_and_answers():
    conn = sqlite3.connect('zoo_quiz.db')
    cursor = conn.cursor()

    # Очищаем таблицу questions
    cursor.execute('DELETE FROM questions')

    # 20 вопросов на русском и английском
    questions = [
        {"id": "1", "text_ru": "Как ты рычишь по утрам?", "text_en": "How do you roar in the morning?"},
        {"id": "2", "text_ru": "Что ты делаешь, когда видишь вкусный обед?", "text_en": "What do you do when you see a tasty lunch?"},
        {"id": "3", "text_ru": "Где бы ты спрятал свою добычу?", "text_en": "Where would you hide your prey?"},
        {"id": "4", "text_ru": "Какой у тебя танец приветствия?", "text_en": "What’s your greeting dance?"},
        {"id": "5", "text_ru": "Что ты делаешь в жару, чтобы не растаять?", "text_en": "What do you do in the heat to avoid melting?"},
        {"id": "6", "text_ru": "Какой у тебя стиль отдыха в тени?", "text_en": "What’s your shade-resting style?"},
        {"id": "7", "text_ru": "Что ты делаешь на высоте?", "text_en": "What do you do up high?"},
        {"id": "8", "text_ru": "Как ты согреваешь лапы в мороз?", "text_en": "How do you warm your paws in the cold?"},
        {"id": "9", "text_ru": "Как ты охотился бы ночью?", "text_en": "How would you hunt at night?"},
        {"id": "10", "text_ru": "Какой твой фирменный трюк?", "text_en": "What’s your signature trick?"},
        {"id": "11", "text_ru": "Как ты зовёшь друзей на вечеринку?", "text_en": "How do you call friends to a party?"},
        {"id": "12", "text_ru": "Что ты делаешь с мокрыми лапами?", "text_en": "What do you do with wet paws?"},
        {"id": "13", "text_ru": "Как ты показываешь свою силу?", "text_en": "How do you show your strength?"},
        {"id": "14", "text_ru": "Где бы ты построил своё логово?", "text_en": "Where would you build your lair?"},
        {"id": "15", "text_ru": "Как ты реагируешь на шум?", "text_en": "How do you react to noise?"},
        {"id": "16", "text_ru": "Что ты делаешь в воде?", "text_en": "What do you do in water?"},
        {"id": "17", "text_ru": "Как ты встречаешь закат?", "text_en": "How do you greet the sunset?"},
        {"id": "18", "text_ru": "Что ты делаешь, когда лень двигаться?", "text_en": "What do you do when you’re too lazy to move?"},
        {"id": "19", "text_ru": "Как ты защищаешь свою территорию?", "text_en": "How do you defend your territory?"},
        {"id": "20", "text_ru": "Какой у тебя секретный талант?", "text_en": "What’s your secret talent?"}
    ]

    # Заполняем таблицу questions
    for q in questions:
        cursor.execute('INSERT OR REPLACE INTO questions (id, text_ru, text_en) VALUES (?, ?, ?)',
                       (q["id"], q["text_ru"], q["text_en"]))

    # Ответы для всех 35 животных
    answers = {
        1: {"ru": "Реву на всю саванну, как индийский лев!", "en": "I roar across the savanna like an Indian lion!"},
        2: {"ru": "Тихо мурлычу в горах, как снежный барс!", "en": "I purr quietly in the mountains like a snow leopard!"},
        3: {"ru": "Грациозно хлопаю крыльями, как красный фламинго!", "en": "I flap my wings gracefully like a red flamingo!"},
        4: {"ru": "Мило похрустываю бамбуком, как малая панда!", "en": "I crunch bamboo cutely like a small panda!"},
        5: {"ru": "Рычу так, что лес дрожит, как амурский тигр!", "en": "I growl so the forest shakes like an Amur tiger!"},
        6: {"ru": "Рявкаю с ледяной глыбы, как белый медведь!", "en": "I bark from an ice block like a polar bear!"},
        7: {"ru": "Тяну шею к солнцу, как сетчатый жираф!", "en": "I stretch my neck to the sun like a reticulated giraffe!"},
        8: {"ru": "Мяукаю с утёса, как пума!", "en": "I meow from a cliff like a puma!"},
        9: {"ru": "Тружусь хоботом, как азиатский слон!", "en": "I trumpet with my trunk like an Asian elephant!"},
        10: {"ru": "Бурчу с берега, как уссурийский белогрудый медведь!", "en": "I grumble from the shore like an Ussuri white-chested bear!"},
        11: {"ru": "Кричу с высоты, как даурский журавль!", "en": "I call from above like a Daurian crane!"},
        12: {"ru": "Клюю воздух, как восточный седлоклювый ябиру!", "en": "I peck the air like an Eastern saddle-billed stork!"},
        13: {"ru": "Шиплю из засады, как дальневосточный леопард!", "en": "I hiss from an ambush like a Far Eastern leopard!"},
        14: {"ru": "Рычу в горах, как гималайский медведь!", "en": "I growl in the mountains like a Himalayan bear!"},
        15: {"ru": "Кричу с перьями, как обыкновенный павлин!", "en": "I screech with feathers like a common peafowl!"},
        16: {"ru": "Танцую с криком, как японский журавль!", "en": "I dance with a cry like a Japanese crane!"},
        17: {"ru": "Свищу с норы, как черношапочный сурок!", "en": "I whistle from my burrow like a black-capped marmot!"},
        18: {"ru": "Блею с вершины, как сибирский горный козёл!", "en": "I bleat from the peak like a Siberian ibex!"},
        19: {"ru": "Мурлычу пушисто, как манул!", "en": "I purr fluffily like a Pallas’s cat!"},
        20: {"ru": "Кричу громко, как обыкновенный какаду!", "en": "I scream loudly like a common cockatoo!"},
        21: {"ru": "Кружу с карканьем, как стервятник!", "en": "I circle with a croak like a turkey vulture!"},
        22: {"ru": "Плюхаюсь в воду, как гигантская выдра!", "en": "I splash into water like a giant otter!"},
        23: {"ru": "Шиплю у воды, как китайский аллигатор!", "en": "I hiss by the water like a Chinese alligator!"},
        24: {"ru": "Шиплю с поднятым капюшоном, как восточная кобра!", "en": "I hiss with a raised hood like an Eastern cobra!"},
        25: {"ru": "Кричу с неба, как степной орёл!", "en": "I scream from the sky like a steppe eagle!"},
        26: {"ru": "Клюю с громким плеском, как розовый пеликан!", "en": "I peck with a loud splash like a rosy pelican!"},
        27: {"ru": "Рычу в очках, как очковый медведь!", "en": "I growl in glasses like a spectacled bear!"},
        28: {"ru": "Шиплю в реке, как сиамский крокодил!", "en": "I hiss in the river like a Siamese crocodile!"},
        29: {"ru": "Шуршу чешуёй, как тёмный тигровый питон!", "en": "I rustle my scales like a dark tiger python!"},
        30: {"ru": "Топаю медленно, как лучистая черепаха!", "en": "I stomp slowly like a radiated tortoise!"},
        31: {"ru": "У-у-у с веток, как борнейский орангутан!", "en": "I hoot from branches like a Bornean orangutan!"},
        32: {"ru": "Пою с высоты, как жёлтощёкий гиббон!", "en": "I sing from up high like a yellow-cheeked gibbon!"},
        33: {"ru": "Кричу с хвостом, как кольцехвостый лемур!", "en": "I shout with my tail like a ring-tailed lemur!"},
        34: {"ru": "Пищу золотом, как золотистый львиный тамарин!", "en": "I squeak in gold like a golden lion tamarin!"},
        35: {"ru": "Шиплю из воды, как трёхпалая амфиума!", "en": "I hiss from the water like a three-toed amphiuma!"}
    }

    # Заполняем ответы для всех животных (35 животных, 20 вопросов)
    for animal_id in range(1, 36):
        answers_dict = {
            "ru": {},
            "en": {}
        }
        for q_id in range(1, 21):
            if q_id == 1:  # "Как ты рычишь по утрам?"
                answers_dict["ru"][str(q_id)] = answers[animal_id]["ru"]
                answers_dict["en"][str(q_id)] = answers[animal_id]["en"]
            elif q_id == 2:  # "Что ты делаешь, когда видишь вкусный обед?"
                answers_dict["ru"][str(q_id)] = f"Хватаю добычу, как {cursor.execute('SELECT name FROM animals WHERE id = ?', (animal_id,)).fetchone()[0]}!"
                answers_dict["en"][str(q_id)] = f"I grab my prey like a {cursor.execute('SELECT name FROM animals WHERE id = ?', (animal_id,)).fetchone()[0].lower()}!"
            # Добавим остальные вопросы позже в полном скрипте
        answers_json = json.dumps(answers_dict)
        cursor.execute('UPDATE animals SET answers = ? WHERE id = ?', (answers_json, animal_id))

    conn.commit()
    conn.close()
    print("Questions and answers filled.")

if __name__ == "__main__":
    fill_questions_and_answers()