import { apiRequest } from './apiClient'

export async function uploadChat(file) {
  const formData = new FormData()

  formData.append('file', file)

  return apiRequest('/uploads/', {
    method: 'POST',
    body: formData,
  })
}

export async function getPersonas() {
  const data = await apiRequest('/personas/')

  return data.personas
}
