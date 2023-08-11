from aiogram.dispatcher.filters.state import State, StatesGroup

class WaitState(StatesGroup):
    WAIT_NUMBER = State()
    WAIT_FILM = State()
    WAIT_KEYWORD = State()