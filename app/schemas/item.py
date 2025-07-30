from pydantic import BaseModel
from uuid import UUID


class ItemBase(BaseModel):
    name: str
    description: str
    price_cents: int


class ItemCreate(ItemBase):
    restaurant_id: UUID


class ItemResponse(ItemBase):
    id: UUID
    restaurant_id: UUID

    class Config:
        orm_mode = True
