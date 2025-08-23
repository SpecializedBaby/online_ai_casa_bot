from typing import Optional

from pydantic import BaseModel


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
    payment_id: Optional[int] = None
    date: str
    seat_type: str = "standard"
    quantity: Optional[int] = 1
    price: Optional[float]
    status: str


class SetPayment(BaseModel):
    payment_id: int
