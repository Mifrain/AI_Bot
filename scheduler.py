import logging
from datetime import datetime, timedelta

from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import db
from helpers import WORKOUT_REMINDER_MESSAGE

scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)


async def start_scheduler(bot):
    # подгрузка включенных уведомок
    reminders = db.get_all_on_reminders()

    if not reminders:
        logger.info("Нет активных напоминаний для восстановления.")
        return

    for job_id, user_id, remind_time in reminders:
        hours, minutes = map(int, remind_time.split(":"))

        scheduler.add_job(
            send_reminder,
            CronTrigger(hour=hours, minute=minutes),
            args=[None, bot, user_id],
            id=job_id,
        )

    # Добавляем задания на отправку анкет через 2 дня после регистрации
    users_with_survey = db.get_users_for_survey()
    for user_id, registration_date in users_with_survey:
        # Преобразуем строку даты в объект datetime
        registration_datetime = datetime.fromisoformat(registration_date)
        survey_date = registration_datetime + timedelta(days=2)

        # Устанавливаем время на 19:40
        survey_date = survey_date.replace(hour=19, minute=40)

        logger.info(survey_date)
        scheduler.add_job(
            send_survey_notification,
            CronTrigger(
                year=survey_date.year,
                month=survey_date.month,
                day=survey_date.day,
                hour=survey_date.hour,
                minute=survey_date.minute,
            ),
            args=[bot, user_id],
            id=f"survey_{user_id}",
        )

    logger.info(f"Восстановлено {len(reminders)} активных напоминаний.")

    if not scheduler.running:
        scheduler.start()


async def send_reminder(message: Message | None, bot=None, chat_id: int = None):
    try:
        if bot:
            await bot.send_message(chat_id, WORKOUT_REMINDER_MESSAGE)
        else:
            await message.answer(WORKOUT_REMINDER_MESSAGE)
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания: {e}")


async def send_survey_notification(bot, user_id: int):
    """
    Отправляет пользователю уведомление с просьбой заполнить анкету.
    """
    try:
        await bot.send_message(
            user_id,
            "Привет! Пожалуйста, уделите минуту, чтобы заполнить анкету о нашем боте: [Заполнить анкету](https://example.com/survey)",
            parse_mode="Markdown",
        )
        db.mark_survey_sent(user_id)  # Отмечаем в базе данных

        logger.info(f"Уведомление об анкете отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(
            f"Ошибка при отправке уведомления об анкете пользователю {user_id}: {e}"
        )
