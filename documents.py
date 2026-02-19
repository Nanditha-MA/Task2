from fastapi import APIRouter, UploadFile, Depends, HTTPException, File, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.dependencies.auth import require_admin, get_current_user
from app.services.document_service import (
    create_document,
    get_user_documents,
    get_document,
    update_document_status,
    get_all_documents
)
from app.services.background_service import log_document_approval
from app.core.database import get_db
from app.utils.file_handler import validate_file, save_file

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    validate_file(file)

    if not file.filename:
        raise HTTPException(400, "Invalid filename")

    path = save_file(file)

    doc = create_document(db, file.filename, path, user.id)

    return {"document_id": doc.id}


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    docs = get_user_documents(db, user.id)

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_path": d.file_path
        }
        for d in docs
    ]


@router.get("/{doc_id}")
def download_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    doc = get_document(db, doc_id, user.id)

    if not doc:
        raise HTTPException(404, "Document not found")

    return FileResponse(
        path=str(doc.file_path),
        filename=str(doc.filename)
    )


@router.get("/admin/all")
def list_all_documents(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    docs = get_all_documents(db)

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "status": d.status,
            "uploaded_by": d.user_id
        }
        for d in docs
    ]


@router.put("/admin/{doc_id}/approve")
def approve_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    doc = update_document_status(db, doc_id, "approved")

    if not doc:
        raise HTTPException(404, "Document not found")

    background_tasks.add_task(
        log_document_approval,
        doc.id,
        admin.id
    )

    return {"message": "Document approved successfully"}


@router.put("/admin/{doc_id}/reject")
def reject_document(
    doc_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    doc = update_document_status(db, doc_id, "rejected")

    if not doc:
        raise HTTPException(404, "Document not found")

    return {"message": "Document rejected"}
