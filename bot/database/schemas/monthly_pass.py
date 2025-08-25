from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class PassBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class PassCreate(BaseModel):
    user_id: int
    payment_id: Optional[int] = None
    offer_id: int
    month: date
    status: str = Field(dedault="unpaid")


class PassStatus(BaseModel):
    status: str
