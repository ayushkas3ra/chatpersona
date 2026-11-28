import { useState } from 'react'
import { uploadChat } from '../services/personaApi'
import './ChatUpload.css'

const MAX_FILE_SIZE = 5 * 1024 * 1024

export default function ChatUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [consent, setConsent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  function handleFileChange(event) {
    const selectedFile = event.target.files[0]

    setError('')
    setSuccess('')
    setFile(null)
    setConsent(false)

    if (!selectedFile) return

    if (!selectedFile.name.toLowerCase().endsWith('.txt')) {
      setError('Please select a .txt file.')
      event.target.value = ''
      return
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setError('File size must not exceed 5 MB.')
      event.target.value = ''
      return
    }

    if (selectedFile.size === 0) {
      setError('The selected file is empty.')
      event.target.value = ''
      return
    }

    setFile(selectedFile)
  }

  async function handleSubmit(event) {
    event.preventDefault()

    if (loading) return

    setError('')
    setSuccess('')

    if (!file) {
      setError('Please select a file.')
      return
    }

    if (!consent) {
      setError('Please confirm participant consent.')
      return
    }

    setLoading(true)

    try {
      const result = await uploadChat(file)

      setSuccess(
        `Upload successful! ${result.personas.length} personas created.`
      )

      setFile(null)
      setConsent(false)
      event.target.reset()

      onUploadSuccess(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-container">
      <h2>Import a conversation</h2>

      <p>Upload a WhatsApp chat export (.txt).</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="chat-file">Select chat file</label>

        <input
          id="chat-file"
          type="file"
          accept=".txt"
          onChange={handleFileChange}
          disabled={loading}
        />

        {file && (
          <p className="selected-file">
            {file.name} - {(file.size / 1024).toFixed(2)} KB
          </p>
        )}

        <label className="upload-consent">
          <input
            type="checkbox"
            checked={consent}
            onChange={(event) => setConsent(event.target.checked)}
            disabled={loading}
          />
          I have permission from the participants to process this conversation
          and create AI communication-style simulations.
        </label>

        {error && (
          <p className="upload-error" role="alert">
            {error}
          </p>
        )}

        {success && (
          <p className="upload-success" role="status">
            {success}
          </p>
        )}

        <button type="submit" disabled={loading || !file || !consent}>
          {loading ? 'Analyzing conversation...' : 'Upload and analyze'}
        </button>
      </form>

      <p className="upload-disclaimer">
        Generated personas are AI simulations, not the actual people.
      </p>
    </div>
  )
}
