export interface ChatRequest {
  document_id: string
  question: string
  session_id?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}
