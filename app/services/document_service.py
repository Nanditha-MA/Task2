from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models.document import Document


def create_document(db: Session, filename: str, path: str, user_id: int):
    doc = Document(
        filename=filename,
        file_path=path,
        user_id=user_id,
        status="pending"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_user_documents(db: Session, user_id: int):
    return db.query(Document).filter(
        Document.user_id == user_id
    ).all()


def get_document(db: Session, doc_id: int, user_id: int):
    return db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == user_id
    ).first()


def get_all_documents(
    db: Session,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Document)

    if status:
        query = query.filter(Document.status == status)

    if start_date and end_date:
        query = query.filter(
            and_(
                Document.created_at >= start_date,
                Document.created_at <= end_date
            )
        )

    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))

    total = query.count()
    documents = query.offset(skip).limit(limit).all()

    return documents, total


def update_document_status(db: Session, doc_id: int, status: str):
    doc = db.query(Document).filter(
        Document.id == doc_id
    ).first()

    if not doc:
        return None

    doc.status = status
    db.commit()
    db.refresh(doc)

    return doc
