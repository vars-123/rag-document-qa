import type { ConversationSummary } from '../types/chat'

interface ConversationSidebarProps {
  conversations: ConversationSummary[]
  loading: boolean
  activeSessionId: string | null
  onSelect: (sessionId: string) => void
}

function formatTimestamp(iso: string) {
  const date = new Date(iso)
  const today = new Date()
  const sameDay = date.toDateString() === today.toDateString()
  return sameDay
    ? date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
    : date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

export function ConversationSidebar({
  conversations,
  loading,
  activeSessionId,
  onSelect,
}: ConversationSidebarProps) {
  return (
    <aside className="conversation-sidebar">
      <h3 className="conversation-sidebar-title">Conversations</h3>
      {loading && <div className="conversation-sidebar-empty">Loading...</div>}
      {!loading && conversations.length === 0 && (
        <div className="conversation-sidebar-empty">
          No past conversations. Your chats about this document will appear here.
        </div>
      )}
      <ul className="conversation-list">
        {conversations.map((conv) => (
          <li key={conv.session_id}>
            <button
              type="button"
              className={`conversation-item ${conv.session_id === activeSessionId ? 'is-active' : ''}`}
              onClick={() => onSelect(conv.session_id)}
            >
              <span className="conversation-title">
                {conv.title || 'Untitled conversation'}
              </span>
              <span className="conversation-meta">
                <span>{formatTimestamp(conv.updated_at)}</span>
                <span>{conv.message_count} msg</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}
