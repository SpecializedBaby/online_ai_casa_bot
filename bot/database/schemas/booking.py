from datetime import date
from pydantic import BaseModel, EmailStr


class UserTGID(BaseModel):
    id: int

    class Config:
        from_attributes = True


class BookingByStatus(BaseModel):
    status: str | None


class BookingsByUser(BookingByStatus):
    user_id: int | None
