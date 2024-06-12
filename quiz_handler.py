from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import json

class QuizStates(StatesGroup):
    NAME = State()
    AGE = State()
    HAS_CHILDREN = State()
    CHILDREN_NUMBER = State()
    ANIMAL_TYPE = State()
    QUESTION = State()

async def start_quiz(message: types.Message):
    await message.answer("Привет!\nЯ бот-викторина Московского зоопарка.\nКаково Ваше имя?")
    await QuizStates.NAME.set()

async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer(f"Приятно познакомиться, {message.text}!\nСколько вам лет?")
    await QuizStates.AGE.set()

async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    name = (await state.get_data())['name']
    await message.answer(f"{name}, давай начнем викторину!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Начало викторины")))
    await QuizStates.HAS_CHILDREN.set()

async def process_quiz_start(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()
    await message.answer("Викторина началась!", reply_markup=markup)
    await message.answer("Есть ли у вас дети?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Да"), types.KeyboardButton("Нет")))
    await QuizStates.CHILDREN_NUMBER.set()

async def process_children(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['has_children'] = message.text.lower() == 'да'
    if data['has_children']:
        await QuizStates.CHILDREN_NUMBER.set()
        await message.answer("Сколько у вас детей?")
    else:
        await QuizStates.ANIMAL_TYPE.set()
        await message.answer("Какой вид обитателей Московского зоопарка вы выбираете:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(*[types.KeyboardButton(animal) for animal in ['Животные', 'Птицы', 'Рыбы', 'Земноводные', 'Змеи']]))

async def process_children_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['children_number'] = message.text
    await QuizStates.ANIMAL_TYPE.set()
    await message.answer("Какой вид обитателей Московского зоопарка вы выбираете:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(*[types.KeyboardButton(animal) for animal in ['Животные', 'Птицы', 'Рыбы', 'Земноводные', 'Змеи']]))

async def process_animal_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['animal_type'] = message.text.lower()
    animal_type = data['animal_type']
    with open('quiz_text.json', 'r', encoding='utf-8') as file:
        quiz_data = json.load(file)
    questions = quiz_data.get(animal_type, [])
    if not questions:
        await message.answer("Извините, вопросы на эту тему еще не подготовлены.")
        await state.finish()
        return
    question = questions[0]  # Предполагаем, что вопросы в списке
    await QuizStates.QUESTION.set()
    await message.answer(question['question'], reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(*[types.KeyboardButton(str(i)) for i in range(1, len(question['answers']) + 1)]))
