from aiogram.fsm.state import StatesGroup, State


class TicketOrder(StatesGroup):
    departure = State()
    destination = State()
    travel_date = State()
    seat_type = State()
    confirm = State()
