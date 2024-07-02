# feedback.py  779559038



import logging  # Импортируем logging
import os  # Импортируем os для проверки существования файла
from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup

class ContactForm(StatesGroup):
    fullname = State()
    phone = State()
    email = State()
    telegram = State()

class FeedbackHandler:
    @staticmethod
    async def start_contact_form(callback_query: types.CallbackQuery):
        callback_data = callback_query.data.split(':')
        if len(callback_data) == 2:
            txt_file = callback_data[1]
        else:
            txt_file = 'default_file.txt'

        await ContactForm.fullname.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(txt_file=txt_file)
        await callback_query.message.answer("Пожалуйста, введите ваше ФИО:")
        await callback_query.answer()

    @staticmethod
    async def process_fullname(message: types.Message, state: FSMContext):
        await state.update_data(fullname=message.text)
        await ContactForm.next()
        await message.answer("Пожалуйста, введите ваш контактный телефон:")

    @staticmethod
    async def process_phone(message: types.Message, state: FSMContext):
        await state.update_data(phone=message.text)
        await ContactForm.next()
        await message.answer("Пожалуйста, введите ваш e-mail:")

    @staticmethod
    async def process_email(message: types.Message, state: FSMContext):
        await state.update_data(email=message.text)
        await ContactForm.next()
        await message.answer("Пожалуйста, введите ваш Telegram:")

    @staticmethod
    async def process_telegram(message: types.Message, state: FSMContext):
        await state.update_data(telegram=message.text)
        data = await state.get_data()
        txt_file = data.get('txt_file', 'default_file.txt')

        # Проверьте существование файла
        if not os.path.exists(txt_file):
            await message.answer("Произошла ошибка: файл не найден.")
            return
        recipient_id = '779559038'
        logging.info(f"Sending telegram with results to chat ID {recipient_id}")
        await FeedbackHandler.send_telegram_with_results(data, txt_file, message.bot)
        await message.answer("Спасибо! Ваши данные были отправлены сотруднику.")
        await state.finish()

    @staticmethod
    async def send_telegram_with_results(data, txt_file, bot):
        recipient_id = '779559038'  # ID чата, куда вы хотите отправить данные

        body = (f"ФИО: {data['fullname']}\n"
                f"Телефон: {data['phone']}\n"
                f"Email: {data['email']}\n"
                f"Telegram: {data['telegram']}\n")

        logging.info(f"Sending message to {recipient_id} with body: {body}")

        await bot.send_message(recipient_id, body)

        logging.info(f"Sending document {txt_file} to {recipient_id}")
        with open(txt_file, 'rb') as f:
            await bot.send_document(recipient_id, f)
