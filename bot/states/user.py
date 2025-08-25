from aiogram.fsm.state import StatesGroup, State


class JourneyBooking(StatesGroup):
    departure = State()
    destination = State()
    travel_date = State()
    seat_type = State()
    quantity = State()
    confirmation = State()


class OfferOrder(StatesGroup):
    user_id = State()
    offer_id = State()
    full_name = State
    age = State()
    zip_code = State()
    month = State()
    confirmation = State()
