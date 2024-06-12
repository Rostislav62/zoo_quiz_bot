# - Механизм обратной связи в файле feedback.py


from aiogram import types, Dispatcher

async def collect_feedback(message: types.Message):
    await message.answer("Пожалуйста, оставьте свой отзыв о викторине!")

def register_feedback_handlers(dp: Dispatcher):
    dp.register_message_handler(collect_feedback, commands="feedback")
