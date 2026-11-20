const API_URL = 'http://127.0.0.1:8000/api/chat/'
const HISTORY_URL = 'http://127.0.0.1:8000/api/history/'

export async function sendChatMessage(participant, message) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      participant: participant,
      message: message,
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.Error || 'Something went wrong. Please try again.')
  }

  return data
}

export async function getChatHistory(participant) {
  const response = await fetch(
    `${HISTORY_URL}?participant=${encodeURIComponent(participant)}`
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch history, ${response.status}`)
  }

  const data = await response.json()

  return data.messages
}
