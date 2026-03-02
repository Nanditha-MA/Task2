import os
import uuid
from fastapi import UploadFile, HTTPException

ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg"]
MAX_SIZE = 5 * 1024 * 1024

class LocalStorageService:
    def upload(self, file: UploadFile):
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename missing")

        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Only PDF and image files are allowed")

        contents = file.file.read()

        if len(contents) > MAX_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")

        file.file.seek(0)

        os.makedirs("uploads", exist_ok=True)

        ext = file.filename.rsplit(".", 1)[-1]
        unique_name = f"{uuid.uuid4()}.{ext}"
        path = os.path.join("uploads", unique_name)

        with open(path, "wb") as buffer:
            buffer.write(file.file.read())

        return path