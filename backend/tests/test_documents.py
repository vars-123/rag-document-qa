import io

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.routers.documents import _documents


@pytest.fixture(autouse=True)
def clear_store() -> None:
    _documents.clear()


@pytest.mark.asyncio
async def test_upload_pdf() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        file_content = b"%PDF-1.4 mock pdf content"
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
        )
    assert response.status_code == 201
    data = response.json()
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
        file_content = b"%PDF-1.4 mock"
        await client.post(
            "/api/documents/upload",
            files={"file": ("a.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        await client.post(
            "/api/documents/upload",
            files={"file": ("b.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        response = await client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 2
