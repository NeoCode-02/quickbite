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
    hashed_pw: str


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr | None = None
    phone: str | None = None
    hashed_pw: str | None = None


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True
