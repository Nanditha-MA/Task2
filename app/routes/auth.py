from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.core.database import get_db
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
