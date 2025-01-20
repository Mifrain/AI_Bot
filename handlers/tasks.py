import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from AI import check_answer_with_gigachat, generate_task_with_gigachat
from database import db
from helpers import category_map
from keyboards.tasks import break_inline_kb, tasks_inline_kb
from states.tasks import TasksState

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("task_") & ~F.data.endswith("_stop"))
async def task_start(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик старта задания."""
    await state.clear()

    category = category_map.get(callback_query.data)
    if category is None:
        await callback_query.message.answer("Неизвестная категория задания.")
        return

    level = db.get_user_level(callback_query.from_user.id)
    logger.info(
        f"Начало задания: категория={category}, уровень={level}, пользователь={callback_query.from_user.id}"
    )

    await state.update_data(
        category=category, level=level
    )  # Сохраняем название категории
    await state.set_state(TasksState.question)

    await callback_query.message.answer(
        f"{category}\nНачинаем генерировать задания!\n\nДля выхода напишите 'стоп' или воспользуйтесь кнопкой выхода."
    )
    await send_next_question(callback_query.message, state)


@router.callback_query(F.data == "task_stop")
async def task_stop(callback: CallbackQuery, state: FSMContext):
    """Завершение задания пользователем."""
    await state.clear()
    await callback.message.answer("Тест Завершен.")
    await callback.message.answer("Меню Заданий", reply_markup=tasks_inline_kb)
    logger.info(f"Пользователь {callback.from_user.id} завершил тест.")


async def send_next_question(message: Message, state: FSMContext):
    """Отправляет следующее задание пользователю."""
    data = await state.get_data()
    category = data.get("category")
    level = data.get("level")

    try:
        # Получаем все данные, включая баллы за задание
        category_name, task, correct_answer, points = await generate_task_with_gigachat(
            level=level, category=category
        )
        if not task or not correct_answer:
            logger.warning(
                f"Не удалось сгенерировать задание для пользователя {message.from_user.id}."
            )
            await message.answer("Не удалось сгенерировать задание. Попробуйте позже.")
            return
    except Exception as e:
        logger.error(f"Ошибка при генерации задания: {e}")
        await message.answer(f"Ошибка при генерации задания: {e}")
        return

    # Сохраняем данные задания в состояние FSM
    await state.update_data(task=task, correct_answer=correct_answer, points=points)

    try:
        await message.delete()
    except Exception:
        logger.warning(
            f"Не удалось удалить предыдущее сообщение пользователя {message.from_user.id}."
        )

    await message.answer(f"{category_name}\n\n{task}", reply_markup=break_inline_kb)


@router.message(TasksState.question)
async def handle_user_answer(message: Message, state: FSMContext):
    """Обрабатывает ответ пользователя на задание."""
    data = await state.get_data()
    task = data.get("task")
    correct_answer = data.get("correct_answer")
    points = data.get("points", 0)  # Получаем баллы из состояния
    level = data.get("level", 1)

    user_answer = message.text.strip().lower()
    if user_answer == "стоп":
        await state.clear()
        await message.answer("Тест Завершен.")
        await message.answer("Меню Заданий", reply_markup=tasks_inline_kb)
        logger.info(f"Пользователь {message.from_user.id} завершил задание досрочно.")
        return

    try:
        feedback = await check_answer_with_gigachat(
            task=task, correct_answer=correct_answer, user_answer=user_answer
        )
        lines = feedback.split("\n", 1)
        if len(lines) < 2 or lines[0].strip().lower() not in ["верно", "неверно"]:
            logger.warning(
                f"Некорректный формат ответа GigaChat для пользователя {message.from_user.id}: {feedback}"
            )
            await message.answer("Не удалось распознать результат. Попробуйте позже.")
            return

        correctness_flag = lines[0].strip().lower()
        user_feedback = lines[1].strip()

        await message.answer(f"Результат:\n{user_feedback}")

        if correctness_flag == "верно":
            level += 1
            db.update_user_rating(message.from_user.id, points)  # Обновляем рейтинг
            logger.info(
                f"Пользователь {message.from_user.id} успешно прошёл задание. Новый уровень: {level}, добавлено баллов: {points}"
            )
            await message.answer(
                f"Поздравляем! Вы переходите на уровень {level}. Ваш рейтинг увеличен на {points} баллов! Следующее задание:"
            )
        elif correctness_flag == "неверно":
            level -= 1 if level > 1 else 0
            logger.info(
                f"Пользователь {message.from_user.id} ошибся. Уровень снижен до: {level}"
            )
            await message.answer("Ты ошибся, твой уровень понижен. Следующее задание:")

        await state.update_data(level=level)
        db.update_user_level(message.from_user.id, level)

        await send_next_question(message, state)

    except Exception as e:
        logger.error(
            f"Ошибка при проверке ответа пользователя {message.from_user.id}: {e}"
        )
        await message.answer(f"Произошла ошибка при проверке ответа: {e}")
