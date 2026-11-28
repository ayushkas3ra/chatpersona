import './Sidebar.css'

export default function Sidebar({
  personas,
  selectedPersonaId,
  onSelectPersona,
}) {
  return (
    <aside className="sidebar">
      <h2>ChatPersona</h2>

      <button
        type="button"
        className="import-button"
        onClick={() => onSelectPersona(null)}
      >
        + Import chat
      </button>

      <h3 className="sidebar-heading">Your personas</h3>

      <div className="participant-list">
        {personas.length === 0 && (
          <p className="empty-personas">
            No personas yet. Import a conversation to get started.
          </p>
        )}

        {personas.map((persona) => (
          <button
            type="button"
            key={persona.id}
            className={`participant ${
              selectedPersonaId === persona.id ? 'active' : ''
            }`}
            onClick={() => onSelectPersona(persona.id)}
            aria-pressed={selectedPersonaId === persona.id}
          >
            <span className="participant-name">{persona.participant_name}</span>

            <span className="participant-meta">
              Import #{persona.chat_import_id}
            </span>
          </button>
        ))}
      </div>
    </aside>
  )
}
