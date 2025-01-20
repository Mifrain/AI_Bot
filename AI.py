import asyncio
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage, HumanMessage
import re

from config import settings
# from bot import logger


if not settings.GIGACHAT_API_KEY:
    raise EnvironmentError("API ключ GigaChat не найден. Проверьте файл .env.")

# Инициализация клиента GigaChat
giga = GigaChat(credentials=settings.GIGACHAT_API_KEY, model="GigaChat-Pro", verify_ssl_certs=False)

async def invoke_gigachat_async(messages):
    return await asyncio.to_thread(giga.invoke, messages)


#можно не передавать тогда будет случайная категория.
async def generate_task_with_gigachat(level: int, category: str = None):
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        try:
            category_filter = f"Категория задания: {category}" if category else "Случайная категория."
            messages = [
                SystemMessage(content="Вы создаёте задания для бота, который помогает развивать внимание пользователей."),
                HumanMessage(content=f"""
Вы создаёте задание для тренировки внимания.

**Уровень сложности:** {level}.
**{category_filter}**

Создайте задание для одной из следующих категорий:
1. Исправление ошибок: текст с 3-5 орфографическими, грамматическими или пунктуационными ошибками. Пользователь должен найти их и исправить.
2. Поиск символов: таблица или текст, где пользователь должен найти указанный символ или последовательность символов.
3. Найти лишний элемент: список слов, чисел или символов, где одно из них выбивается из общего ряда.
4. Распознавание последовательностей: числовая или логическая последовательность, где пользователь должен определить следующий элемент.
5. Тест на память: текст или таблица символов, которые пользователь должен запомнить. После этого задайте вопрос по содержимому.

**ВНИМАНИЕ! Ожидаемый формат ответа:**  
Ответ должен быть структурирован без использования Markdown, HTML или других разметок. Ответ должен быть представлен в следующем формате:

Категория: Название категории  
Текст задания: Ваш текст задания (одно или несколько предложений)  
Правильный ответ: Краткое и точное решение (одно или несколько предложений)

Пример:  
Категория: Исправление ошибок  
Текст задания: Найдите ошибки в этом тексте: \"Они шёл в парке, но не взяла зонтик.\"  
Правильный ответ: \"Он шёл в парке, но не взял зонтик.\"

Убедитесь, что ответ полностью соответствует указанному формату.
""")
            ]
            response = await invoke_gigachat_async(messages)
            result = response.content.strip()
            # logger.info(f"Полученный ответ: {result}")

            # Обновлённое регулярное выражение для разбора ответа
            match = re.search(
                r"Категория:\s*(.*?)\s+Текст задания:\s*(.*?)\s+Правильный ответ:\s*(.*)",
                result,
                re.DOTALL,
            )
            if not match:
                # logger.error(f"Неверный формат ответа: {result}")
                raise ValueError("Некорректный формат задания от GigaChat.")

            category = match.group(1).strip()
            task = match.group(2).strip()
            correct_answer = match.group(3).strip()
            return category, task, correct_answer
        except Exception as e:
            attempts += 1
            # logger.error(f"Попытка {attempts} из {max_attempts} не удалась. Ошибка: {e}")
            await asyncio.sleep(1)

    raise RuntimeError("Не удалось создать задание после 3 попыток.")


# Асинхронная функция проверки ответа
async def check_answer_with_gigachat(task, correct_answer, user_answer):
    messages = [
        SystemMessage(content="Вы бот для проверки заданий."),
        HumanMessage(content=f"""
            Вы являетесь ботом, который проверяет ответы пользователей. Ответ должен быть структурирован следующим образом:
            1. Первая строка — это флаг правильности:
            - "верно" — если пользователь ответил правильно.
            - "неверно" — если пользователь ошибся.
            2. Остальной текст — сообщение для пользователя:
            - Если ответ верный: поздравьте пользователя и кратко повторите правильный ответ.
            - Если ответ неверный: вежливо укажите на ошибку, объясните правильный ответ и предложите попробовать ещё раз.

            Пример:
            верно
            Молодец! Ты ответил верно. Каждое число последовательности удваивается, поэтому после 32 идёт 64.

            Или:
            неверно
            К сожалению, это неверно. Правильный ответ: 64. Каждое число последовательности удваивается. Попробуй ещё раз!

            Задание: {task}
            Ответ пользователя: {user_answer}
            Правильный ответ: {correct_answer}

            Пожалуйста, сформируйте ответ в указанном формате.
    """)
    ]
    response = await invoke_gigachat_async(messages)
    feedback = response.content.strip()
    return feedback


# # Асинхронная консольная программа
# async def main():
#
#     #убери и замени.
#     print("Добро пожаловать в тренировку внимания с GigaChat!")
#
#     # это должно храниться либо в пользователе, для каждой категории в бд, либо просто единоразово.
#     level = 1
#
#     category = None
#
#
#     #заменить для бота, команда выход реализовано так
#     # выйти и сменить категорию - команды.
#     while True:
#         if not category:
#             print("\nВыберите категорию для начала:")
#             print("1. Исправление ошибок")
#             print("2. Поиск символов")
#             print("3. Найти лишний элемент")
#             print("4. Распознавание последовательностей")
#             print("5. Тест на память")
#             category_choice = input("Введите номер категории: ").strip()
#
#             category_map = {
#                 "1": "Исправление ошибок",
#                 "2": "Поиск символов",
#                 "3": "Найти лишний элемент",
#                 "4": "Распознавание последовательностей",
#                 "5": "Тест на память"
#             }
#             category = category_map.get(category_choice, None)
#             if not category:
#                 print("Неверный выбор категории. Попробуйте снова.")
#                 continue
#
#         # Генерация задания
#         try:
#             category, task, correct_answer = await generate_task_with_gigachat(level, category)
#             print(f"\nКатегория: {category}")
#             print(f"Задание: {task}")
#         except Exception as e:
#             print(f"Ошибка при генерации задания: {e}")
#             continue
#
#         # Запрос ответа пользователя
#         user_answer = input("Введите ваш ответ или 'Сменить категорию' для выбора новой: ").strip()
#         if user_answer.lower() == "выйти":
#             print("Спасибо за игру! До свидания!")
#             break
#         elif user_answer.lower() == "сменить категорию":
#             category = None
#             continue
#
#         # Проверка ответа
#         try:
#             feedback = await check_answer_with_gigachat(
#                 task=task,
#                 correct_answer=correct_answer,
#                 user_answer=user_answer
#             )
#             # Разделяем feedback на флаг правильности и сообщение для пользователя
#             lines = feedback.split("\n", 1)
#             correctness_flag = lines[0].strip().lower()  # "верно" или "неверно"
#             user_feedback = lines[1].strip() if len(lines) > 1 else ""
#
#             # Печатаем сообщение для пользователя
#             print("\nРезультат:")
#             print(user_feedback)
#
#             # Проверяем флаг правильности
#             if correctness_flag == "верно":
#                 level += 1  # Увеличиваем уровень сложности
#             elif correctness_flag == "неверно":
#                 print("Попробуйте ещё раз на этом же уровне.")
#         except Exception as e:
#             print(f"Ошибка при проверке ответа: {e}")
#             break
#
# if __name__ == "__main__":
#     asyncio.run(main())
