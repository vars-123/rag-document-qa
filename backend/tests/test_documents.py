import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.routers.documents import _documents


@pytest.fixture(autouse=True)
def clear_store() -> None:
    _documents.clear()


async def _upload_pdf(
    client: AsyncClient,
    content: bytes = b"%PDF-1.4 mock",
    filename: str = "test.pdf",
) -> dict:
    response = await client.post(
        "/api/documents/upload",
        files={"file": (filename, io.BytesIO(content), "application/pdf")},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_upload_pdf() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = await _upload_pdf(client)
    assert data["filename"] == "test.pdf"
    assert data["status"] == "uploaded"
    assert "id" in data
    assert "uploaded_at" in data


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_rejects_large_file() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        large = b"x" * (10 * 1024 * 1024 + 1)
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("large.pdf", io.BytesIO(large), "application/pdf")},
        )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_documents() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _upload_pdf(client, filename="a.pdf")
        await _upload_pdf(client, filename="b.pdf")
        response = await client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 2


@pytest.mark.asyncio
async def test_process_document_success() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc = await _upload_pdf(client)

        with (
            patch("app.routers.documents.extract_text", return_value="Chunk one. Chunk two. Chunk three."),
            patch("app.routers.documents.chunk_text", return_value=["Chunk one.", "Chunk two.", "Chunk three."]),
        ):
            response = await client.post(f"/api/documents/{doc['id']}/process")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["chunk_count"] == 3


@pytest.mark.asyncio
async def test_process_document_not_found() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/documents/nonexistent/process")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_process_document_already_processed() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc = await _upload_pdf(client)

        with (
            patch("app.routers.documents.extract_text", return_value="Some text"),
            patch("app.routers.documents.chunk_text", return_value=["Some text"]),
        ):
            await client.post(f"/api/documents/{doc['id']}/process")
            response = await client.post(f"/api/documents/{doc['id']}/process")

    assert response.status_code == 400
    assert "processed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_process_document_no_text() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc = await _upload_pdf(client)

        with patch("app.routers.documents.extract_text", return_value="   "):
            response = await client.post(f"/api/documents/{doc['id']}/process")

    assert response.status_code == 400
    assert "No text" in response.json()["detail"]
