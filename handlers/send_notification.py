from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import db
from keyboards.tasks import reminder_inline_kb
from scheduler import scheduler, send_reminder
from states.reminder import ReminderState

router = Router()


@router.callback_query(F.data == "reminder_on")
async def start_notifications(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    reminder = db.is_reminder_exist(user_id)

    if reminder:
        if reminder[3]:
            await callback.message.answer("Уведомления уже были запущены!")
        else:
            db.update_reminder_status(user_id=user_id, is_reminder_on=True)

            remind_time = reminder[2]
            hours, minutes = map(int, remind_time.split(":"))

            scheduler.add_job(
                send_reminder,
                CronTrigger(hour=hours, minute=minutes),
                args=[callback.message],
                id=f"reminder_{user_id}",
            )

            await callback.message.answer("Уведомления запущены!")
            await callback.message.delete()
            await callback.message.answer(
                f"Меню напоминаний\nВаши уведомления: Включены ✅\nСохраненное время ⏰: {remind_time}",
                reply_markup=reminder_inline_kb,
            )
    else:
        await state.clear()
        await callback.message.answer(
            "Введите время для ежедневных уведомлений в формате HH:MM"
        )
        await state.set_state(ReminderState.time)

    if not scheduler.running:
        scheduler.start()


@router.callback_query(F.data == "reminder_off")
async def stop_notifications(callback: CallbackQuery):
    user_id = callback.from_user.id

    db.update_reminder_status(user_id, False)

    existing_job = scheduler.get_job(f"reminder_{user_id}")
    if existing_job:
        existing_job.remove()
        await callback.message.answer("Уведомления остановлены")
        await callback.message.delete()
        await callback.message.answer(
            f"Меню напоминаний\nВаши уведомления: Выключены ❌\nСохраненное время ⏰: {db.get_reminder_time(user_id)}",
            reply_markup=reminder_inline_kb,
        )
    else:
        await callback.message.answer(
            "Уведомления уже остановлены или не были запущены"
        )

    if not scheduler.running:
        scheduler.start()


@router.message(ReminderState.time)
async def save_reminder_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    time = message.text.strip()

    try:
        hours, minutes = map(int, time.split(":"))
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError

        job_id = f"reminder_{user_id}"
        remind_time = f"{hours:02}:{minutes:02}"

        db.add_reminder(
            job_id=job_id, user_id=user_id, remind_time=remind_time, is_reminder_on=True
        )

        scheduler.add_job(
            send_reminder,
            CronTrigger(hour=hours, minute=minutes),
            args=[message],
            id=job_id,
        )

        await message.answer("Уведомления запущены!")
        await message.answer(
            f"Меню напоминаний\nВаши уведомления: Включены ✅\nСохраненное время ⏰: {remind_time}",
            reply_markup=reminder_inline_kb,
        )
    except ValueError:
        await message.answer("Неверный формат времени. Попробуйте снова (HH:MM).")
    finally:
        await state.clear()


@router.callback_query(F.data == "change_reminder_time")
async def change_reminder_time(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    reminder = db.is_reminder_exist(user_id)
    if not reminder:
        await callback.message.answer("У вас нет активных напоминаний для изменения.")
        return

    await state.clear()
    await callback.message.answer(
        "Введите новое время для ежедневных уведомлений в формате HH:MM."
    )
    await state.set_state(ReminderState.time_change)


@router.message(ReminderState.time_change)
async def save_changed_reminder_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    time = message.text.strip()

    try:
        hours, minutes = map(int, time.split(":"))
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError

        job_id = f"reminder_{user_id}"
        remind_time = f"{hours:02}:{minutes:02}"

        db.update_reminder_time(user_id, remind_time)

        existing_job = scheduler.get_job(job_id)
        if existing_job:
            existing_job.remove()

        if db.check_is_reminder_on(user_id):
            scheduler.add_job(
                send_reminder,
                CronTrigger(hour=hours, minute=minutes),
                args=[message],
                id=job_id,
            )

        scheduler.get_job(job_id)

        await message.answer(f"Время напоминания изменено на {remind_time}.")
        await message.answer(
            f"Меню напоминаний\nВаши уведомления:{'Включены ✅' if scheduler.get_job(job_id) else 'Выключены ❌'}\nСохраненное время ⏰: {remind_time}",
            reply_markup=reminder_inline_kb,
        )
    except ValueError:
        await message.answer("Неверный формат времени. Попробуйте снова (HH:MM).")

    finally:
        await state.clear()


@router.message(Command("check"))
async def check(message: Message):
    await message.answer(str(scheduler.running))
