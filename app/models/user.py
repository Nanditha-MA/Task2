from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from app.core.database import Base
from datetime import datetime
from typing import Optional


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")

    reset_otp: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    otp_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)