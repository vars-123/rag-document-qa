import { useCallback, useEffect, useMemo, useState } from 'react'
import { ChatInterface } from './components/ChatInterface'
import { DocumentList } from './components/DocumentList'
import { UploadZone } from './components/UploadZone'
import { useDocuments } from './hooks/useDocuments'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking...')
  const { documents, loading, error, upload, process, embed, delete: deleteDoc } = useDocuments()
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)

  const selectedDoc = useMemo(
    () => documents.find((d) => d.id === selectedDocId) ?? null,
    [documents, selectedDocId],
  )

  const handleSelect = useCallback((id: string) => {
    setSelectedDocId((prev) => (prev === id ? null : id))
  }, [])

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setBackendStatus(data.status))
      .catch(() => setBackendStatus('unreachable'))
  }, [])

  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', maxWidth: 640, margin: '0 auto' }}>
      <h1>RAG Document QA</h1>
      <p>Backend status: <strong>{backendStatus}</strong></p>

      <hr />

      <h2>Upload PDF</h2>
      <UploadZone onUpload={upload} />

      <hr />

      <h2>Documents</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && (
        <DocumentList
          documents={documents}
          onDelete={deleteDoc}
          onProcess={process}
          onEmbed={embed}
          onSelect={handleSelect}
          selectedId={selectedDocId}
        />
      )}

      {selectedDoc && (
        <>
          <hr />
          <h2>Ask a Question</h2>
          <ChatInterface documentId={selectedDoc.id} documentName={selectedDoc.filename} />
        </>
      )}
    </main>
  )
}

export default App
