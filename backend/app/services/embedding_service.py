from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.services.vector_service import add_embeddings


async def embed_document(document_id: str, chunks: list[str]) -> int:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    embeddings_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key,
    )

    vectors = await embeddings_model.aembed_documents(chunks)

    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "chunk_index": i} for i in range(len(chunks))
    ]

    add_embeddings(
        collection_name=document_id,
        ids=ids,
        embeddings=vectors,
        metadatas=metadatas,
    )

    return len(chunks)
