from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.models.document import Document
from app.models.document_status_history import DocumentStatusHistory

def create_document(
    db: Session,
    filename: str,
    path: str,
    user_id: int
):
    doc = Document(
        title=filename,
        file_path=path,
        uploaded_by=user_id
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


def get_user_documents(db: Session, user_id: int):
    return db.query(Document).filter(
        Document.uploaded_by == user_id,
        Document.is_deleted.is_(False)
    ).all()


def get_document_by_public_id(
    db: Session,
    public_id: str
) -> Optional[Document]:
    return db.query(Document).filter(
        Document.public_id == public_id,
        Document.is_deleted.is_(False)
    ).first()


def update_document_status_by_public_id(
    db: Session,
    public_id: str,
    status: str,
    admin_id: int,
    reason: str
):
    doc = get_document_by_public_id(db, public_id)

    if not doc:
        return None

    doc.status = status

    history = DocumentStatusHistory(
        document_id=doc.id,
        changed_by=admin_id,
        status=status,
        reason=reason,
        changed_at=datetime.utcnow()
    )

    db.add(history)
    db.commit()
    db.refresh(doc)

    return doc


def soft_delete_document_by_public_id(
    db: Session,
    public_id: str
):
    doc = get_document_by_public_id(db, public_id)

    if not doc:
        return None

    doc.is_deleted = True
    doc.deleted_at = datetime.utcnow()

    db.commit()
    db.refresh(doc)

    return doc