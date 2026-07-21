import { useCallback, useState } from 'react'
import type { ChatMessage } from '../types/chat'
import { sendChatMessage } from '../services/api'

export function useChat(documentId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const send = useCallback(
    async (question: string) => {
      if (!documentId || !question.trim()) return

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
          { document_id: documentId, question },
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
    [documentId],
  )

  const clear = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, streaming, error, send, clear }
}
