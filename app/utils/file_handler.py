import os
import uuid
from fastapi import UploadFile, HTTPException
from fastapi import UploadFile, HTTPException

ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def validate_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Unsupported file type")

    content = file.file.read()
    size = len(content)

    if size > MAX_SIZE:
        raise HTTPException(400, "File too large")

    file.file.seek(0)


def save_file(file: UploadFile):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    if not file.filename:
        raise HTTPException(400, "Filename missing")

    # safe extension extraction
    parts = file.filename.split(".")
    ext = parts[-1] if len(parts) > 1 else "bin"

    unique_name = f"{uuid.uuid4()}.{ext}"

    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    file.file.seek(0)

    return file_path
