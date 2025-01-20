from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram.types import Message

from database import db


scheduler = AsyncIOScheduler()


async def start_scheduler(bot):
    # подгрузка включенных уведомок
    reminders = db.get_all_on_reminders()

    if not reminders:
        print("Нет активных напоминаний для восстановления.")
        return

    for job_id, user_id, remind_time in reminders:
        hours, minutes = map(int, remind_time.split(":"))

        scheduler.add_job(
            send_reminder,
            CronTrigger(hour=hours, minute=minutes),
            args=[None, bot, user_id],
            id=job_id
        )

    print(f"Восстановлено {len(reminders)} активных напоминаний.")

    if not scheduler.running:
        scheduler.start()


async def send_reminder(message: Message, bot = None, chat_id: int = None):
    if bot:
        await bot.send_message(chat_id, 'Время приступить к тренировкам!')
    else:
        await message.answer("Время приступить к тренировкам!")



