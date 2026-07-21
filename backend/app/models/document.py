from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
