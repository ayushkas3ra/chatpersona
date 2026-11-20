import './App.css'
import { useState } from 'react'

import ChatWindow from './components/ChatWindow'
import Sidebar from './components/Sidebar'

export default function App() {
  const [selectedParticipant, setSelectedParticipant] = useState('')
  return (
    <div className="app-container">
      <Sidebar
        selectedParticipant={selectedParticipant}
        onSelectParticipant={setSelectedParticipant}
      />
      <main className="chat-container">
        <ChatWindow
          key={selectedParticipant}
          participant={selectedParticipant}
        />
      </main>
    </div>
  )
}
