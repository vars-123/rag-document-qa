import type { DocumentResponse } from '../types/document'
import type { ChatRequest, ChatMessage } from '../types/chat'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')
const BASE = API_BASE_URL

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json()
    return body.detail || res.statusText
  } catch {
    return res.statusText
  }
}

export async function fetchDocuments(): Promise<DocumentResponse[]> {
  const res = await fetch(`${BASE}/documents`)
  if (!res.ok) throw new Error(await parseError(res))
  const data = await res.json()
  return data.documents
}

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function processDocument(id: string): Promise<DocumentResponse> {
  const res = await fetch(`${BASE}/documents/${id}/process`, { method: 'POST' })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function embedDocument(id: string): Promise<DocumentResponse> {
  const res = await fetch(`${BASE}/documents/${id}/embed`, { method: 'POST' })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await parseError(res))
}

export async function sendChatMessage(
  body: ChatRequest,
  onChunk: (text: string) => void,
): Promise<void> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error('Chat request failed')

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
  const res = await fetch(`${BASE}/chat/history?session_id=${sessionId}`)
  if (!res.ok) throw new Error('Failed to fetch history')
  const data = await res.json()
  return data.messages
}
