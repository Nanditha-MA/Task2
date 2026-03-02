from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.services.auth_service import register_user, authenticate_user
from app.services.rate_limiter import check_rate_limit
from app.services.email_service import send_email
from app.schemas.user import UserCreate, UserLogin
from app.schemas.password import ForgotPasswordRequest, VerifyOtpRequest, ResetPasswordRequest
from app.schemas.token import TokenResponse
from app.utils.otp import generate_otp
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register")
def register(data: UserCreate = Body(...), db: Session = Depends(get_db)):
    user = register_user(db, data.email, data.password, data.role)
    send_email(user.email, "Registration Successful", "Your account has been created successfully.")
    return {"message": "User created"}


@router.post("/login", response_model=TokenResponse)
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    check_rate_limit(request)
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"user_id": user.id})
    refresh = create_refresh_token({"user_id": user.id})

    return {"access_token": access, "refresh_token": refresh}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    user.reset_otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    db.commit()

    send_email(
        user.email,
        "Password Reset OTP",
        f"Your OTP is {otp}. It is valid for 5 minutes."
    )

    return {"message": "OTP sent to email"}


@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or user.reset_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if not user.otp_expiry or user.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    return {"message": "OTP verified"}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or user.reset_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if not user.otp_expiry or user.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    user.password = get_password_hash(data.new_password)
    user.reset_otp = None
    user.otp_expiry = None

    db.commit()

    return {"message": "Password updated successfully"}