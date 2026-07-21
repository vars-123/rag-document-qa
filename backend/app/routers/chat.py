from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest
from app.routers.documents import _documents
from app.services.chat_service import generate_stream, retrieve_context

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(body: ChatRequest):
    rec = _documents.get(body.document_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Document not found")
    if rec.status != "embedded":
        raise HTTPException(
            status_code=400,
            detail=f"Document status is '{rec.status}', expected 'embedded'",
        )

    context_chunks = await retrieve_context(body.document_id, body.question)

    if not context_chunks:
        raise HTTPException(
            status_code=400,
            detail="No relevant context found for the question",
        )

    return StreamingResponse(
        generate_stream(body.question, context_chunks),
        media_type="text/event-stream",
    )
