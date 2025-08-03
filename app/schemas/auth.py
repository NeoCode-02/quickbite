from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user ID or email
    exp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
