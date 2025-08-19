from datetime import date
from pydantic import BaseModel, EmailStr


class RouteBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class GetRoute(BaseModel):
    departure: str
    destination: str


class RouteCreate(GetRoute):
    cost: float
