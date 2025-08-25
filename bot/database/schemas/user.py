from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: int  # TG user id

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    username: str
    full_name: str
    birthday: Optional[str] = None
    address: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: str
    age: int
    zip_code: str
