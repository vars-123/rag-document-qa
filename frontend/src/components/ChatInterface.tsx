import { type FormEvent, useRef } from 'react'
import { useChat } from '../hooks/useChat'
import type { ChatMessage } from '../types/chat'

interface ChatInterfaceProps {
  documentId: string
  documentName: string
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'
  return (
    <div
      style={{
        marginBottom: 12,
        textAlign: isUser ? 'right' : 'left',
      }}
    >
      <div
        style={{
          display: 'inline-block',
          background: isUser ? '#dbeafe' : '#f3f4f6',
          borderRadius: 8,
          padding: '8px 12px',
          maxWidth: '80%',
          textAlign: 'left',
          whiteSpace: 'pre-wrap',
        }}
      >
        {msg.content || (msg.role === 'assistant' ? '...' : '')}
      </div>
    </div>
  )
}

export function ChatInterface({ documentId, documentName }: ChatInterfaceProps) {
  const { messages, streaming, error, send, clear } = useChat(documentId)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const input = inputRef.current
    if (!input) return
    const val = input.value
    if (!val.trim() || streaming) return
    input.value = ''
    send(val)
  }

  return (
    <div
      style={{
        border: '1px solid #d1d5db',
        borderRadius: 8,
        display: 'flex',
        flexDirection: 'column',
        height: 400,
      }}
    >
      <div
        style={{
          padding: '8px 12px',
          borderBottom: '1px solid #d1d5db',
          fontWeight: 600,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span>Chat: {documentName}</span>
        <button onClick={clear} disabled={messages.length === 0}>
          Clear
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: 12 }}>
        {messages.length === 0 && (
          <p style={{ color: '#9ca3af' }}>Ask a question about this document.</p>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', borderTop: '1px solid #d1d5db' }}>
        <input
          ref={inputRef}
          type="text"
          placeholder="Type your question..."
          disabled={streaming}
          style={{ flex: 1, border: 'none', padding: '8px 12px', outline: 'none' }}
        />
        <button type="submit" disabled={streaming} style={{ padding: '8px 16px' }}>
          {streaming ? '...' : 'Send'}
        </button>
      </form>
    </div>
  )
}
