import { useCallback, useEffect, useState } from 'react'
import type { DocumentResponse } from '../types/document'
import { fetchDocuments, uploadDocument, processDocument, embedDocument, deleteDocument } from '../services/api'

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const docs = await fetchDocuments()
      setDocuments(docs)
      setError(null)
    } catch {
      setError('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const upload = useCallback(
    async (file: File) => {
      try {
        await uploadDocument(file)
        await load()
      } catch {
        setError('Upload failed')
      }
    },
    [load],
  )

  const process = useCallback(
    async (id: string) => {
      try {
        await processDocument(id)
        await load()
      } catch {
        setError('Process failed')
      }
    },
    [load],
  )

  const embed = useCallback(
    async (id: string) => {
      try {
        await embedDocument(id)
        await load()
      } catch {
        setError('Embed failed')
      }
    },
    [load],
  )

  const delete_ = useCallback(
    async (id: string) => {
      try {
        await deleteDocument(id)
        await load()
      } catch {
        setError('Delete failed')
      }
    },
    [load],
  )

  return { documents, loading, error, upload, process, embed, delete: delete_ }
}
