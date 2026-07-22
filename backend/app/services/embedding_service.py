from langchain_huggingface import HuggingFaceEmbeddings

from app.services.vector_service import add_embeddings

_embeddings_model: HuggingFaceEmbeddings | None = None


def _get_embeddings_model() -> HuggingFaceEmbeddings:
    global _embeddings_model
    if _embeddings_model is None:
        _embeddings_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
        )
    return _embeddings_model


async def embed_document(document_id: str, chunks: list[str]) -> int:
    vectors = await _get_embeddings_model().aembed_documents(chunks)

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
    return await _get_embeddings_model().aembed_query(text)
