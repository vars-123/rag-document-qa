"""Generate and store embeddings using OpenAI."""


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of text chunks."""
    ...


def embed_document(document_id: str, chunks: list[str]) -> int:
    """Generate embeddings and store them in ChromaDB. Returns chunk count."""
    ...
