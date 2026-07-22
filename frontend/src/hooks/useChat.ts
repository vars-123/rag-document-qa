import { useCallback, useEffect, useState } from 'react'
import type { ChatMessage } from '../types/chat'
import { fetchChatHistory, sendChatMessage } from '../services/api'

function createSessionId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function getSessionStorageKey(documentId: string) {
  return `rag-document-qa:chat-session:${documentId}`
}

export function useChat(documentId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loadingHistory, setLoadingHistory] = useState(false)

  useEffect(() => {
    if (!documentId) {
      setMessages([])
      setError(null)
      setSessionId(null)
      setLoadingHistory(false)
      return
    }

    const storageKey = getSessionStorageKey(documentId)
    const storedSessionId = globalThis.localStorage.getItem(storageKey) ?? createSessionId()
    globalThis.localStorage.setItem(storageKey, storedSessionId)

    let active = true
    setLoadingHistory(true)
    setError(null)
    setSessionId(storedSessionId)
    setMessages([])

    fetchChatHistory(storedSessionId)
      .then((history) => {
        if (active) {
          setMessages(history)
        }
      })
      .catch((err) => {
        if (!active) return
        const msg = err instanceof Error ? err.message : 'Failed to load chat history'
        setError(msg)
      })
      .finally(() => {
        if (active) {
          setLoadingHistory(false)
        }
      })

    return () => {
      active = false
    }
  }, [documentId])

  const send = useCallback(
    async (question: string) => {
      if (!documentId || !sessionId || !question.trim()) return

      setError(null)
      setStreaming(true)

      const userMsg: ChatMessage = {
        role: 'user',
        content: question,
        timestamp: new Date().toISOString(),
      }
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMsg, assistantMsg])

      try {
        await sendChatMessage(
          { document_id: documentId, question, session_id: sessionId },
          (chunk) => {
            setMessages((prev) => {
              const next = [...prev]
              const last = next[next.length - 1]
              if (last.role === 'assistant') {
                next[next.length - 1] = { ...last, content: last.content + chunk }
              }
              return next
            })
          },
        )
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Chat failed'
        setError(msg)
        setMessages((prev) => {
          const next = [...prev]
          const last = next[next.length - 1]
          if (last.role === 'assistant' && last.content === '') {
            return next.slice(0, -1)
          }
          return next
        })
      } finally {
        setStreaming(false)
      }
    },
    [documentId, sessionId],
  )

  const clear = useCallback(() => {
    if (!documentId) {
      setMessages([])
      setError(null)
      return
    }

    const nextSessionId = createSessionId()
    globalThis.localStorage.setItem(getSessionStorageKey(documentId), nextSessionId)
    setSessionId(nextSessionId)
    setMessages([])
    setError(null)
  }, [documentId])

  return { messages, streaming, error, send, clear, loadingHistory }
}
