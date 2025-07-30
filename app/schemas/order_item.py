from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel


class OrderStatus(str, Enum):
    PLACED = "placed"
    ACCEPTED = "accepted"
    READY = "ready"
    PICKED_UP = "picked_up"
    DONE = "done"
    CANCELLED = "cancelled"


class OrderItemCreate(BaseModel):
    item_id: UUID
    quantity: int


class OrderCreate(BaseModel):
    restaurant_id: UUID
    delivery_address: str
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    restaurant_id: UUID
    delivery_address: str
    total_cents: int
    status: OrderStatus
    created_at: datetime

    class Config:
        orm_mode = True
