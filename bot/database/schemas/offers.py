from pydantic import BaseModel, HttpUrl


class OffersBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class OffersCreate(BaseModel):
    name: str
    description: str
    advantages: str
    url: HttpUrl
    price: float


class OfferName(BaseModel):
    name: str

    class Config:
        from_attributes = True
