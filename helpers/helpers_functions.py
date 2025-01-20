from helpers import NO_REMINDER_TEXT, REMINDER_MENU_TEXT


def format_reminder_message(reminder):
    if reminder:
        return REMINDER_MENU_TEXT.format(
            status="Включены ✅" if reminder[3] else "Выключены❌",
            time=reminder[2],
        )
    return NO_REMINDER_TEXT


def format_rating_message(top_users, user_position, user_rating):
    """Форматирование сообщения рейтинга."""
    top_users_text = "\n".join(
        [
            f"{i + 1}. Пользователь {user_id}: {rating} очков"
            for i, (user_id, rating) in enumerate(top_users)
        ]
    )
    user_text = (
        f"\n\nВы занимаете {user_position} место с {user_rating} очками."
        if user_position > 0
        else "\n\nВы пока не участвуете в рейтинге."
    )
    return f"🏆 Топ-5 пользователей:\n{top_users_text}{user_text}"
