import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'

vi.mock('@/api/client', () => ({
  default: {
    post: vi.fn(),
  },
}))

describe('authentication views', () => {
  let testRouter: ReturnType<typeof createRouter>

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.mocked(apiClient.post).mockReset()
    testRouter = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: { template: '<div />' } },
        { path: '/register', component: { template: '<div />' } },
        { path: '/pets', component: { template: '<div />' } },
      ],
    })
    await testRouter.push('/login')
    await testRouter.isReady()
  })

  it('logs in and persists the returned session', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        data: {
          access_token: 'token-from-api',
          user: {
            user_id: 2,
            username: 'linyu',
            role: 'USER',
            status: 'ACTIVE',
          },
        },
        message: '登录成功',
      },
    })
    const wrapper = mount(LoginView, {
      global: { plugins: [testRouter] },
    })

    await wrapper.find('input[name="username"]').setValue('linyu')
    await wrapper.find('input[name="password"]').setValue('PawFinder123!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(apiClient.post).toHaveBeenCalledWith('/auth/login', {
      username: 'linyu',
      password: 'PawFinder123!',
    })
    expect(useAuthStore().accessToken).toBe('token-from-api')
    expect(localStorage.getItem('pawfinder_access_token')).toBe('token-from-api')
  })

  it('rejects mismatched registration passwords before requesting the API', async () => {
    const wrapper = mount(RegisterView, {
      global: { plugins: [testRouter] },
    })

    await wrapper.find('input[name="username"]').setValue('new_user')
    await wrapper.find('input[name="password"]').setValue('Password123!')
    await wrapper.find('input[name="confirm_password"]').setValue('Password456!')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('两次输入的密码不一致')
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it('keeps registration controls inside responsive grid columns', () => {
    const wrapper = mount(RegisterView, {
      global: { plugins: [testRouter] },
    })

    expect(wrapper.findAll('.register-input')).toHaveLength(5)
    expect(wrapper.findAll('.register-form__row')).toHaveLength(2)
  })
})
