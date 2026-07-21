import type { DocumentResponse } from '../types/document'

interface DocumentListProps {
  documents: DocumentResponse[]
  onDelete: (id: string) => void
}

export function DocumentList({ documents, onDelete }: DocumentListProps) {
  if (documents.length === 0) {
    return <p>No documents uploaded yet.</p>
  }

  return (
    <ul>
      {documents.map((doc) => (
        <li key={doc.id}>
          <span>{doc.filename}</span>
          <span> — {doc.status}</span>
          <button onClick={() => onDelete(doc.id)} style={{ marginLeft: 8 }}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  )
}
