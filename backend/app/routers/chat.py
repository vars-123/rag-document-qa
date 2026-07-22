import inspect
import uuid

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.models.chat import ChatHistoryResponse, ChatRequest
from app.routers.documents import _documents
from app.services.chat_history_service import add_message, ensure_session, get_messages
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

    session_id = body.session_id or str(uuid.uuid4())
    try:
        ensure_session(session_id, body.document_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    add_message(session_id, "user", body.question)

    async def stream_answer():
        answer_parts: list[str] = []
        try:
            stream = generate_stream(body.question, context_chunks)
            if inspect.isasyncgen(stream) or hasattr(stream, "__aiter__"):
                async for chunk in stream:
                    answer_parts.append(chunk)
                    yield chunk
            else:
                for chunk in stream:
                    answer_parts.append(chunk)
                    yield chunk
        except Exception:
            raise
        else:
            add_message(session_id, "assistant", "".join(answer_parts))

    return StreamingResponse(
        stream_answer(),
        media_type="text/event-stream",
        headers={"X-Chat-Session-Id": session_id},
    )


@router.get("/history")
async def chat_history(session_id: str = Query(..., min_length=1)) -> ChatHistoryResponse:
    messages = get_messages(session_id)
    return ChatHistoryResponse(session_id=session_id, messages=messages)
