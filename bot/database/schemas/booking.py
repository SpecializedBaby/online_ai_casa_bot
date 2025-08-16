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

