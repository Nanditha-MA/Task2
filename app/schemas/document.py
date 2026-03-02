from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    title: str


class DocumentStatsResponse(BaseModel):
    total: int
    approved: int
    rejected: int
    pending: int


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    status: str
    created_at: datetime