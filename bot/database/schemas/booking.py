from datetime import date
from pydantic import BaseModel, EmailStr


class BookingBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class BookingByStatus(BaseModel):
    status: str | None


class BookingsByUser(BookingByStatus):
    user_id: int | None


class BookingUpdate(BookingBase, BookingByStatus):
    pass


class CreateBooking(BookingUpdate):
    user_id: int
    route_id: int | None
    payment_id: int | None
    date: str
    seat_type: str
    quantity: int
    price: float | None
    status: str


class SetPayment(BookingByStatus):
    payment_id: int
