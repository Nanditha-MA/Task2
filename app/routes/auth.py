from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM, create_access_token
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    register_user(db, user.email, user.password, user.role)
    return {"message": "User registered"}


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    access, refresh = login_user(db, user.email, user.password)
    return {"access_token": access, "refresh_token": refresh}


@router.post("/refresh")
def refresh_token(refresh_token: str = Body(...)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        new_access_token = create_access_token({"user_id": user_id})

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )