import { setActivePinia, createPinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import type { RouteLocationNormalized } from 'vue-router'

import { authenticationGuard } from '@/router'
import { useAuthStore } from '@/stores/auth'
import { toLocalDateTimePayload } from '@/utils/format'

describe('frontend foundation', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('persists and clears an authenticated session', () => {
    const auth = useAuthStore()
    auth.setSession({
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      user: {
        user_id: 7,
        username: 'finder',
        role: 'USER',
        status: 'ACTIVE',
      },
    })

    expect(auth.isAuthenticated).toBe(true)
    expect(localStorage.getItem('pawfinder_access_token')).toBe('access-token')

    auth.clearSession()
    expect(auth.isAuthenticated).toBe(false)
    expect(localStorage.getItem('pawfinder_access_token')).toBeNull()
  })

  it('redirects anonymous visitors away from protected pages', () => {
    const result = authenticationGuard({
      name: 'notifications',
      fullPath: '/notifications',
      meta: { requiresAuth: true },
    } as RouteLocationNormalized)

    expect(result).toEqual({
      name: 'login',
      query: { redirect: '/notifications' },
    })
  })

  it('keeps datetime-local values in Asia/Shanghai wall-clock time', () => {
    expect(toLocalDateTimePayload('2026-11-17T17:30')).toBe('2026-11-17T17:30:00')
  })
})
