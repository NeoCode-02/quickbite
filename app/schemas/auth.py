from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user ID or email
    exp: int


class LoginRequest(BaseModel):
    username: str
    password: str
