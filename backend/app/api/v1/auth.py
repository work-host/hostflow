from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.core.security import verify_password, create_access_token, hash_password
from app.schemas.auth import LoginResponse, UserPublic, ChangePasswordIn
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not user.is_active or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    if not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    token = create_access_token(sub=user.email, extra={"role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        },
    }


@router.get("/me", response_model=UserPublic)
def me(current: User = Depends(get_current_user)):
    return {
        "id": current.id,
        "email": current.email,
        "role": current.role,
        "is_active": current.is_active,
    }


@router.post("/change-password")
def change_password(
    payload: ChangePasswordIn,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current.password_hash or ""):
        raise HTTPException(status_code=400, detail="Old password invalid")
    current.password_hash = hash_password(payload.new_password)
    db.add(current)
    db.commit()
    return {"status": "ok"}
