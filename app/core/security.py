from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict):
    payload = data.copy()
    payload.update({"type": "access"})
    payload.update({
        "exp": datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    payload = data.copy()
    payload.update({"type": "refresh"})
    payload.update({
        "exp": datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)