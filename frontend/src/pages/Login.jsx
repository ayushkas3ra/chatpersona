import { useState } from 'react'
import { login, getCurrentUser } from '../services/authApi'
import './Auth.css'

export default function Login({ onLogin, onSwitchToRegister, successMessage }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    if (loading) return

    setError('')
    setLoading(true)

    try {
      await login(username, password)

      const user = await getCurrentUser()

      onLogin(user)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>ChatPersona</h1>
        <p>Sign in to your account</p>

        <form onSubmit={handleSubmit}>
          {successMessage && (
            <p className="auth-success" role="status">
              {successMessage}
            </p>
          )}
          <label htmlFor="username">Username</label>

          <input
            id="username"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
          />

          <label htmlFor="password">Password</label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />

          {error && (
            <p className="auth-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Log in'}
          </button>
        </form>

        <p className="auth-switch">
          Don't have an account?
          <button
            type="button"
            onClick={() => onSwitchToRegister()}
            disabled={loading}
          >
            Register
          </button>
        </p>
      </div>
    </div>
  )
}
