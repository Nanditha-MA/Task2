from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base

class DocumentStatusHistory(Base):
    __tablename__ = "document_status_history"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    changed_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)