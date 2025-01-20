import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database import db
from handlers import menu, send_notification, start, tasks
from middleware import RegistrationMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
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


if __name__ == "__main__":
    dp.startup.register(on_startup)

    logger.info("Бот Запущен")
    try:
        dp.run_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
