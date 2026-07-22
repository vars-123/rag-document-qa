import { useCallback, useEffect, useMemo, useState } from 'react'
import { ChatInterface } from './components/ChatInterface'
import { DocumentList } from './components/DocumentList'
import { UploadZone } from './components/UploadZone'
import { useDocuments } from './hooks/useDocuments'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking...')
  const { documents, loading, error, clearError, activeOps, upload, process, embed, delete: deleteDoc } = useDocuments()
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

  const backendTone =
    backendStatus === 'ok' ? 'status-ok' : backendStatus === 'checking...' ? 'status-neutral' : 'status-bad'

  return (
    <main className="app-shell">
      <div className="app">
        <header className="hero">
          <div className="eyebrow">RAG PDF Question Answering</div>
          <h1>Ask grounded questions over your PDFs.</h1>
          <p>
            Upload a file, process it into chunks, embed the content, and keep the chat anchored to the selected
            document.
          </p>
          <div className="hero-stats">
            <span className={`status-pill ${backendTone}`}>Backend {backendStatus}</span>
            <span className="status-pill">Documents {documents.length}</span>
            <span className="status-pill">Selected {selectedDoc ? selectedDoc.filename : 'none'}</span>
          </div>
        </header>

        {error && (
          <div className="banner" role="alert">
            <div>
              <strong>Document action failed</strong>
              <div>{error}</div>
            </div>
            <button type="button" onClick={clearError} aria-label="Dismiss error">
              ×
            </button>
          </div>
        )}

        <section className="workspace">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Upload and manage documents</h2>
                <p className="panel-subtitle">Move each PDF through upload, processing, embedding, and chat.</p>
              </div>
            </div>
            <UploadZone onUpload={upload} />
            <div>
              <div className="panel-header" style={{ marginBottom: 12 }}>
                <div>
                  <h2 className="panel-title">Documents</h2>
                  <p className="panel-subtitle">
                    {loading ? 'Loading document list...' : `${documents.length} document${documents.length === 1 ? '' : 's'} available`}
                  </p>
                </div>
              </div>
              {loading ? (
                <div className="empty-state">Loading documents...</div>
              ) : (
                <DocumentList
                  documents={documents}
                  onDelete={deleteDoc}
                  onProcess={process}
                  onEmbed={embed}
                  onSelect={handleSelect}
                  selectedId={selectedDocId}
                  activeOps={activeOps}
                />
              )}
            </div>
          </div>

          <div className="panel chat-panel">
            {selectedDoc ? (
              <ChatInterface documentId={selectedDoc.id} documentName={selectedDoc.filename} />
            ) : (
              <div className="empty-state">
                <h2 className="panel-title" style={{ marginBottom: 8 }}>
                  Select a document to chat
                </h2>
                <p style={{ margin: 0 }}>
                  Only embedded documents can answer questions. Pick one from the list to open its conversation.
                </p>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
