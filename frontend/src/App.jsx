import './App.css'
import { useState, useEffect } from 'react'

import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Register from './pages/Register'

import { getCurrentUser, logout } from './services/authApi'

import ChatUpload from './components/ChatUpload'
import { getPersonas } from './services/personaApi'

import ChatWindow from './components/ChatWindow'

export default function App() {
  const [selectedPersonaId, setSelectedPersonaId] = useState(null)

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [authPage, setAuthPage] = useState('login')
  const [successMessage, setSuccessMessage] = useState('')
  const [error, setError] = useState('')

  const [personas, setPersonas] = useState([])
  const [personasLoading, setPersonasLoading] = useState(false)
  const [personasError, setPersonasError] = useState('')

  const selectedPersona = personas.find(
    (persona) => persona.id === selectedPersonaId
  )

  useEffect(() => {
    if (!user) {
      setPersonas([])
      setPersonasError('')
      setPersonasLoading(false)
      return
    }

    let cancelled = false

    async function loadPersonas() {
      setPersonasLoading(true)
      setPersonasError('')

      try {
        const data = await getPersonas()

        if (!cancelled) {
          setPersonas(data)
        }
      } catch (err) {
        if (!cancelled) {
          setPersonasError(err.message)
        }
      } finally {
        if (!cancelled) {
          setPersonasLoading(false)
        }
      }
    }

    loadPersonas()

    return () => {
      cancelled = true
    }
  }, [user])

  useEffect(() => {
    checkSession()
  }, [])

  async function handleUploadSuccess() {
    setPersonasLoading(true)
    setPersonasError('')

    try {
      const data = await getPersonas()
      setPersonas(data)
    } catch (err) {
      setPersonasError(err.message)
    } finally {
      setPersonasLoading(false)
    }
  }

  async function checkSession() {
    setLoading(true)
    setError('')

    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
    } catch (err) {
      if (err.status === 403 || err.status === 401) {
        setUser(null)
      } else {
        setError('Unable to connect to the server.')
      }
    } finally {
      setLoading(false)
    }
  }

  function handleLogin(currentUser) {
    setUser(currentUser)
    setSuccessMessage('')
    setError('')
  }

  function showRegister() {
    setSuccessMessage('')
    setAuthPage('register')
  }

  function showLogin(message = '') {
    setSuccessMessage(message)
    setAuthPage('login')
  }

  async function handleLogout() {
    try {
      setError('')
      await logout()

      setUser(null)
      setSelectedPersonaId(null)
      setPersonas([])
      showLogin()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return <div>Loading ChatPersona...</div>
  }

  if (error && !user) {
    return (
      <div>
        <p role="alert">{error}</p>
        <button onClick={checkSession}>Retry</button>
      </div>
    )
  }

  if (!user) {
    if (authPage === 'register') {
      return <Register onSwitchToLogin={showLogin} />
    }

    return (
      <Login
        onLogin={handleLogin}
        onSwitchToRegister={showRegister}
        successMessage={successMessage}
      />
    )
  }

  return (
    <div className="app-container">
      <Sidebar
        personas={personas}
        selectedPersonaId={selectedPersonaId}
        onSelectPersona={setSelectedPersonaId}
      />

      <main className="chat-container">
        <header className="user-header">
          <span>Welcome, {user.username}</span>

          <button onClick={handleLogout}>Logout</button>
        </header>

        {error && <p role="alert">{error}</p>}

        {personasError && <p role="alert">{personasError}</p>}

        {personasLoading && <p>Loading personas...</p>}

        {!selectedPersona ? (
          <ChatUpload onUploadSuccess={handleUploadSuccess} />
        ) : (
          <ChatWindow key={selectedPersona.id} persona={selectedPersona} />
        )}
      </main>
    </div>
  )
}
