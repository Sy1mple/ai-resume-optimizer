import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000'),
  timeout: 20000
})

export async function generateContent(taskType, payload, aiProvider = 'free', openaiApiKey = '') {
  const { data } = await api.post('/api/generate', {
    task_type: taskType,
    payload,
    ai_provider: aiProvider,
    openai_api_key: openaiApiKey || undefined
  })
  return data
}

export async function getHistory() {
  const { data } = await api.get('/api/history')
  return data
}

export async function deleteHistoryRecord(id) {
  const { data } = await api.delete(`/api/history/${id}`)
  return data
}

export async function exportDocument(payload) {
  const response = await api.post('/api/export', payload, {
    responseType: 'blob'
  })
  const disposition = response.headers['content-disposition'] || ''
  const match = disposition.match(/filename="(.+)"/)
  return {
    blob: response.data,
    filename: match?.[1] || `resume.${payload.format}`
  }
}

export async function requestEmailCode(email) {
  const { data } = await api.post('/api/auth/email-code', { email })
  return data
}

export async function verifyEmailCode(email, code) {
  const { data } = await api.post('/api/auth/verify-code', { email, code })
  return data
}

export async function qrLogin(provider) {
  const { data } = await api.post('/api/auth/qr-login', { provider })
  return data
}

export async function createQrSession(provider) {
  const { data } = await api.post('/api/auth/qr-session', { provider })
  return data
}

export async function getQrSession(sessionId) {
  const { data } = await api.get(`/api/auth/qr-session/${sessionId}`)
  return data
}
