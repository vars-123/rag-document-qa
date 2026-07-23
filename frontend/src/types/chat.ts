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

export interface ConversationSummary {
  session_id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}
