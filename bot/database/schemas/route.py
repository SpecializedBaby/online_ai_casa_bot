from pydantic import BaseModel


class RouteBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class RouteFind(BaseModel):
    departure: str
    destination: str

    class Config:
        from_attributes = True


class RouteCostUpdate(BaseModel):
    cost: float


class RouteCreate(RouteFind, RouteCostUpdate):
    pass

