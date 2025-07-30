from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CourierAssignmentResponse(BaseModel):
    order_id: UUID
    courier_id: UUID
    assigned_at: datetime
    picked_up_at: datetime | None = None
    delivered_at: datetime | None = None

    class Config:
        orm_mode = True
