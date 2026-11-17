import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { reactive } from 'vue'


interface ApiErrorPayload {
  code?: string
  message?: string
}

export interface ApiEnvelope<T> {
  data: T
  message: string
  meta?: Record<string, unknown>
}

export const apiState = reactive({
  pendingRequests: 0,
  errorMessage: '',
})

export function clearApiError() {
  apiState.errorMessage = ''
}

function finishRequest() {
  apiState.pendingRequests = Math.max(0, apiState.pendingRequests - 1)
}

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 12_000,
  headers: {
    Accept: 'application/json',
  },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  apiState.pendingRequests += 1
  const token = localStorage.getItem('pawfinder_access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    finishRequest()
    return response
  },
  (error: AxiosError<ApiErrorPayload>) => {
    finishRequest()
    const message = error.response?.data?.message
    apiState.errorMessage =
      message || (error.code === 'ECONNABORTED' ? '请求超时，请稍后重试' : '网络连接异常，请检查服务是否已启动')
    if (error.response?.status === 401) {
      window.dispatchEvent(new CustomEvent('pawfinder:auth-expired'))
    }
    return Promise.reject(error)
  },
)

export default apiClient
