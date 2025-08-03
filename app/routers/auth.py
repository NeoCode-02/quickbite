from fastapi import APIRouter, HTTPException
from app.models import User
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, Token
from app.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_confirmation_token,
    verify_password,
    get_password_hash,
)
from app.tasks import send_email
from app.dependencies import db_dep
from app.settings import FRONTEND_URL

router = APIRouter()


@router.post("/register/")
def register_user(register_data: UserCreate, db: db_dep):
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    is_superuser = False
    is_verified = False

    if db.query(User).count() == 0:
        is_superuser = True
        is_verified = True

    user = User(
        username=register_data.username,
        email=register_data.email,
        hashed_pw=get_password_hash(register_data.hashed_pw),
        is_superuser=is_superuser,
        is_active=True,
        is_verified=is_verified,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    if not is_verified:
        token = generate_confirmation_token(email=user.email)
        send_email.delay(
            to_email=user.email,
            subject="Confirm your registration",
            body=f"Click to confirm: {FRONTEND_URL}/auth/confirm/{token}/",
        )

    return {"detail": f"User registered. {'Confirmation email sent.' if not is_verified else 'Auto-confirmed.'}"}


@router.post("/login/", response_model=Token)
def login_user(login_data: LoginRequest, db: db_dep):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_pw):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Account not confirmed")

    payload = {
        "sub": user.username,
        "email": user.email,
        "role": user.role.value,
    }

    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/confirm/{token}/", response_model=dict)
def confirm_email(token: str, db: db_dep):
    try:
        payload = decode_token(token)
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "User already confirmed"}

        user.is_verified = True
        db.commit()
        return {"message": "Email confirmed successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.post("/logout/", response_model=dict)
def logout_user(token_data: Token, db: db_dep) -> dict:
    try:
        payload = decode_token(token_data.access_token)
        email = payload.get("email")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid access token")

        return {"message": f"User {email} logged out (client should delete token)."}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
