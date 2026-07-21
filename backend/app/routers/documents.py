import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile

from app.models.document import DocumentListResponse, DocumentResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPE = "application/pdf"

# Resolve uploads directory relative to the backend root
BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory document store: id -> metadata
_documents: dict[str, DocumentResponse] = {}


@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile) -> DocumentResponse:
    if file.content_type != ALLOWED_CONTENT_TYPE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only PDF files are allowed.",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(contents)

    now = datetime.now(timezone.utc)
    doc = DocumentResponse(
        id=doc_id,
        filename=file.filename or "untitled",
        status="uploaded",
        uploaded_at=now,
    )
    _documents[doc_id] = doc
    return doc


@router.get("")
async def list_documents() -> DocumentListResponse:
    return DocumentListResponse(documents=list(_documents.values()))
