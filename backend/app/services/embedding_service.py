from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings
from app.services.vector_service import add_embeddings

_document_embeddings_model: GoogleGenerativeAIEmbeddings | None = None
_query_embeddings_model: GoogleGenerativeAIEmbeddings | None = None


def _get_document_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    global _document_embeddings_model
    if _document_embeddings_model is None:
        _document_embeddings_model = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        )
    return _document_embeddings_model


def _get_query_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    global _query_embeddings_model
    if _query_embeddings_model is None:
        _query_embeddings_model = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768,
        )
    return _query_embeddings_model


async def embed_document(document_id: str, chunks: list[str]) -> int:
    vectors = await _get_document_embeddings_model().aembed_documents(chunks)

    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "chunk_index": i, "text": chunks[i]}
        for i in range(len(chunks))
    ]

    add_embeddings(
        collection_name=document_id,
        ids=ids,
        embeddings=vectors,
        metadatas=metadatas,
    )

    return len(chunks)


async def embed_query(text: str) -> list[float]:
    return await _get_query_embeddings_model().aembed_query(text)
