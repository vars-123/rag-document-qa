from pydantic import BaseModel


class ChatRequest(BaseModel):
    document_id: str
    question: str
    session_id: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]


class ConversationSummary(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]
