import type { DocumentResponse } from '../types/document'
import type { ChatRequest, ChatMessage, ConversationSummary } from '../types/chat'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')
const BASE = API_BASE_URL

const CLIENT_ID_KEY = 'rag-document-qa:client-id'

export function getClientId(): string {
  let id = globalThis.localStorage.getItem(CLIENT_ID_KEY)
  if (!id) {
    id = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`
    globalThis.localStorage.setItem(CLIENT_ID_KEY, id)
  }
  return id
}

function clientHeaders(extra?: Record<string, string>): Record<string, string> {
  return { 'X-Client-Id': getClientId(), ...extra }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json()
    return body.detail || res.statusText
  } catch {
    return res.statusText
  }
}

export async function fetchDocuments(): Promise<DocumentResponse[]> {
  const res = await fetch(`${BASE}/documents`, { headers: clientHeaders() })
  if (!res.ok) throw new Error(await parseError(res))
  const data = await res.json()
  return data.documents
}

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', headers: clientHeaders(), body: form })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function processDocument(id: string): Promise<DocumentResponse> {
  const res = await fetch(`${BASE}/documents/${id}/process`, { method: 'POST', headers: clientHeaders() })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function embedDocument(id: string): Promise<DocumentResponse> {
  const res = await fetch(`${BASE}/documents/${id}/embed`, { method: 'POST', headers: clientHeaders() })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${id}`, { method: 'DELETE', headers: clientHeaders() })
  if (!res.ok) throw new Error(await parseError(res))
}

export async function sendChatMessage(
  body: ChatRequest,
  onChunk: (text: string) => void,
): Promise<void> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: clientHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await parseError(res))

  const reader = res.body?.getReader()
  if (!reader) return
  const decoder = new TextDecoder()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    onChunk(decoder.decode(value, { stream: true }))
  }
}

export async function fetchChatHistory(
  sessionId: string,
): Promise<ChatMessage[]> {
  const res = await fetch(`${BASE}/chat/history?session_id=${sessionId}`, { headers: clientHeaders() })
  if (!res.ok) throw new Error('Failed to fetch history')
  const data = await res.json()
  return data.messages
}

export async function fetchConversations(
  documentId: string,
): Promise<ConversationSummary[]> {
  const res = await fetch(`${BASE}/chat/conversations?document_id=${documentId}`, { headers: clientHeaders() })
  if (!res.ok) throw new Error(await parseError(res))
  const data = await res.json()
  return data.conversations
}
