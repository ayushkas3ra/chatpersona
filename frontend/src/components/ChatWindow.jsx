import './ChatWindow.css'
import MessageBubble from './MessageBubble'
import { useState, useEffect, useRef } from 'react'
import { sendChatMessage, getChatHistory } from '../services/chatApi'

export default function ChatWindow({ persona }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyLoading, setHistoryLoading] = useState(true)

  const messageListRef = useRef(null)
  const personaId = persona.id

  // Automatic scrolling
  useEffect(() => {
    if (historyLoading) return

    const container = messageListRef.current

    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, [messages, historyLoading, loading, error])

  // Load conversation history
  useEffect(() => {
    let cancelled = false

    async function loadMessages() {
      setHistoryLoading(true)
      setMessages([])
      setInput('')
      setError('')

      try {
        const history = await getChatHistory(personaId)

        if (!cancelled) {
          setMessages(Array.isArray(history) ? history : [])
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
        }
      } finally {
        if (!cancelled) {
          setHistoryLoading(false)
        }
      }
    }

    loadMessages()

    return () => {
      cancelled = true
    }
  }, [personaId])

  // Send a message
  async function handleSendMessage(event) {
    event.preventDefault()

    const messageText = input.trim()

    if (!messageText || loading || historyLoading) return

    const newMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: messageText,
    }

    setMessages((previous) => [...previous, newMessage])

    setInput('')
    setError('')
    setLoading(true)

    try {
      const data = await sendChatMessage(personaId, messageText)

      const aiMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.reply,
      }

      setMessages((previous) => [...previous, aiMessage])
    } catch (err) {
      // Remove optimistic message only if the request fails
      setMessages((previous) =>
        previous.filter((message) => message.id !== newMessage.id)
      )

      setInput(messageText)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-window">
      <header className="chat-header">
        <h2>{persona.participant_name}</h2>
        <small>AI-generated style simulation, not the actual person</small>
      </header>

      <div className="message-list" ref={messageListRef}>
        {historyLoading ? (
          <p>Loading conversation...</p>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}

        {loading && <p>ChatPersona is thinking...</p>}

        {error && (
          <p className="chat-error" role="alert">
            {error}
          </p>
        )}
      </div>

      <form className="chat-input" onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Type a message..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={loading || historyLoading}
          maxLength={4000}
          aria-label="Chat message"
        />

        <button
          type="submit"
          disabled={loading || historyLoading || !input.trim()}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}
