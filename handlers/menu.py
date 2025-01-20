import logging

from aiogram import F, Router
from aiogram.types import Message

from database import db
from helpers import format_rating_message, format_reminder_message
from keyboards.menu import admin_menu_kb, main_menu_kb
from keyboards.tasks import reminder_inline_kb, tasks_inline_kb

router = Router()

logger = logging.getLogger(__name__)


@router.message(F.text == "/menu")
async def menu_command(message: Message):
    await message.answer("Главное Меню\nВыберите действие:", reply_markup=main_menu_kb)


@router.message(F.text == "/admin")
async def admin_command(message: Message):
    is_admin = db.is_user_admin(message.from_user.id)
    if not is_admin:
        await message.answer("Вы не являетесь админом!", reply_markup=main_menu_kb)
        return
    await message.answer("Админ панель\nВыберите действие:", reply_markup=admin_menu_kb)


@router.message(F.text == "Список всех пользователей")
async def list_users_command(message: Message):
    """Обработчик для вывода количества пользователей"""
    is_admin = db.is_user_admin(message.from_user.id)
    if not is_admin:
        await message.answer("Вы не являетесь админом!", reply_markup=main_menu_kb)
        return

    try:
        total_users = db.get_user_count()
        await message.answer(f"Всего зарегистрированных пользователей: {total_users}")
    except Exception as e:
        logger.error(f"Ошибка при получении количества пользователей: {e}")
        await message.answer(
            "Не удалось получить количество пользователей. Попробуйте позже."
        )


@router.message(F.text == "📋 Задания")
async def tasks(message: Message):
    await message.answer("Выберите задание", reply_markup=tasks_inline_kb)


@router.message(F.text == "⏰ Напоминания")
async def reminder(message: Message):
    reminder = db.is_reminder_exist(message.from_user.id)
    await message.answer(
        format_reminder_message(reminder), reply_markup=reminder_inline_kb
    )


@router.message(F.text == "🏆 Уровень")
async def rating(message: Message):
    await message.answer(
        f"Ваш Текущий Уровень 🏆: {db.get_user_level(message.from_user.id)}\n\nРешайте больше заданий, чтобы быть лучше всех!"
    )


@router.message(F.text == "ℹ️ Помощь")
async def help(message: Message):
    await message.answer(f"Привет!\nЕсли тебе нужна помощь, напиши админу:\n@admin")


@router.message(F.text == "🏅 Рейтинг")
async def rating(message: Message):
    try:
        user_data = db.get_top_and_user_position(message.from_user.id)

        rating_message = "Топ пользователей:\n"
        for i, user in enumerate(user_data["top_users"], start=1):
            rating_message += f"{i}. {user['display_name']}: {user['rating']} очков\n"

        if user_data["user_position"] > 0:
            rating_message += "Ваши результаты:\n\n"
            rating_message += f"Позиция: {user_data['user_position']}\n"
            rating_message += f"Очки: {user_data['user_rating']}"
        else:
            rating_message += "Вы пока не в рейтинге.\n"

        await message.answer(rating_message)

    except Exception as e:
        await message.answer(
            "Произошла ошибка при получении рейтинга. Попробуйте позже."
        )
        logger.error(f"Ошибка при получении рейтинга пользователя: {e}")
