from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    email = State()
    confirmation_code = State()
    scenario = State()
    developer_mode = State()
