import { type FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import { useChat } from '../hooks/useChat'
import { useConversations } from '../hooks/useConversations'
import { ConversationSidebar } from './ConversationSidebar'
import type { ChatMessage } from '../types/chat'

interface ChatInterfaceProps {
  documentId: string
  documentName: string
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
        <div className="message-meta">
          <span>{isUser ? 'You' : 'Assistant'}</span>
          <span>{new Date(msg.timestamp).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</span>
        </div>
        <div>{msg.content || (msg.role === 'assistant' ? '...' : '')}</div>
      </div>
    </div>
  )
}

export function ChatInterface({ documentId, documentName }: ChatInterfaceProps) {
  const { messages, streaming, error, send, startNew, switchSession, sessionId, loadingHistory } = useChat(documentId)
  const { conversations, loading: loadingConversations, refresh: refreshConversations } = useConversations(documentId)
  const [draft, setDraft] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [documentId, sessionId])

  const canSend = useMemo(() => {
    return draft.trim().length > 0 && !streaming && !loadingHistory
  }, [draft, loadingHistory, streaming])

  const submit = async () => {
    if (!canSend) return
    const question = draft.trim()
    setDraft('')
    await send(question)
    refreshConversations()
    inputRef.current?.focus()
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    submit()
  }

  return (
    <div className="chat-layout">
      <ConversationSidebar
        conversations={conversations}
        loading={loadingConversations}
        activeSessionId={sessionId}
        onSelect={switchSession}
      />
      <div className="chat-shell">
        <div className="chat-header">
          <div>
            <h2 className="chat-title">{documentName}</h2>
            <p className="chat-description">Ask grounded questions from the selected PDF.</p>
          </div>
          <button className="secondary-button" onClick={startNew} disabled={messages.length === 0 && !loadingHistory}>
            New chat
          </button>
        </div>

      <div className="chat-thread" role="log" aria-live="polite">
        {loadingHistory && (
          <div className="chat-placeholder">
            Loading conversation history
            <span className="loading-dots" aria-hidden="true" style={{ marginLeft: 8 }}>
              <span />
              <span />
              <span />
            </span>
          </div>
        )}
        {!loadingHistory && messages.length === 0 && (
          <div className="chat-placeholder">
            No messages yet. Start with a question about this document.
          </div>
        )}
        {messages.map((msg, index) => (
          <MessageBubble key={`${msg.role}-${index}-${msg.timestamp}`} msg={msg} />
        ))}
        {error && <div className="banner">{error}</div>}
      </div>

      <form className="chat-composer" onSubmit={handleSubmit}>
        <div className="chat-input-row">
          <textarea
            ref={inputRef}
            placeholder="Ask something specific about the uploaded PDF..."
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            disabled={streaming || loadingHistory}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                submit()
              }
            }}
          />
          <button className="primary-button" type="submit" disabled={!canSend}>
            {streaming ? 'Thinking…' : 'Send'}
          </button>
        </div>
        <div className="chat-help">
          <span>Enter sends, Shift+Enter adds a new line.</span>
          <span>{streaming ? 'Generating answer...' : 'Responses stream in real time.'}</span>
        </div>
      </form>
      </div>
    </div>
  )
}
