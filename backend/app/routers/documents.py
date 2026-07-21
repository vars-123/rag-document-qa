import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile

from app.models.document import DocumentListResponse, DocumentResponse
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_document as embed_doc
from app.services.pdf_service import extract_text

router = APIRouter(prefix="/api/documents", tags=["documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPE = "application/pdf"

BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@dataclass
class _DocumentRecord:
    id: str
    filename: str
    status: str
    uploaded_at: datetime
    file_path: str
    chunk_count: int = 0


_documents: dict[str, _DocumentRecord] = {}


def _to_response(rec: _DocumentRecord) -> DocumentResponse:
    return DocumentResponse(
        id=rec.id,
        filename=rec.filename,
        status=rec.status,
        uploaded_at=rec.uploaded_at,
        chunk_count=rec.chunk_count,
    )


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
    rec = _DocumentRecord(
        id=doc_id,
        filename=file.filename or "untitled",
        status="uploaded",
        uploaded_at=now,
        file_path=file_path,
    )
    _documents[doc_id] = rec
    return _to_response(rec)


@router.get("")
async def list_documents() -> DocumentListResponse:
    return DocumentListResponse(
        documents=[_to_response(rec) for rec in _documents.values()]
    )


@router.post("/{doc_id}/process")
async def process_document(doc_id: str) -> DocumentResponse:
    rec = _documents.get(doc_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Document not found")

    if rec.status != "uploaded":
        raise HTTPException(
            status_code=400,
            detail=f"Document status is '{rec.status}', expected 'uploaded'",
        )

    if not os.path.exists(rec.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    rec.status = "processing"
    try:
        text = extract_text(rec.file_path)
        if not text.strip():
            rec.status = "failed"
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the PDF",
            )
        chunks = chunk_text(text)
        rec.chunk_count = len(chunks)
        rec.status = "processed"
    except HTTPException:
        raise
    except Exception as exc:
        rec.status = "failed"
        raise HTTPException(
            status_code=500, detail=f"Processing failed: {exc}"
        ) from exc

    return _to_response(rec)


@router.post("/{doc_id}/embed")
async def embed_document(doc_id: str) -> DocumentResponse:
    rec = _documents.get(doc_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Document not found")

    if rec.status != "processed":
        raise HTTPException(
            status_code=400,
            detail=f"Document status is '{rec.status}', expected 'processed'",
        )

    if not os.path.exists(rec.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    rec.status = "embedding"
    try:
        text = extract_text(rec.file_path)
        chunks = chunk_text(text)
        await embed_doc(doc_id, chunks)
        rec.chunk_count = len(chunks)
        rec.status = "embedded"
    except ValueError as exc:
        rec.status = "failed"
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        rec.status = "failed"
        raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}") from exc

    return _to_response(rec)
