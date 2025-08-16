from datetime import date
from pydantic import BaseModel, EmailStr


class UserTGID(BaseModel):
    id: int

    class Config:
        from_attributes = True


class UserCreate(UserTGID):
    username: str
    full_name: str


class UserRegister(UserCreate):
    birthday: str
    address: str
