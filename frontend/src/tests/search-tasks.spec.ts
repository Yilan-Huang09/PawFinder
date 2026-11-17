import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SearchTaskPanel from '@/components/search/SearchTaskPanel.vue'
import type { SearchTask } from '@/types/domain'

const availableTask: SearchTask = {
  task_id: 21,
  area_id: 6,
  volunteer_id: null,
  status: 'AVAILABLE',
  accepted_at: null,
  started_at: null,
  completed_at: null,
  report: null,
  updated_at: '2026-11-10T10:00:00',
  area: {
    area_id: 6,
    case_id: 4,
    created_by: 1,
    area_name: '公园东区',
    center_latitude: 30.211,
    center_longitude: 120.221,
    radius_meters: 900,
    description: '沿公园出口巡查',
    status: 'OPEN',
  },
}

describe('search task collaboration', () => {
  it('allows an available task to be claimed', async () => {
    const wrapper = mount(SearchTaskPanel, {
      props: { tasks: [availableTask], currentUserId: 8 },
    })

    await wrapper.get('[data-test="claim-task-21"]').trigger('click')
    expect(wrapper.emitted('claim')).toEqual([[availableTask]])
  })

  it('requires a report and emits progress and completion updates', async () => {
    const claimed = { ...availableTask, volunteer_id: 8, status: 'CLAIMED' as const }
    const wrapper = mount(SearchTaskPanel, {
      props: { tasks: [claimed], currentUserId: 8 },
    })

    await wrapper.get('[data-test="start-task-21"]').trigger('click')
    expect(wrapper.emitted('update')).toEqual([[claimed, 'IN_PROGRESS', null]])

    await wrapper.setProps({ tasks: [{ ...claimed, status: 'IN_PROGRESS' }] })
    await wrapper.get('textarea[name="task_report_21"]').setValue('已沿绿道完整巡查，未发现目标。')
    await wrapper.get('[data-test="complete-task-21"]').trigger('click')
    expect(wrapper.emitted('update')?.at(-1)).toEqual([
      expect.objectContaining({ task_id: 21 }),
      'COMPLETED',
      '已沿绿道完整巡查，未发现目标。',
    ])
  })

  it('shows an API conflict without losing the task list', () => {
    const wrapper = mount(SearchTaskPanel, {
      props: {
        tasks: [availableTask],
        currentUserId: 8,
        errorMessage: '该任务已被其他志愿者认领',
      },
    })

    expect(wrapper.get('[role="alert"]').text()).toContain('已被其他志愿者认领')
    expect(wrapper.text()).toContain('公园东区')
  })
})
