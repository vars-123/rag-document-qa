import type { DocumentResponse } from '../types/document'

interface DocumentListProps {
  documents: DocumentResponse[]
  onDelete: (id: string) => void
  onRetry: (id: string) => void
  onSelect?: (id: string) => void
  selectedId?: string | null
  activeOps: ReadonlySet<string>
}

const IN_PROGRESS_STATUSES = new Set(['uploaded', 'processing', 'processed', 'embedding'])

const STATUS_LABELS: Record<string, string> = {
  uploaded: 'Queued',
  processing: 'Processing…',
  processed: 'Processing…',
  embedding: 'Embedding…',
  embedded: 'Ready',
  failed: 'Failed',
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
  const inProgress = IN_PROGRESS_STATUSES.has(status) ? ' is-busy' : ''
  return `status-badge status-${status}${inProgress}`
}

export function DocumentList({
  documents,
  onDelete,
  onRetry,
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
          Upload a PDF and it will be prepared automatically. When it is ready, open the chat and start asking questions.
        </p>
      </div>
    )
  }

  return (
    <ul className="document-list">
      {documents.map((doc) => {
        const busy = activeOps.has(doc.id)
        const selected = selectedId === doc.id
        const inProgress = IN_PROGRESS_STATUSES.has(doc.status)

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
              <span className={statusClass(doc.status)}>{STATUS_LABELS[doc.status] ?? doc.status}</span>
            </div>

            {doc.status === 'failed' && (
              <p className="document-error">
                {doc.error ?? 'Something went wrong while preparing this document.'}
              </p>
            )}

            <div className="document-actions">
              {doc.status === 'embedded' && onSelect && (
                <button className="primary-button" onClick={() => onSelect(doc.id)} disabled={busy}>
                  {selected ? 'Selected' : 'Open chat'}
                </button>
              )}
              {doc.status === 'failed' && (
                <button className="secondary-button" onClick={() => onRetry(doc.id)} disabled={busy}>
                  {busy ? 'Retrying…' : 'Retry'}
                </button>
              )}
              {inProgress && <span className="document-progress-note">Preparing your document…</span>}
              <button className="ghost-button" onClick={() => onDelete(doc.id)} disabled={busy || inProgress}>
                {busy ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
