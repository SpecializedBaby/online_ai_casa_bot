from datetime import date
from pydantic import BaseModel, EmailStr


class PaymentBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    payment_method: str
    invoice_id: int | None


