import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.routers.documents import _documents
from app.services.chat_history_service import clear_chat_history


@pytest.fixture(autouse=True)
def clear_store() -> None:
    _documents.clear()
    clear_chat_history()


async def _upload_and_embed(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 mock"), "application/pdf")},
    )
    assert response.status_code == 201
    doc = response.json()

    with (
        patch("app.routers.documents.extract_text", return_value="Some context."),
        patch("app.routers.documents.chunk_text", return_value=["Some context."]),
        patch("app.routers.documents.embed_doc", return_value=1),
    ):
        await client.post(f"/api/documents/{doc['id']}/process")
        resp = await client.post(f"/api/documents/{doc['id']}/embed")
    assert resp.status_code == 200
    return resp.json()


@pytest.mark.asyncio
async def test_chat_streams_response() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc = await _upload_and_embed(client)
        session_id = "session-123"

        with (
            patch("app.routers.chat.retrieve_context", return_value=["Some context."]),
            patch(
                "app.routers.chat.generate_stream",
                return_value=iter(["Hello", " ", "world"]),
            ),
        ):
            response = await client.post(
                "/api/chat",
                json={
                    "document_id": doc["id"],
                    "question": "test query",
                    "session_id": session_id,
                },
            )
        assert response.status_code == 200
        assert response.text == "Hello world"
        assert response.headers["x-chat-session-id"] == session_id

        history_response = await client.get(f"/api/chat/history?session_id={session_id}")
        assert history_response.status_code == 200
        history = history_response.json()
        assert history["session_id"] == session_id
        assert [message["role"] for message in history["messages"]] == [
            "user",
            "assistant",
        ]
        assert history["messages"][0]["content"] == "test query"
        assert history["messages"][1]["content"] == "Hello world"


@pytest.mark.asyncio
async def test_chat_document_not_found() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={"document_id": "nonexistent", "question": "test"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_not_embedded() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
        )
        doc = response.json()
        response = await client.post(
            "/api/chat",
            json={"document_id": doc["id"], "question": "test"},
        )
    assert response.status_code == 400
    assert "uploaded" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_no_context() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc = await _upload_and_embed(client)

        with patch("app.routers.chat.retrieve_context", return_value=[]):
            response = await client.post(
                "/api/chat",
                json={"document_id": doc["id"], "question": "test"},
            )

    assert response.status_code == 400
    assert "No relevant context" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_missing_question() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc = await _upload_and_embed(client)
        response = await client.post(
            "/api/chat",
            json={"document_id": doc["id"]},
        )
    assert response.status_code == 422
