import { apiRequest } from './apiClient'

export async function initializeCsrf() {
  return apiRequest('/auth/csrf')
}

export async function register(username, password) {
  await initializeCsrf()

  return apiRequest('/auth/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })
}

export async function login( username, password ) {
  await initializeCsrf()

  return apiRequest('/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })
}

export async function logout() {
  return apiRequest('/auth/logout/', {
    method: 'POST',
  })
}

export async function getCurrentUser() {
  return apiRequest('/auth/me/')
}
