import { useCallback, useEffect, useRef, useState } from 'react'
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
  const activationRef = useRef(0)

  const activateSession = useCallback((docId: string, nextSessionId: string) => {
    globalThis.localStorage.setItem(getSessionStorageKey(docId), nextSessionId)

    const activation = ++activationRef.current
    setLoadingHistory(true)
    setError(null)
    setSessionId(nextSessionId)
    setMessages([])

    fetchChatHistory(nextSessionId)
      .then((history) => {
        if (activationRef.current === activation) {
          setMessages(history)
        }
      })
      .catch((err) => {
        if (activationRef.current !== activation) return
        const msg = err instanceof Error ? err.message : 'Failed to load chat history'
        setError(msg)
      })
      .finally(() => {
        if (activationRef.current === activation) {
          setLoadingHistory(false)
        }
      })
  }, [])

  useEffect(() => {
    if (!documentId) {
      activationRef.current += 1
      setMessages([])
      setError(null)
      setSessionId(null)
      setLoadingHistory(false)
      return
    }

    const storedSessionId =
      globalThis.localStorage.getItem(getSessionStorageKey(documentId)) ?? createSessionId()
    activateSession(documentId, storedSessionId)
  }, [documentId, activateSession])

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

      let receivedAny = false
      try {
        await sendChatMessage(
          { document_id: documentId, question, session_id: sessionId },
          (chunk) => {
            if (chunk) receivedAny = true
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
        if (!receivedAny) {
          setError('The assistant returned an empty response. Please try again.')
          setMessages((prev) => {
            const last = prev[prev.length - 1]
            return last?.role === 'assistant' && last.content === ''
              ? prev.slice(0, -1)
              : prev
          })
        }
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

  const startNew = useCallback(() => {
    if (!documentId) {
      setMessages([])
      setError(null)
      return
    }
    activateSession(documentId, createSessionId())
  }, [documentId, activateSession])

  const switchSession = useCallback(
    (nextSessionId: string) => {
      if (!documentId || nextSessionId === sessionId) return
      activateSession(documentId, nextSessionId)
    },
    [documentId, sessionId, activateSession],
  )

  return { messages, streaming, error, send, startNew, switchSession, sessionId, loadingHistory }
}
