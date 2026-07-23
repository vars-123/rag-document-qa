import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.routers.documents import _documents
from app.services.chat_history_service import clear_chat_history

CLIENT_A = {"X-Client-Id": "test-client-aaaa"}
CLIENT_B = {"X-Client-Id": "test-client-bbbb"}


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
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
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
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        response = await client.post(
            "/api/chat",
            json={"document_id": "nonexistent", "question": "test"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_not_embedded() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
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
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
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
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        doc = await _upload_and_embed(client)
        response = await client.post(
            "/api/chat",
            json={"document_id": doc["id"]},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_not_owner_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client_a:
        doc = await _upload_and_embed(client_a)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_B) as client_b:
        response = await client_b.post(
            "/api/chat",
            json={"document_id": doc["id"], "question": "test"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_history_isolated_per_client() -> None:
    transport = ASGITransport(app=app)
    session_id = "session-isolation"
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client_a:
        doc = await _upload_and_embed(client_a)
        with (
            patch("app.routers.chat.retrieve_context", return_value=["Some context."]),
            patch("app.routers.chat.generate_stream", return_value=iter(["Hi"])),
        ):
            response = await client_a.post(
                "/api/chat",
                json={
                    "document_id": doc["id"],
                    "question": "test query",
                    "session_id": session_id,
                },
            )
        assert response.status_code == 200

        history_a = await client_a.get(f"/api/chat/history?session_id={session_id}")
        assert len(history_a.json()["messages"]) == 2

    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_B) as client_b:
        history_b = await client_b.get(f"/api/chat/history?session_id={session_id}")
        assert history_b.status_code == 200
        assert history_b.json()["messages"] == []

        response = await client_b.post(
            "/api/chat",
            json={
                "document_id": doc["id"],
                "question": "test",
                "session_id": session_id,
            },
        )
        assert response.status_code == 404


def test_extract_text_handles_content_blocks() -> None:
    from app.services.chat_service import _extract_text

    assert _extract_text("hi") == "hi"
    assert (
        _extract_text(
            [
                {"type": "thinking", "thinking": "reasoning..."},
                {"type": "text", "text": "Hello"},
            ]
        )
        == "Hello"
    )
    assert _extract_text([{"type": "text", "text": "a"}, "b"]) == "ab"
    assert _extract_text(None) == ""
