from datetime import date
from pydantic import BaseModel, EmailStr


class RouteBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    departure: str
    destination: str
    cost: float
