from aiogram.fsm.state import StatesGroup, State


class RegisterUser(StatesGroup):
    full_name = State()
    birthday = State()
    address = State()  # ZIP code only
    email = State()

class GermanyPassOrder(StatesGroup):
    month = State()


class JourneyOrder(StatesGroup):
    departure = State()
    destination = State()
    travel_date = State()
    seat_type = State()
    quantity = State()
