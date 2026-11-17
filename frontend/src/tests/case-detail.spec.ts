import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import CaseMap from '@/components/maps/CaseMap.vue'
import MatchScore from '@/components/matches/MatchScore.vue'
import SightingTimeline from '@/components/timeline/SightingTimeline.vue'
import type { CaseMatch, LostCase, Sighting } from '@/types/domain'

const match: CaseMatch = {
  match_id: 3,
  case_id: 1,
  sighting_id: 8,
  appearance_score: 92,
  distance_score: 84,
  time_score: 76,
  total_score: 86.4,
  distance_km: 1.25,
  match_reason: '外观高度相似，距离 1.25 公里',
  algorithm_version: 'rule-v1',
  review_status: 'PENDING',
  reviewed_by: null,
  generated_at: '2026-11-10T12:00:00',
  reviewed_at: null,
  sighting: {
    sighting_id: 8,
    reporter_id: 7,
    species: 'DOG',
    primary_color: 'BLACK',
    gender_guess: 'UNKNOWN',
    size_guess: 'MEDIUM',
    seen_time: '2026-11-10T11:00:00',
    latitude: 30.276,
    longitude: 120.1573,
    address: '西南大学北门公交站',
    confidence: 5,
    status: 'ACTIVE',
    created_at: '2026-11-10T11:05:00',
    updated_at: '2026-11-10T11:05:00',
  },
}

describe('case detail components', () => {
  it('explains a match score and emits owner review actions', async () => {
    const wrapper = mount(MatchScore, { props: { match } })

    expect(wrapper.text()).toContain('86.4')
    expect(wrapper.text()).toContain('外观 92')
    expect(wrapper.text()).toContain('距离 84')
    await wrapper.get('[data-test="confirm-match"]').trigger('click')
    expect(wrapper.emitted('review')).toEqual([['CONFIRMED']])
  })

  it('filters the sighting timeline by recent hours', async () => {
    const recent = { ...match.sighting, seen_time: new Date(Date.now() - 2 * 3_600_000).toISOString() }
    const old = {
      ...match.sighting,
      sighting_id: 9,
      address: '三天前的位置',
      seen_time: new Date(Date.now() - 72 * 3_600_000).toISOString(),
    }
    const wrapper = mount(SightingTimeline, { props: { sightings: [recent, old] as Sighting[] } })

    await wrapper.get('select[name="timeline_range"]').setValue('24')
    expect(wrapper.text()).toContain('西南大学北门公交站')
    expect(wrapper.text()).not.toContain('三天前的位置')
  })

  it('renders a real OpenStreetMap and coordinate list when no map key is configured', () => {
    const lostCase = {
      case_id: 1,
      latitude: 29.8269,
      longitude: 106.4253,
      address: '西南大学北门',
    } as LostCase
    const wrapper = mount(CaseMap, {
      props: { lostCase, sightings: [match.sighting], areas: [], mapKey: '' },
    })

    expect(wrapper.find('[data-map-mode="fallback"]').exists()).toBe(true)
    expect(wrapper.get('iframe').attributes('src')).toContain('openstreetmap.org/export/embed.html')
    expect(wrapper.text()).toContain('西南大学北门')
    expect(wrapper.text()).toContain('29.826900')
    expect(wrapper.text()).toContain('西南大学北门公交站')
  })
})
