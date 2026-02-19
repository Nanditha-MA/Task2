from fastapi import FastAPI
from app.core.database import Base, engine

from app.models.user import User
from app.models.document import Document
from app.models.document_status_history import DocumentStatusHistory

from app.routes.auth import router as auth_router
from app.routes.documents import router as doc_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(doc_router)

@app.get("/")
def root():
    return {"message": "API running"}
