"""Split extracted text into overlapping chunks."""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into chunks using LangChain's RecursiveCharacterTextSplitter."""
    ...
