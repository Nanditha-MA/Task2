from sqlalchemy.orm import Session
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


def get_all_documents(db: Session):
    return db.query(Document).all()


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
