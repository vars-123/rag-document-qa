import type { DocumentResponse } from '../types/document'

interface DocumentListProps {
  documents: DocumentResponse[]
  onDelete: (id: string) => void
  onProcess: (id: string) => void
  onEmbed: (id: string) => void
  onSelect?: (id: string) => void
  selectedId?: string | null
  activeOps: ReadonlySet<string>
}

function formatTimestamp(value: string) {
  return new Date(value).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function statusClass(status: string) {
  return `status-badge status-${status}`
}

export function DocumentList({
  documents,
  onDelete,
  onProcess,
  onEmbed,
  onSelect,
  selectedId,
  activeOps,
}: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <h3 className="panel-title" style={{ marginBottom: 8 }}>
          No documents yet
        </h3>
        <p style={{ margin: 0 }}>
          Upload a PDF to create the first document. It will appear here with processing and embedding actions.
        </p>
      </div>
    )
  }

  return (
    <ul className="document-list">
      {documents.map((doc) => {
        const busy = activeOps.has(doc.id)
        const selected = selectedId === doc.id

        return (
          <li key={doc.id} className={`document-card${selected ? ' is-selected' : ''}`}>
            <div className="document-header">
              <div>
                <h3 className="document-title">{doc.filename}</h3>
                <div className="document-meta">
                  <span>{formatTimestamp(doc.uploaded_at)}</span>
                  {doc.chunk_count > 0 && <span>{doc.chunk_count} chunks</span>}
                </div>
              </div>
              <span className={statusClass(doc.status)}>{doc.status}</span>
            </div>

            <div className="document-actions">
              {doc.status === 'uploaded' && (
                <button className="secondary-button" onClick={() => onProcess(doc.id)} disabled={busy}>
                  {busy ? 'Processing…' : 'Process'}
                </button>
              )}
              {doc.status === 'processed' && (
                <button className="secondary-button" onClick={() => onEmbed(doc.id)} disabled={busy}>
                  {busy ? 'Embedding…' : 'Embed'}
                </button>
              )}
              {doc.status === 'embedded' && onSelect && (
                <button className="primary-button" onClick={() => onSelect(doc.id)} disabled={busy}>
                  {selected ? 'Selected' : 'Open chat'}
                </button>
              )}
              <button className="ghost-button" onClick={() => onDelete(doc.id)} disabled={busy}>
                {busy ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
