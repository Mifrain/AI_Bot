import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from config import settings
from handlers import start, send_notification, menu, tasks
from database import db
from middleware import RegistrationMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

db.create_tables()

dp.message.middleware.register(RegistrationMiddleware())

# Routers
dp.include_router(start.router)

dp.include_router(menu.router)
dp.include_router(tasks.router)

dp.include_router(send_notification.router)

async def on_startup():
    from scheduler import start_scheduler

    await start_scheduler(bot)
    logger.info("Уведомления подгружены")


if __name__ == '__main__':
    dp.startup.register(on_startup)

    logger.info("Бот Запущен")
    dp.run_polling(bot)
