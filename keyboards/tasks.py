from aiogram.filters import callback_data
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_inline_keyboard(buttons: list[dict]) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text=btn['text'], callback_data=btn.get('callback_data'), url=btn.get('url'))]
        for btn in buttons
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

tasks_buttons = [
    {"text": "✍️ Исправление ошибок", "callback_data": "task_find_errors"},
    {"text": "🔍Поиск символов", "callback_data": "task_find_symbols"},
    {"text": "🖼 Найти лишний элемент", "callback_data": "task_find_extra"},
    {"text": "⏱ Распознавание последовательностей", "callback_data": "task_find_order"},
    {"text": "📊 Тест на память", "callback_data": "task_memory"},
]

reminder_buttons = [
    {'text': 'Включить напоминания', 'callback_data': "reminder_on"},
    {'text': 'Выключить напоминания', 'callback_data': 'reminder_off'},
    {'text': 'Установить время напоминаний', 'callback_data': 'change_reminder_time'}
]

test_buttons = [
    {"text": "❌ Завершить Тест ❌", "callback_data": "task_stop"},
    # {'text': "Продолжить", 'callback_data': "task_continue"}
]

tasks_inline_kb = get_inline_keyboard(tasks_buttons)
reminder_inline_kb = get_inline_keyboard(reminder_buttons)

# Questions
back_inline_kb = get_inline_keyboard([{"text": "📊 Меню задач 📊", "callback_data": "task_menu"}])
break_inline_kb = get_inline_keyboard(test_buttons)

