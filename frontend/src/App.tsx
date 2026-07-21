import { useEffect, useState } from 'react'
import { DocumentList } from './components/DocumentList'
import { UploadZone } from './components/UploadZone'
import { useDocuments } from './hooks/useDocuments'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking...')
  const { documents, loading, error, upload, delete: deleteDoc } = useDocuments()

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
      {!loading && <DocumentList documents={documents} onDelete={deleteDoc} />}
    </main>
  )
}

export default App
