from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_menu_keyboard(buttons: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn)] for btn in buttons],
        resize_keyboard=True
    )

def get_inline_keyboard(buttons: list[dict]) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text=btn['text'], callback_data=btn.get('callback_data'), url=btn.get('url'))]
        for btn in buttons
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

main_menu = [
    "📋 Задания",
    "⏰ Напоминания",
    "🏆 Уровень",
    "ℹ️ Помощь"
]

main_menu_kb = get_menu_keyboard(main_menu)

choose_target = [
    {"text": "Хочу улучшить концентрацию", "callback_data": "improve_concentration"},
    {"text": "Увеличить скорость реакции", "callback_data": "increase_reaction_speed"},
    {"text": "Улучшить память", "callback_data": "improve_memory"},
    {"text": "Для развлечения", "callback_data": "for_fun"}
]

choose_target_kb = get_inline_keyboard(choose_target)