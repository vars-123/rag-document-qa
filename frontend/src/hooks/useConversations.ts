import { useCallback, useEffect, useState } from 'react'
import type { ConversationSummary } from '../types/chat'
import { fetchConversations } from '../services/api'

export function useConversations(documentId: string | null) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    if (!documentId) {
      setConversations([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await fetchConversations(documentId)
      setConversations(data)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load conversations'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [documentId])

  useEffect(() => {
    refresh()
  }, [refresh])

  return { conversations, loading, error, refresh }
}
