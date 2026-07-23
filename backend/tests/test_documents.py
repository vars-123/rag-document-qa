import io
import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.routers.documents import UPLOAD_DIR, _documents

CLIENT_A = {"X-Client-Id": "test-client-aaaa"}
CLIENT_B = {"X-Client-Id": "test-client-bbbb"}


@pytest.fixture(autouse=True)
def clear_store() -> None:
    _documents.clear()


async def _upload_pdf(
    client: AsyncClient,
    content: bytes = b"%PDF-1.4 mock",
    filename: str = "test.pdf",
) -> dict:
    with patch(
        "app.routers.documents.run_pipeline", new=AsyncMock(return_value=None)
    ):
        response = await client.post(
            "/api/documents/upload",
            files={"file": (filename, io.BytesIO(content), "application/pdf")},
        )
    assert response.status_code == 201
    return response.json()


async def _upload_and_embed(client: AsyncClient, filename: str = "test.pdf") -> dict:
    with (
        patch(
            "app.routers.documents.extract_text",
            return_value="Chunk one. Chunk two.",
        ),
        patch(
            "app.routers.documents.chunk_text",
            return_value=["Chunk one.", "Chunk two."],
        ),
        patch("app.routers.documents.embed_doc", new=AsyncMock(return_value=2)),
    ):
        response = await client.post(
            "/api/documents/upload",
            files={"file": (filename, io.BytesIO(b"%PDF-1.4 mock"), "application/pdf")},
        )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_upload_pdf() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        data = await _upload_pdf(client)
    assert data["filename"] == "test.pdf"
    assert data["status"] == "uploaded"
    assert data["error"] is None
    assert "id" in data
    assert "uploaded_at" in data


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_rejects_large_file() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        large = b"x" * (10 * 1024 * 1024 + 1)
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("large.pdf", io.BytesIO(large), "application/pdf")},
        )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_auto_pipeline_reaches_embedded() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        doc = await _upload_and_embed(client)
        response = await client.get("/api/documents")

    documents = response.json()["documents"]
    assert documents[0]["id"] == doc["id"]
    assert documents[0]["status"] == "embedded"
    assert documents[0]["chunk_count"] == 2
    assert documents[0]["error"] is None


@pytest.mark.asyncio
async def test_pipeline_failure_marks_document_failed() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        with patch("app.routers.documents.extract_text", return_value="   "):
            response = await client.post(
                "/api/documents/upload",
                files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 mock"), "application/pdf")},
            )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        list_response = await client.get("/api/documents")

    document = list_response.json()["documents"][0]
    assert document["id"] == doc_id
    assert document["status"] == "failed"
    assert "No text" in document["error"]


@pytest.mark.asyncio
async def test_list_documents() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        await _upload_pdf(client, filename="a.pdf")
        await _upload_pdf(client, filename="b.pdf")
        response = await client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 2


@pytest.mark.asyncio
async def test_retry_failed_document() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        with patch("app.routers.documents.extract_text", return_value="   "):
            response = await client.post(
                "/api/documents/upload",
                files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 mock"), "application/pdf")},
            )
        doc_id = response.json()["id"]

        with (
            patch("app.routers.documents.extract_text", return_value="Some text."),
            patch("app.routers.documents.chunk_text", return_value=["Some text."]),
            patch("app.routers.documents.embed_doc", new=AsyncMock(return_value=1)),
        ):
            retry_response = await client.post(f"/api/documents/{doc_id}/retry")

        assert retry_response.status_code == 200
        list_response = await client.get("/api/documents")

    document = list_response.json()["documents"][0]
    assert document["status"] == "embedded"
    assert document["error"] is None


@pytest.mark.asyncio
async def test_retry_rejects_non_failed_document() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        doc = await _upload_pdf(client)
        response = await client.post(f"/api/documents/{doc['id']}/retry")

    assert response.status_code == 400
    assert "failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_retry_document_not_found() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        response = await client.post("/api/documents/nonexistent/retry")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_success() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        doc = await _upload_pdf(client)
        file_path = os.path.join(UPLOAD_DIR, f"{doc['id']}.pdf")

        with (
            patch("app.routers.documents.delete_collection", return_value=None),
            patch("app.routers.documents.delete_document_history", return_value=None),
        ):
            response = await client.delete(f"/api/documents/{doc['id']}")

        list_response = await client.get("/api/documents")

    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}
    assert not os.path.exists(file_path)
    assert list_response.json()["documents"] == []
    assert doc["id"] not in _documents


@pytest.mark.asyncio
async def test_delete_document_not_found() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client:
        response = await client.delete("/api/documents/nonexistent")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_documents_isolated_per_client() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client_a:
        await _upload_pdf(client_a, filename="a.pdf")
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_B) as client_b:
        response = await client_b.get("/api/documents")

    assert response.status_code == 200
    assert response.json()["documents"] == []


@pytest.mark.asyncio
async def test_retry_document_not_owner_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client_a:
        doc = await _upload_pdf(client_a)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_B) as client_b:
        response = await client_b.post(f"/api/documents/{doc['id']}/retry")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_not_owner_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_A) as client_a:
        doc = await _upload_pdf(client_a)
    async with AsyncClient(transport=transport, base_url="http://test", headers=CLIENT_B) as client_b:
        response = await client_b.delete(f"/api/documents/{doc['id']}")

    assert response.status_code == 404
    assert doc["id"] in _documents


@pytest.mark.asyncio
async def test_missing_client_id_header_rejected() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/documents")

    assert response.status_code == 422
