function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    ?.split('=')[1]
}

function extractErrorMessage(data, status) {
  if (typeof data?.detail === 'string') {
    return data.detail
  }

  if (typeof data?.error === 'string') {
    return data.error
  }

  if (data && typeof data === 'object') {
    const messages = Object.values(data)
      .flat()
      .filter((value) => typeof value === 'string')

    if (messages.length > 0) {
      return messages.join(' ')
    }
  }

  return `Request failed: ${status}`
}

export async function apiRequest(endpoint, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = new Headers(options.headers)

  if (!['GET', 'Head', 'OPTIONS', 'TRACE'].includes(method)) {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken)
    }
  }

  const response = await fetch(`/api${endpoint}`, {
    ...options,
    method,
    headers,
    credentials: 'same-origin',
  })

  const contentType = response.headers.get('content-type') || ''

  let data = null

  if (response.status !== 204) {
    if (contentType.includes('application/json')) {
      data = await response.json()
    } else {
      data = await response.text()
    }
  }

  if (!response.ok) {
    const error = new Error(extractErrorMessage(data, response.status))

    error.status = response.status

    throw error
  }

  return data
}
