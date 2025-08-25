from aiogram.fsm.state import StatesGroup, State


class AddOffer(StatesGroup):
    name = State()
    description = State()
    advantages = State()
    url = State()
    price = State()
