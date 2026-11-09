import { computed, ref } from 'vue'
import { defineStore } from 'pinia'


export interface AuthUser {
  user_id: number
  username: string
  role: 'USER' | 'ADMIN'
  status: 'ACTIVE' | 'DISABLED'
  phone?: string | null
  email?: string | null
  avatar_url?: string | null
}

export interface AuthSession {
  accessToken: string
  refreshToken: string
  user: AuthUser
}

const ACCESS_TOKEN_KEY = 'pawfinder_access_token'
const REFRESH_TOKEN_KEY = 'pawfinder_refresh_token'
const USER_KEY = 'pawfinder_user'

function readStoredUser(): AuthUser | null {
  const value = localStorage.getItem(USER_KEY)
  if (!value) return null
  try {
    return JSON.parse(value) as AuthUser
  } catch {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_TOKEN_KEY))
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_KEY))
  const user = ref<AuthUser | null>(readStoredUser())

  const isAuthenticated = computed(
    () => Boolean(accessToken.value && user.value?.status === 'ACTIVE'),
  )
  const isAdmin = computed(
    () => isAuthenticated.value && user.value?.role === 'ADMIN',
  )

  function setSession(session: AuthSession) {
    accessToken.value = session.accessToken
    refreshToken.value = session.refreshToken
    user.value = session.user
    localStorage.setItem(ACCESS_TOKEN_KEY, session.accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, session.refreshToken)
    localStorage.setItem(USER_KEY, JSON.stringify(session.user))
  }

  function updateUser(nextUser: AuthUser) {
    user.value = nextUser
    localStorage.setItem(USER_KEY, JSON.stringify(nextUser))
  }

  function clearSession() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    isAdmin,
    setSession,
    updateUser,
    clearSession,
  }
})
