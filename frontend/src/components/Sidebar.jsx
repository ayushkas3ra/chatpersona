import './Sidebar.css'

export default function Sidebar({ selectedParticipant, onSelectParticipant }) {
  const participants = ['Rahul', 'Ayush']
  return (
    <aside className="sidebar">
      <h2>ChatPersona</h2>
      <div className="participant-list">
        {participants.map((participant) => (
          <button
            key={participant}
            className={`participant ${selectedParticipant === participant ? 'active' : ''}`}
            onClick={() => onSelectParticipant(participant)}
          >
            {participant}
          </button>
        ))}
      </div>
    </aside>
  )
}
