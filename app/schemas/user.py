from pydantic import BaseModel, EmailStr
from uuid import UUID
from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "customer"
    COURIER = "courier"
    ADMIN = "admin"


class UserBase(BaseModel):
    username: str
    email: EmailStr | None = None
    phone: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr | None = None
    phone: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    id: UUID
    role: UserRole

    class Config:
        orm_mode = True
