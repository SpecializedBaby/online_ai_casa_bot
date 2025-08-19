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


class CreateBooking(BaseModel):
    user_id: int
    route_id: int
    payment_id: int | None
    date: str
    seat_type: str
    quantity: int | None
    price: float | None
    status: str


class SetPayment(BaseModel):
    payment_id: int
