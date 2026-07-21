from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.services.embedding_service import embed_query
from app.services.vector_service import similarity_search

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based on the provided context. "
    "If the context does not contain enough information to answer the question, "
    "say so honestly. Do not make up information."
)


async def retrieve_context(document_id: str, question: str, k: int = 5) -> list[str]:
    vector = await embed_query(question)
    results = similarity_search(
        collection_name=document_id, query_embedding=vector, k=k
    )
    return [r.get("text", "") for r in results if r.get("text")]


async def generate_stream(question: str, context_chunks: list[str]):
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    context = "\n\n".join(context_chunks)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
        ),
    ]

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        streaming=True,
        openai_api_key=settings.openai_api_key,
    )

    async for chunk in llm.astream(messages):
        content = chunk.content
        if content:
            yield content
