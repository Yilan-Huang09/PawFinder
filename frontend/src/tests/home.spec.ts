import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import HomeView from '@/views/HomeView.vue'
import { fetchCases } from '@/api/cases'

vi.mock('@/api/cases', () => ({
  fetchCases: vi.fn(),
}))

const caseFixture = {
  case_id: 1,
  pet_id: 1,
  publisher_id: 2,
  lost_time: '2026-11-08T07:40:00',
  latitude: 30.2741,
  longitude: 120.1551,
  address: '西湖区文三路地铁站附近',
  description: '晨间散步时挣脱牵引绳。',
  contact_phone: '138****0002',
  status: 'SEARCHING' as const,
  closed_at: null,
  created_at: '2026-11-08T08:00:00',
  updated_at: '2026-11-08T08:00:00',
  pet: {
    pet_id: 1,
    owner_id: 2,
    name: '豆包',
    species: 'DOG',
    breed: 'Border Collie',
    primary_color: 'BLACK',
    secondary_color: 'WHITE',
    gender: 'FEMALE',
    size: 'MEDIUM',
    distinctive_features: '胸口白色心形毛，红色项圈',
    status: 'ACTIVE',
    cover_photo_url: null,
  },
}

describe('HomeView', () => {
  beforeEach(() => {
    vi.mocked(fetchCases).mockResolvedValue({
      items: [caseFixture],
      meta: { page: 1, per_page: 4, total: 1, pages: 1 },
    })
  })

  it('puts the three primary actions above discovery content', async () => {
    const wrapper = mount(HomeView, {
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('发布走失')
    expect(text).toContain('提交目击')
    expect(text).toContain('加入搜寻')
    expect(text.indexOf('发布走失')).toBeLessThan(text.indexOf('附近正在寻找'))
  })

  it('renders nearby cases returned by the public API', async () => {
    const wrapper = mount(HomeView, {
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()

    expect(fetchCases).toHaveBeenCalledWith({ page: 1, per_page: 4, status: 'SEARCHING' })
    expect(wrapper.text()).toContain('豆包')
    expect(wrapper.text()).toContain('西湖区文三路地铁站附近')
  })
})
