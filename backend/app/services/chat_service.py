from langchain_ollama import ChatOllama

from app.services.embedding_service import embed_query
from app.services.vector_service import similarity_search

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based on the provided context. "
    "If the context does not contain enough information to answer the question, "
    "say so honestly. Do not make up information."
)

_llm = ChatOllama(
    model="llama3.2",
    temperature=0,
    streaming=True,
)


async def retrieve_context(document_id: str, question: str, k: int = 5) -> list[str]:
    vector = await embed_query(question)
    results = similarity_search(
        collection_name=document_id, query_embedding=vector, k=k
    )
    return [r.get("text", "") for r in results if r.get("text")]


async def generate_stream(question: str, context_chunks: list[str]):
    context = "\n\n".join(context_chunks)
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"),
    ]

    async for chunk in _llm.astream(messages):
        content = chunk.content
        if content:
            yield content
