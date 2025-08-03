from fastapi import APIRouter, HTTPException
from app.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.dependencies import db_dep, current_user_dep
from app.schemas.password import ChangePasswordRequest
from app.utils import verify_password, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me/", response_model=UserResponse)
def get_me(current_user: current_user_dep):
    return current_user


@router.put("/me/", response_model=UserResponse)
def update_me(
    update_data: UserUpdate,
    db: db_dep,
    current_user: current_user_dep,
):
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password/", response_model=dict)
def change_password(
    data: ChangePasswordRequest,
    db: db_dep,
    current_user: current_user_dep,
):
    if not verify_password(data.old_password, current_user.hashed_pw):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.hashed_pw = get_password_hash(data.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}