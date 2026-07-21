from langchain_huggingface import HuggingFaceEmbeddings

from app.services.vector_service import add_embeddings

_embeddings_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
)


async def embed_document(document_id: str, chunks: list[str]) -> int:
    vectors = await _embeddings_model.aembed_documents(chunks)

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
    return await _embeddings_model.aembed_query(text)
