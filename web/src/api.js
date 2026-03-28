const BASE_URL = 'https://instagram-tracker-qav7.onrender.com'

function getUserID() {
  let id = localStorage.getItem('USER_ID')
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem('USER_ID', id)
  }
  return id
}

async function request(path, options = {}) {
  const res = await fetch(BASE_URL + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-User-ID': getUserID(),
      ...(options.headers || {}),
    },
  })
  if (!res.ok) {
    const text = await res.text()
    let msg = text
    try { msg = JSON.parse(text)?.detail || text } catch {}
    throw new Error(msg || `HTTP ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  getAccounts: ()              => request('/api/accounts'),
  addAccount:  (username, intervalHours) =>
    request('/api/accounts', {
      method: 'POST',
      body: JSON.stringify({ instagram_username: username, check_interval_hours: intervalHours, user_id: getUserID() }),
    }),
  deleteAccount: (id)          => request(`/api/accounts/${id}`, { method: 'DELETE' }),
  updateAccount: (id, patch)   => request(`/api/accounts/${id}`, { method: 'PATCH', body: JSON.stringify(patch) }),
  getSnapshot:   (id)          => request(`/api/accounts/${id}/snapshot`),
  checkNow:      (id)          => request(`/api/accounts/${id}/check-now`, { method: 'POST' }),
  getHistory:    (page = 1)    => request(`/api/history?page=${page}`),
  getAccountHistory: (id, page = 1) => request(`/api/history/${id}?page=${page}`),
  health:        ()            => request('/health'),
}
