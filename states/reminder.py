from aiogram.fsm.state import State, StatesGroup


class ReminderState(StatesGroup):
    time_change = State()
    time = State()
