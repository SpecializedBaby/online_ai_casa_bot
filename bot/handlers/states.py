from aiogram.fsm.state import StatesGroup, State


class GermanyPassOrder(StatesGroup):
    month = State()
    full_name = State()
    birthday = State()
    email = State()
    address = State()


class JourneyOrder(StatesGroup):
    departure = State()
    destination = State()
    travel_date = State()
    seat_type = State()
    quantity = State()
