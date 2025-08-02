from fastapi import APIRouter, HTTPException
from app.models import User
from jose import JWTError
from app.schemas.user import UserCreate
from app.schemas.auth import UserLogin, Token
from app.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_confirmation_token,
    verify_password,
)
from app.tasks import send_email
from app.dependencies import db_dep
from app.settings import FRONTEND_URL

router = APIRouter()


@router.post("/register/")
async def register_user(register_data: UserCreate, db: db_dep) -> dict:
    existing_user = db.query(User).filter(User.email == register_data.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    is_first_user = db.query(User).count() == 0

    if is_first_user:
        is_superuser = True
        is_verified = True

    user = User(
        username=register_data.username,
        email=register_data.email,
        hashed_pw=register_data.hashed_pw,
        is_superuser=is_superuser,
        is_active=True,
        is_verified=is_verified,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_confirmation_token(email=user.email)
    send_email.delay(
        to_email=user.email,
        subject="Confirm your registration to Bookla",
        body=f"Click to confirm: {FRONTEND_URL}/auth/confirm/{token}/",
    )

    return {"detail": f"Confirmation email sent to {user.email}."}


@router.post("/login/")
async def login_user(login_data: UserLogin, db: db_dep) -> Token:
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_pw):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Account not confirmed")

    payload = {"email": user.email, "is_superuser": user.is_superuser}

    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.get("/confirm/{token}/")
async def confirm_email(token: str, db: db_dep) -> dict:
    try:
        payload = decode_token(token)
        email = payload.get("email")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "User already confirmed"}

        user.is_verified = True
        db.commit()
        db.refresh(user)

        return {"message": "Email confirmed successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout/")
async def logout_user(token_data: Token) -> dict:
    try:
        payload = decode_token(token_data.access_token)
        email = payload.get("email")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid access token")

        return {"message": "Logged out successfully"}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid access token") from e
