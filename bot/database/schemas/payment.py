from typing import Optional
from pydantic import BaseModel


class PaymentBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    payment_method: str
    invoice_id: Optional[int] = None
