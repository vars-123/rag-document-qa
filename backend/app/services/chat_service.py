"""Generate LLM responses with retrieved context."""


def generate_streaming_response(
    question: str, context_chunks: list[str], session_id: str | None = None
):
    """Stream a response from OpenAI using retrieved context."""
    ...
