import './MessageBubble.css'

export default function MessageBubble({ message }) {
  return (
    <div className={`message ${message.role}`}>
      <p>{message.content}</p>
    </div>
  )
}
