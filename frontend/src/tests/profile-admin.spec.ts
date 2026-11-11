import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import StatsCards from '@/components/admin/StatsCards.vue'
import NotificationList from '@/components/notifications/NotificationList.vue'
import type { AdminStatistics, AppNotification } from '@/types/domain'

const notification: AppNotification = {
  notification_id: 5,
  user_id: 1,
  type: 'MATCH_FOUND',
  title: '发现高分线索',
  content: '文三路附近有一条 90.5 分候选线索。',
  related_case_id: 1,
  related_match_id: 2,
  related_task_id: null,
  is_read: false,
  created_at: '2026-11-10T10:00:00',
  read_at: null,
}

const statistics: AdminStatistics = {
  users: { total: 12, active: 11, disabled: 1 },
  cases: { total: 8, searching: 5, reunited: 2, closed: 1 },
  sightings: { total: 20, active: 17, hidden: 2, invalid: 1 },
  matches: { total: 14, pending: 4, high_score: 6 },
  tasks: { total: 10, available: 3, in_progress: 2, completed: 5 },
  reunions: { total: 2 },
}

describe('profile, notifications and administration', () => {
  it('shows unread notifications and emits read actions', async () => {
    const wrapper = mount(NotificationList, { props: { items: [notification] } })

    expect(wrapper.text()).toContain('发现高分线索')
    expect(wrapper.find('.notification-item--unread').exists()).toBe(true)
    await wrapper.get('[data-test="read-notification-5"]').trigger('click')
    expect(wrapper.emitted('read')).toEqual([[notification]])
  })

  it('renders presentation-ready administration statistics', () => {
    const wrapper = mount(StatsCards, { props: { statistics } })

    expect(wrapper.text()).toContain('12')
    expect(wrapper.text()).toContain('5 个寻找中')
    expect(wrapper.text()).toContain('6 个高分匹配')
    expect(wrapper.text()).toContain('2')
  })
})
