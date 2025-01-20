from aiogram.fsm.state import State, StatesGroup


class TasksState(StatesGroup):
    question = State()
