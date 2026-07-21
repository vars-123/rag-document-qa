import chromadb

from app.config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_db_path)
    return _client


def get_collection(name: str):
    return _get_client().get_or_create_collection(name)


def add_embeddings(
    collection_name: str,
    ids: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict] | None = None,
) -> None:
    collection = get_collection(collection_name)
    collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)


def similarity_search(
    collection_name: str,
    query_embedding: list[float],
    k: int = 5,
) -> list[dict]:
    collection = get_collection(collection_name)
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    output: list[dict] = []
    if results["ids"] and results["metadatas"]:
        for i, doc_id in enumerate(results["ids"][0]):
            meta = (results["metadatas"][0] or [{}])[i] or {}
            output.append({"id": doc_id, **meta})
    return output


def delete_collection(collection_name: str) -> None:
    _get_client().delete_collection(collection_name)
