from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.settings import ALGORITHM, SECRET_KEY

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# oauth2_dep = Annotated[str, Depends(oauth2_scheme)]
dbearer_scheme = HTTPBearer(auto_error=False)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db_session)]


class Pagination:
    def __init__(
        self,
        q: str | None = Query(None, description="Search query"),
        offset: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    ):
        self.q = q
        self.offset = offset
        self.limit = limit


PaginationDep = Annotated[Pagination, Depends()]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(dbearer_scheme),
    db: Session = Depends(get_db_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials or not credentials.credentials:
        raise credentials_exception

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if not email:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address",
        )

    return user


current_user_dep = Annotated[User, Depends(get_current_user)]
