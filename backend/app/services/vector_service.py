"""ChromaDB operations for storing and retrieving vectors."""


def similarity_search(collection_name: str, query: str, k: int = 5) -> list[dict]:
    """Search for the top-k most similar chunks to a query."""
    ...


def delete_collection(collection_name: str) -> None:
    """Delete a document's vector collection."""
    ...
