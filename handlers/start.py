from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from states.registration import RegistrationState

from database import db

from keyboards.menu import choose_target_kb, main_menu_kb

router = Router()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    
    if db.is_user_registered(message.from_user.id):
        fullname = db.get_user_firstname(message.from_user.id)
        await message.answer(f"Добро пожаловать, {fullname}!")
    else:
        await message.answer("Пожалуйста, введите ваше имя:")
        await state.set_state(RegistrationState.first_name)

@router.message(RegistrationState.first_name)
async def process_name(message: Message, state: FSMContext):
    first_name = message.text.strip()
    if len(first_name.split(' ')) > 1:
        await message.answer("Пожалуйста, введите только имя")
    else:
        await state.update_data(first_name=first_name)
        await message.answer("Введите Ваш возраст:")
        await state.set_state(RegistrationState.age)

@router.message(RegistrationState.age)
async def process_age(message: Message, state: FSMContext):
    age = message.text.strip()
    if not age.isdigit():
        await message.answer("Возраст должен быть числом. Попробуйте снова.")
    else:
        await state.update_data(age=age)
        await message.answer("Выберите Вашу цель тренировок:", reply_markup=choose_target_kb)
        await state.set_state(RegistrationState.target)

@router.callback_query(RegistrationState.target)
async def process_target(callback: CallbackQuery, state: FSMContext):
    target = callback.data
    data = await state.get_data()
    db.register_user(
        callback.from_user.id,
        callback.from_user.username or "Unknown",
        data["first_name"],
        data["age"],
        target
    )
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer(
        f"Регистрация завершена! Добро пожаловать, {data['first_name']}!",
        reply_markup=main_menu_kb
    )
    await state.clear()
