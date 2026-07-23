import { useCallback, useEffect, useRef, useState } from 'react'
import type { DocumentResponse } from '../types/document'
import { fetchDocuments, uploadDocument, retryDocument, deleteDocument } from '../services/api'

const POLL_INTERVAL_MS = 2000
const NON_TERMINAL_STATUSES = new Set(['uploaded', 'processing', 'processed', 'embedding'])

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeOps, setActiveOps] = useState<Set<string>>(new Set())
  const errorTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const setErrorAutoClear = useCallback((msg: string) => {
    setError(msg)
    if (errorTimerRef.current) clearTimeout(errorTimerRef.current)
    errorTimerRef.current = setTimeout(() => setError(null), 8000)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
    if (errorTimerRef.current) clearTimeout(errorTimerRef.current)
  }, [])

  const load = useCallback(async () => {
    try {
      const docs = await fetchDocuments()
      setDocuments(docs)
      return docs
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load documents'
      setErrorAutoClear(msg)
      return []
    } finally {
      setLoading(false)
    }
  }, [setErrorAutoClear])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    if (!documents.some((doc) => NON_TERMINAL_STATUSES.has(doc.status))) return
    const timer = setTimeout(load, POLL_INTERVAL_MS)
    return () => clearTimeout(timer)
  }, [documents, load])

  const runOp = useCallback(
    async (id: string, op: () => Promise<unknown>, opName: string) => {
      setActiveOps((prev) => new Set(prev).add(id))
      setError(null)
      if (errorTimerRef.current) clearTimeout(errorTimerRef.current)
      try {
        await op()
        await load()
      } catch (err) {
        const msg = err instanceof Error ? err.message : `${opName} failed`
        setErrorAutoClear(msg)
      } finally {
        setActiveOps((prev) => {
          const next = new Set(prev)
          next.delete(id)
          return next
        })
      }
    },
    [load, setErrorAutoClear],
  )

  const upload = useCallback(
    async (file: File) => {
      try {
        await uploadDocument(file)
        await load()
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Upload failed'
        setErrorAutoClear(msg)
      }
    },
    [load, setErrorAutoClear],
  )

  const retry = useCallback(
    (id: string) => runOp(id, () => retryDocument(id), 'Retry'),
    [runOp],
  )

  const delete_ = useCallback(
    (id: string) => runOp(id, () => deleteDocument(id), 'Delete'),
    [runOp],
  )

  return { documents, loading, error, clearError, activeOps, upload, retry, delete: delete_ }
}
