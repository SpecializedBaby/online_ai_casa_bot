from aiogram.fsm.state import StatesGroup, State


class JourneyOrder(StatesGroup):
    departure = State()
    destination = State()
    travel_date = State()
    seat_type = State()
    quantity = State()


class GermanyPassOrder(StatesGroup):
    birthday = State()
    address = State()
    month = State()
