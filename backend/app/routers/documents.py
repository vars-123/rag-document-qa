import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile

from app.dependencies import get_client_id
from app.models.document import DocumentListResponse, DocumentResponse
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_document as embed_doc
from app.services.chat_history_service import delete_document_history
from app.services.pdf_service import extract_text
from app.services.vector_service import delete_collection

router = APIRouter(prefix="/api/documents", tags=["documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPE = "application/pdf"

BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

NO_TEXT_ERROR = (
    "No text could be extracted from the PDF. This may be a scanned or image-only PDF."
)


@dataclass
class _DocumentRecord:
    id: str
    filename: str
    status: str
    uploaded_at: datetime
    file_path: str
    owner_id: str
    chunk_count: int = 0
    error: str | None = None


_documents: dict[str, _DocumentRecord] = {}


def _to_response(rec: _DocumentRecord) -> DocumentResponse:
    return DocumentResponse(
        id=rec.id,
        filename=rec.filename,
        status=rec.status,
        uploaded_at=rec.uploaded_at,
        chunk_count=rec.chunk_count,
        error=rec.error,
    )


def get_owned_document(doc_id: str, owner_id: str) -> _DocumentRecord:
    rec = _documents.get(doc_id)
    if rec is None or rec.owner_id != owner_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return rec


async def run_pipeline(doc_id: str) -> None:
    rec = _documents.get(doc_id)
    if rec is None or not os.path.exists(rec.file_path):
        return

    try:
        rec.status = "processing"
        text = extract_text(rec.file_path)
        if not text.strip():
            raise ValueError(NO_TEXT_ERROR)
        chunks = chunk_text(text)
        rec.chunk_count = len(chunks)

        rec.status = "embedding"
        await embed_doc(doc_id, chunks)

        rec.status = "embedded"
        rec.error = None
    except Exception as exc:
        if _documents.get(doc_id) is rec:
            rec.status = "failed"
            rec.error = str(exc)


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    owner_id: str = Depends(get_client_id),
) -> DocumentResponse:
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
        owner_id=owner_id,
    )
    _documents[doc_id] = rec
    background_tasks.add_task(run_pipeline, doc_id)
    return _to_response(rec)


@router.get("")
async def list_documents(
    owner_id: str = Depends(get_client_id),
) -> DocumentListResponse:
    return DocumentListResponse(
        documents=[
            _to_response(rec)
            for rec in _documents.values()
            if rec.owner_id == owner_id
        ]
    )


@router.post("/{doc_id}/retry")
async def retry_document(
    doc_id: str,
    background_tasks: BackgroundTasks,
    owner_id: str = Depends(get_client_id),
) -> DocumentResponse:
    rec = get_owned_document(doc_id, owner_id)

    if rec.status != "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Document status is '{rec.status}', expected 'failed'",
        )
    if not os.path.exists(rec.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    rec.status = "uploaded"
    rec.error = None
    background_tasks.add_task(run_pipeline, doc_id)
    return _to_response(rec)


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str, owner_id: str = Depends(get_client_id)
) -> dict[str, str]:
    rec = get_owned_document(doc_id, owner_id)
    _documents.pop(doc_id)

    try:
        delete_collection(doc_id)
    except Exception:
        pass

    try:
        if os.path.exists(rec.file_path):
            os.remove(rec.file_path)
    except Exception as exc:
        _documents[doc_id] = rec
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {exc}") from exc

    try:
        delete_document_history(doc_id)
    except Exception:
        pass

    return {"status": "deleted"}
