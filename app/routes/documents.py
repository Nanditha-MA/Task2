from fastapi import APIRouter, UploadFile, Depends, HTTPException, File
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from typing import List
from app.services.document_service import soft_delete_document_by_public_id
from app.dependencies.auth import require_admin, get_current_user
from app.models.user import User
from app.services.email_service import send_email
from app.services.document_service import (
    create_document,
    get_document_by_public_id,
    update_document_status_by_public_id,
)
from app.services.storage import LocalStorageService
from app.services.cache_service import get_cached, set_cache, delete_cache
from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentStatsResponse
import os

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])
storage = LocalStorageService()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = storage.upload(file)
    doc = create_document(db, file.filename, path, user.id)

    delete_cache("approved_docs")
    delete_cache("admin_stats")

    return {"document_id": doc.public_id}


@router.get("/approved", response_model=List[DocumentResponse])
def get_approved_documents(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    cache_key = f"approved_docs_{skip}_{limit}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    docs = (
        db.query(Document)
        .filter(
            Document.status == "approved",
            Document.is_deleted.is_(False)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = [
        {"id": d.public_id, "title": d.title}
        for d in docs
    ]

    set_cache(cache_key, result)
    return result


@router.get("/{public_id}/download")
def download_document(
    public_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    doc = get_document_by_public_id(db, public_id)

    if doc is None or doc.status != "approved":
        raise HTTPException(status_code=403, detail="Not allowed")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(
        open(doc.file_path, "rb"),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={doc.title}"
        }
    )


@router.put("/admin/{public_id}/approve")
def approve_document(
    public_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    doc = update_document_status_by_public_id(
        db,
        public_id,
        "approved",
        admin.id,
        "approved by admin"
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    owner = db.query(User).filter(User.id == doc.uploaded_by).first()

    if owner:
        send_email(
            owner.email,
            "Document Approved",
            f'Subject: Document Approved\n\nYour document "{doc.title}" has been approved.\n\nYou can now login and download it from your dashboard.'
        )

    delete_cache("approved_docs")
    delete_cache("admin_stats")

    return {"message": "approved"}


@router.put("/admin/{public_id}/reject")
def reject_document(
    public_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    doc = update_document_status_by_public_id(
        db,
        public_id,
        "rejected",
        admin.id,
        "rejected by admin"
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    owner = db.query(User).filter(User.id == doc.uploaded_by).first()

    if owner:
        send_email(
            owner.email,
            "Document Rejected",
            f'Subject: Document Rejected\n\nYour document "{doc.title}" has been rejected.\n\nReason: rejected by admin.\n\nYou can contact support or upload a revised document.'
        )

    delete_cache("approved_docs")
    delete_cache("admin_stats")

    return {"message": "rejected"}


@router.get("/admin/stats", response_model=DocumentStatsResponse)
def admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    cached = get_cached("admin_stats")
    if cached:
        return cached

    total = db.query(Document).filter(Document.is_deleted.is_(False)).count()
    approved = db.query(Document).filter(Document.status == "approved", Document.is_deleted.is_(False)).count()
    rejected = db.query(Document).filter(Document.status == "rejected", Document.is_deleted.is_(False)).count()
    pending = db.query(Document).filter(Document.status == "pending", Document.is_deleted.is_(False)).count()

    result = {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    }

    set_cache("admin_stats", result)
    return result


@router.delete("/{public_id}")
def delete_document(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = get_document_by_public_id(db, public_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user.role != "admin" and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    soft_delete_document_by_public_id(db, public_id)

    delete_cache("approved_docs")
    delete_cache("admin_stats")

    return {"message": "deleted"}