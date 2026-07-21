import type { DocumentResponse } from '../types/document'

interface DocumentListProps {
  documents: DocumentResponse[]
  onDelete: (id: string) => void
  onProcess: (id: string) => void
  onEmbed: (id: string) => void
  onSelect?: (id: string) => void
  selectedId?: string | null
}

export function DocumentList({ documents, onDelete, onProcess, onEmbed, onSelect, selectedId }: DocumentListProps) {
  if (documents.length === 0) {
    return <p>No documents uploaded yet.</p>
  }

  return (
    <ul>
      {documents.map((doc) => (
        <li
          key={doc.id}
          style={{
            background: selectedId === doc.id ? '#e0f2fe' : undefined,
            padding: '4px 8px',
            borderRadius: 4,
          }}
        >
          <span>{doc.filename}</span>
          <span> — {doc.status}</span>
          {doc.status === 'uploaded' && (
            <button onClick={() => onProcess(doc.id)} style={{ marginLeft: 8 }}>
              Process
            </button>
          )}
          {doc.status === 'processed' && (
            <button onClick={() => onEmbed(doc.id)} style={{ marginLeft: 8 }}>
              Embed
            </button>
          )}
          {doc.status === 'embedded' && onSelect && (
            <button onClick={() => onSelect(doc.id)} style={{ marginLeft: 8 }}>
              Ask
            </button>
          )}
          <button onClick={() => onDelete(doc.id)} style={{ marginLeft: 8, marginTop: 4 }}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  )
}
