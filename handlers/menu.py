from aiogram import Router, F
from aiogram.types import Message

from keyboards.menu import main_menu_kb
from keyboards.tasks import tasks_inline_kb, reminder_inline_kb

from database import db

router = Router()


@router.message(F.text == "/menu")
async def menu_command(message: Message):
    await message.answer("Главное Меню\nВыберите действие:", reply_markup=main_menu_kb)



@router.message(F.text == "📋 Задания")
async def tasks(message: Message):
    await message.answer("Выберите задание", reply_markup=tasks_inline_kb)

@router.message(F.text == "⏰ Напоминания")
async def reminder(message: Message):
    reminder = db.is_reminder_exist(message.from_user.id)
    if reminder:
        await message.answer(f"Меню напоминаний\nВаши уведомления:{'Включены ✅' if reminder[3] else 'Выключены❌'}\nСохраненное время ⏰: {reminder[2]}" ,
                             reply_markup=reminder_inline_kb)
    else:
        await message.answer(
            f"Меню напоминаний\nВаши уведомления: Выключены ❌\nСохраненное время ⏰: Отсутствует",
            reply_markup=reminder_inline_kb)

@router.message(F.text == "🏆 Уровень")
async def rating(message: Message):
    await message.answer(f"Ваш Текущий Уровень 🏆: {db.get_user_level(message.from_user.id)}\n\nРешайте больше заданий, чтобы быть лучше всех!")

@router.message(F.text == "ℹ️ Помощь")
async def help(message: Message):
    await message.answer(f"Помощи не будет")