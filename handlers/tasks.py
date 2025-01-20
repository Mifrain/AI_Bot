from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery

from states.tasks import TasksState
from AI import generate_task_with_gigachat, check_answer_with_gigachat
from keyboards.tasks import tasks_inline_kb, break_inline_kb
from database import db


router = Router()

# Карта категорий заданий
category_map = {
    "task_find_errors": "Исправление ошибок",
    "task_find_symbols": "Поиск символов",
    "task_find_extra": "Найти лишний элемент",
    "task_find_order": "Распознавание последовательностей",
    "task_memory": "Тест на память"
}


@router.callback_query(F.data.split('_')[0] == "task")
async def task_start(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()

    category = category_map.get(callback_query.data)
    level = db.get_user_level(callback_query.from_user.id)

    await state.update_data(category=callback_query.data)
    await state.update_data(level=level)

    await state.set_state(TasksState.question)
    await callback_query.message.answer(f"{category}\nНачинаем генерировать задания!\n\nДля выхода напишите стоп или воспользуйтесь кнопкой выхода")
    await send_next_question(callback_query.message, state)


async def send_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data.get("category")
    level = data.get("level")

    category, task, correct_answer = await generate_task_with_gigachat(level=level, category=category)

    await state.update_data(task=task)
    await state.update_data(correct_answer=correct_answer)

    await message.delete()
    await message.answer(f"{category}\n\n{task}",  reply_markup=break_inline_kb)

@router.callback_query(F.data == "task_stop",  StateFilter(""))
async def task_stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Тест Завершен")
    await callback.message.answer("Меню Заданий", reply_markup=tasks_inline_kb)


@router.message(TasksState.question)
async def handle_user_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    task = data.get("task")
    correct_answer = data.get("correct_answer")
    level = data.get("level", 1)

    user_answer = message.text.strip().lower()
    if user_answer == "стоп":
        await state.clear()
        await message.answer("Тест Завершен")
        await message.answer("Меню Заданий", reply_markup=tasks_inline_kb)
        return

    try:
        feedback = await check_answer_with_gigachat(
            task=task,
            correct_answer=correct_answer,
            user_answer=user_answer
        )
        lines = feedback.split("\n", 1)
        correctness_flag = lines[0].strip().lower()
        user_feedback = lines[1].strip() if len(lines) > 1 else ""

        await message.answer(f"Результат:\n{user_feedback}")

        if correctness_flag == "верно":
            level += 1

            await message.answer(
                f"Поздравляем! Вы переходите на уровень {level}. Следующее задание:",
                reply_markup=break_inline_kb
            )
        elif correctness_flag == "неверно":
            level -= 1 if level > 1 else 0

            await message.answer("Попробуйте ещё раз на этом уровне.")

        await state.update_data(level=level)
        db.update_user_level(message.from_user.id, level)

        await send_next_question(message, state)

    except Exception as e:
        await message.answer(f"Произошла ошибка при проверке ответа: {e}")