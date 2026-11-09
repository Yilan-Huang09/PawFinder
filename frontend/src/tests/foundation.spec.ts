import { setActivePinia, createPinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import router from '@/router'
import { useAuthStore } from '@/stores/auth'

describe('frontend foundation', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    await router.push('/')
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

  it('redirects anonymous visitors away from protected pages', async () => {
    await router.push('/notifications')

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/notifications')
  })
})
