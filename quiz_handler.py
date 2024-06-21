import json
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class QuizStates(StatesGroup):
    NAME = State()
    CHILDREN = State()
    ANIMAL_TYPE = State()
    QUESTION = State()

async def start_quiz(message: types.Message):
    await message.reply("Привет!\nЯ бот-викторина Московского зоопарка.\nКаково Ваше имя?")
    await QuizStates.NAME.set()

async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Начало викторины"))
    await message.reply(f"Приятно познакомиться, {message.text}!\n\n"
                        "Викторина поможет вам узнать\n"
                        "«Какое у вас тотемное животное?»\n\n"
                        "Нажимайте на кнопку ниже чтобы начать викторину", reply_markup=markup)
    await QuizStates.next()

async def process_start_quiz(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()
    await message.reply("Викторина началась!", reply_markup=markup)
    await message.answer("Есть ли у тебя дети?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton("Да"), types.KeyboardButton("Нет")))

async def process_children(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['children'] = message.text.lower() == 'да'

    if data['children']:
        await message.reply("Сколько у вас детей?\nПишите только цифру", reply_markup=types.ReplyKeyboardRemove())
        await QuizStates.CHILDREN.set()
    else:
        await ask_animal_type(message, state)

async def process_children_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['children_number'] = message.text

    await ask_animal_type(message, state)

async def ask_animal_type(message: types.Message, state: FSMContext):
    await QuizStates.ANIMAL_TYPE.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).row(
        types.KeyboardButton("Животные"), types.KeyboardButton("Птицы"),
        types.KeyboardButton("Рыбы"), types.KeyboardButton("Земноводные"),
        types.KeyboardButton("Змеи")
    )
    await message.answer("Какой вид обитателей Московского зоопарка вы выбираете:", reply_markup=markup)

async def process_animal_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['animal_type'] = message.text.lower()

    await QuizStates.QUESTION.set()
    await ask_question(message, state)

async def ask_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        with open('quiz_text.json', 'r', encoding='utf-8') as file:
            quiz_data = json.load(file)

        animal_type_key = data['animal_type']
        if animal_type_key in quiz_data:
            questions_data = quiz_data[animal_type_key][0]
            question_text = questions_data['questions'].replace("{name}", data['name'])
            options = questions_data['options']

            data['questions'] = questions_data
            data['current_question'] = 0

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
                types.KeyboardButton("1"), types.KeyboardButton("2"), types.KeyboardButton("3")
            )

            await message.answer(question_text)
            for idx, option in enumerate(options):
                await message.answer(f"{idx + 1}. {option}")
            await message.answer("Выберите один из вариантов (1, 2 или 3):", reply_markup=markup)

async def process_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_question = data.get('current_question', 0)
        questions_data = data['questions']

        answer = message.text.strip()
        if answer in ["1", "2", "3"]:
            if current_question + 1 < len(questions_data['options']):
                data['current_question'] += 1
                await ask_question(message, state)
            else:
                await message.reply("Спасибо за участие в викторине!")
                await state.finish()
        else:
            await message.reply("Пожалуйста, выберите один из вариантов (1, 2 или 3).")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_quiz, commands="start", state="*")
    dp.register_message_handler(process_name, state=QuizStates.NAME)
    dp.register_message_handler(process_start_quiz, lambda message: message.text == "Начало викторины", state=QuizStates.CHILDREN)
    dp.register_message_handler(process_children, state=QuizStates.CHILDREN)
    dp.register_message_handler(process_children_number, state=QuizStates.CHILDREN)
    dp.register_message_handler(process_animal_type, state=QuizStates.ANIMAL_TYPE)
    dp.register_message_handler(process_answer, state=QuizStates.QUESTION)
