import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 20000
})

export async function generateContent(taskType, payload) {
  const { data } = await api.post('/api/generate', {
    task_type: taskType,
    payload
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
