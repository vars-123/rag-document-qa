from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    uploaded_at: datetime
    chunk_count: int = 0
    error: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
