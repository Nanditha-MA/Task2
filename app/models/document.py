import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    public_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String,
        default="pending"
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )