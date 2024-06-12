# - Контактный механизм в файле contacts.py


from aiogram import types, Dispatcher

async def contact_support(message: types.Message):
    await message.answer("Свяжитесь с нами по телефону +7 (495) 123-45-67 или email: info@moscowzoo.ru")

def register_contact_handlers(dp: Dispatcher):
    dp.register_message_handler(contact_support, commands="contact")
