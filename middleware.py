import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, ReplyKeyboardRemove

from database import db
from helpers import NOT_REGISTERED_MESSAGE

logger = logging.getLogger(__name__)


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            if isinstance(event, Message):
                user_id = event.from_user.id
                state = data.get("state")
                if state is not None and await state.get_state() is not None:
                    return await handler(event, data)

                if not db.is_user_registered(user_id) and event.text != "/start":
                    await event.answer(
                        NOT_REGISTERED_MESSAGE,
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    return

            return await handler(event, data)

        except Exception as e:
            logger.error(
                "Ошибка: %s, User: %s, Msg: %s",
                str(e),
                event.from_user.id if isinstance(event, Message) else "N/A",
                event.text if isinstance(event, Message) else "N/A",
            )
            if isinstance(event, Message):
                await event.answer("Произошла ошибка. Попробуйте позже.")
            return None
