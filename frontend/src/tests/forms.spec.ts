import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { createCase, optimizeDescription } from '@/api/workflows'
import { fetchPets } from '@/api/pets'
import LocationFields from '@/components/forms/LocationFields.vue'
import PhotoUploader from '@/components/uploads/PhotoUploader.vue'
import CaseCreateView from '@/views/CaseCreateView.vue'

vi.mock('@/api/pets', () => ({ fetchPets: vi.fn() }))
vi.mock('@/api/workflows', () => ({
  createCase: vi.fn(),
  optimizeDescription: vi.fn(),
}))

describe('form components and workflows', () => {
  beforeEach(() => {
    vi.mocked(fetchPets).mockResolvedValue([
      {
        pet_id: 1,
        owner_id: 2,
        name: '豆包',
        species: 'DOG',
        primary_color: 'BLACK',
        gender: 'FEMALE',
        size: 'MEDIUM',
        status: 'ACTIVE',
      },
    ])
    vi.mocked(createCase).mockResolvedValue({ case_id: 9 } as never)
    vi.mocked(optimizeDescription).mockResolvedValue({
      text: '黑白边牧，戴红色项圈。',
      source: 'local',
      suggestions: ['补充最后出现方向'],
    })
  })

  it('emits valid coordinates and address changes', async () => {
    const wrapper = mount(LocationFields, {
      props: { latitude: null, longitude: null, address: '' },
    })

    await wrapper.find('input[name="latitude"]').setValue('29.8269')
    await wrapper.find('input[name="longitude"]').setValue('106.4253')
    await wrapper.find('input[name="address"]').setValue('西南大学北门附近')

    expect(wrapper.emitted('update:latitude')?.at(-1)).toEqual([29.8269])
    expect(wrapper.emitted('update:longitude')?.at(-1)).toEqual([106.4253])
    expect(wrapper.emitted('update:address')?.at(-1)).toEqual(['西南大学北门附近'])
  })

  it('offers reliable Chongqing coordinate shortcuts and fixes swapped values', async () => {
    const presetWrapper = mount(LocationFields, {
      props: { latitude: null, longitude: null, address: '' },
    })

    await presetWrapper.get('[data-test="use-swu-location"]').trigger('click')
    expect(presetWrapper.emitted('update:latitude')?.at(-1)).toEqual([29.8269])
    expect(presetWrapper.emitted('update:longitude')?.at(-1)).toEqual([106.4253])
    expect(presetWrapper.emitted('update:address')?.at(-1)).toEqual(['西南大学北门天生路附近'])

    const swappedWrapper = mount(LocationFields, {
      props: { latitude: 106.4253, longitude: 29.8269, address: '西南大学' },
    })
    await swappedWrapper.get('[data-test="swap-coordinates"]').trigger('click')
    expect(swappedWrapper.emitted('update:latitude')?.at(-1)).toEqual([29.8269])
    expect(swappedWrapper.emitted('update:longitude')?.at(-1)).toEqual([106.4253])
  })

  it('previews and removes selected images', async () => {
    const wrapper = mount(PhotoUploader, {
      props: { modelValue: [], maxFiles: 2 },
    })
    const input = wrapper.find('input[type="file"]')
    const file = new File(['image-content'], 'pet.png', { type: 'image/png' })
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')

    const selectedFiles = wrapper.emitted('update:modelValue')?.at(-1)?.[0] as File[]
    await wrapper.setProps({ modelValue: selectedFiles })
    expect(wrapper.text()).toContain('pet.png')
    expect(selectedFiles).toHaveLength(1)

    await wrapper.find('button[aria-label="移除 pet.png"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual([[]])
  })

  it('optimizes a description locally and submits the case', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/cases/new', component: { template: '<div />' } },
        { path: '/cases/:caseId', component: { template: '<div />' } },
      ],
    })
    await router.push('/cases/new')
    await router.isReady()
    const wrapper = mount(CaseCreateView, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.find('select[name="pet_id"]').setValue('1')
    await wrapper.find('input[name="lost_time"]').setValue('2026-11-09T12:00')
    await wrapper.find('input[name="latitude"]').setValue('29.8269')
    await wrapper.find('input[name="longitude"]').setValue('106.4253')
    await wrapper.find('input[name="address"]').setValue('西南大学北门附近')
    await wrapper.find('textarea[name="description"]').setValue('黑白边牧 戴红色项圈')
    await wrapper.find('button[data-test="optimize-description"]').trigger('click')
    await flushPromises()

    expect(vi.mocked(optimizeDescription)).toHaveBeenCalledWith('黑白边牧 戴红色项圈')
    expect((wrapper.find('textarea[name="description"]').element as HTMLTextAreaElement).value)
      .toBe('黑白边牧，戴红色项圈。')

    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(vi.mocked(createCase)).toHaveBeenCalledWith(expect.objectContaining({
      pet_id: 1,
      lost_time: '2026-11-09T12:00:00',
      latitude: 29.8269,
      longitude: 106.4253,
    }))
  })
})
