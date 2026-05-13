import axios from 'axios'
import { getToken, removeToken } from './auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000,
})

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const contentApi = {
  generateScript: (topic: string, style: string) => api.post('/content/generate-script', { topic, style }),
  getTemplates: () => api.get('/content/templates'),
  getMedia: (params?: unknown) => api.get('/content/media', { params }),
  uploadMedia: (file: File, tags?: string, name?: string) => {
    const fd = new FormData()
    fd.append('file', file)
    if (tags) fd.append('tags', tags)
    if (name) fd.append('name', name)
    return api.post('/content/media/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  deleteMedia: (id: number) => api.delete(`/content/media/${id}`),
  updateMedia: (id: number, data: { tags?: string; name?: string }) => api.put(`/content/media/${id}`, data),
  composeVideo: (topic: string, templateId: number, style: string) => api.post('/content/compose-video', { topic, template_id: templateId, style }),
  getTasks: (params?: unknown) => api.get('/content/tasks', { params }),
  getTask: (id: number) => api.get(`/content/tasks/${id}`),
  downloadTask: (id: number) => api.get(`/content/tasks/${id}/download`, { responseType: 'blob' }),
  generateDigitalHuman: (avatarId: string, script: string) => api.post('/content/digital-human/generate', { avatar_id: avatarId, script }),
  getAvatars: () => api.get('/content/digital-human/avatars'),
}

export const distributionApi = {
  getAccounts: () => api.get('/accounts'),
  createAccount: (data: unknown) => api.post('/accounts', data),
  updateAccount: (id: number, data: unknown) => api.put(`/accounts/${id}`, data),
  deleteAccount: (id: number) => api.delete(`/accounts/${id}`),
  schedulePublish: (data: unknown) => api.post('/accounts/schedule-publish', data),
  getPublishLogs: (params?: unknown) => api.get('/accounts/publish-logs', { params }),
  getReportsOverview: () => api.get('/reports/overview'),
  getReportsAnomalies: () => api.get('/reports/anomalies'),
  getRankings: () => api.get('/reports/rankings'),
}

export const conversionApi = {
  chatAsk: (message: string, sessionId?: string) => api.post('/chat/ask', { message, session_id: sessionId }),
  chatHistory: (sessionId: string) => api.get(`/chat/history/${sessionId}`),
  getFunnel: () => api.get('/analytics/funnel'),
  getAttribution: () => api.get('/analytics/attribution'),
  getRoi: () => api.get('/analytics/roi'),
}

export const insightApi = {
  getProfiles: () => api.get('/insight/profiles'),
  getTopics: () => api.get('/insight/topics'),
  adoptTopic: (data: unknown) => api.post('/insight/topics/adopt', data),
}

export const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary'),
  getTrends: () => api.get('/dashboard/trends'),
}

export default api
