from pydantic import BaseModel, EmailStr
from uuid import UUID


class RestaurantBase(BaseModel):
    name: str
    address: str
    phone: str
    email: EmailStr
    description: str | None = None
    operating_hours: str


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    description: str | None = None
    operating_hours: str | None = None


class RestaurantResponse(RestaurantBase):
    id: UUID

    class Config:
        orm_mode = True
