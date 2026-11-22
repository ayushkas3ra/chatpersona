import './ChatWindow.css'
import MessageBubble from './MessageBubble'
import { useState, useEffect, useRef } from 'react'
import { sendChatMessage, getChatHistory } from '../services/chatApi'

export default function ChatWindow({ participant }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [historyLoading, setHistoryLoading] = useState(false)

  const messageListRef = useRef(null)

  useEffect(() => {
    if (historyLoading) return

    const container = messageListRef.current

    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, [messages, historyLoading])

  useEffect(() => {
    let cancelled = false
    async function loadMessages() {
      //reset everything
      setHistoryLoading(true)
      setMessages([])
      setInput('')
      setError('')

      //fetching history
      try {
        const history = await getChatHistory(participant)
        if (!cancelled) {
          setMessages(Array.isArray(history) ? history : [])
        }
      } catch (error) {
        if (!cancelled) {
          setError(error.message)
        }
      } finally {
        if (!cancelled) {
          setHistoryLoading(false)
        }
      }
    }
    loadMessages(participant)
  }, [participant])

  async function handleSendMessage(event) {
    event.preventDefault()

    const messageText = input.trim()

    if (!messageText || loading || historyLoading) return

    const newMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
    }

    setMessages((previousMessage) => [...previousMessage, newMessage])

    setInput('')
    setError('')
    setLoading(true)

    try {
      const data = await sendChatMessage(participant, messageText)

      const aiMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.reply,
      }

      setMessages((previous) => [...previous, aiMessage])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-window">
      <header className="chat-header">
        <h2>{participant}</h2>
        <small>AI-generated style simulation</small>
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
        {error && <p className="chat-error">{error}</p>}
      </div>

      <form className="chat-input" onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading || historyLoading}
        />
        <button type="submit" disabled={loading || historyLoading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}
