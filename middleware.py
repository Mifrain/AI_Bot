from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from database import db

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):

        if isinstance(event, Message):
            user_id = event.from_user.id
            state = data.get("state")
            if state is not None and await state.get_state() is not None:
                return await handler(event, data)

            if not db.is_user_registered(user_id) and event.text != "/start":
                await event.answer(
                    "Вы не зарегистрированы. Пожалуйста, начните регистрацию, вызвав команду /start.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return  

        return await handler(event, data)