import { apiRequest } from './apiClient'

export async function sendChatMessage(personaId, message) {
  return apiRequest('/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      persona_id: personaId,
      message: message,
    }),
  })
}

export async function getChatHistory(personaId) {
  const data = await apiRequest(
    `/history/?persona_id=${encodeURIComponent(personaId)}`
  )

  return data.messages
}
