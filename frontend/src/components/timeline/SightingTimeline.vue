<script setup lang="ts">
import { Clock, Location } from '@element-plus/icons-vue'
import { computed, ref } from 'vue'

import type { Sighting } from '@/types/domain'
import { formatDateTime } from '@/utils/format'

const props = defineProps<{ sightings: Sighting[] }>()
const rangeHours = ref(0)
const filtered = computed(() => {
  if (!rangeHours.value) return props.sightings
  const threshold = Date.now() - rangeHours.value * 3_600_000
  return props.sightings.filter((item) => new Date(item.seen_time).getTime() >= threshold)
})
</script>

<template>
  <section class="sighting-timeline pf-card">
    <div class="sighting-timeline__head">
      <div><span>SIGHTING LOG</span><h2>目击时间线</h2></div>
      <select v-model.number="rangeHours" name="timeline_range" aria-label="筛选时间范围">
        <option :value="0">全部时间</option>
        <option :value="24">最近 24 小时</option>
        <option :value="72">最近 3 天</option>
        <option :value="168">最近 7 天</option>
      </select>
    </div>
    <ol v-if="filtered.length">
      <li v-for="item in filtered" :key="item.sighting_id">
        <span class="sighting-timeline__dot" />
        <div>
          <strong>{{ item.address }}</strong>
          <p><el-icon><Clock /></el-icon>{{ formatDateTime(item.seen_time) }} <el-icon><Location /></el-icon>{{ item.latitude.toFixed(5) }}, {{ item.longitude.toFixed(5) }}</p>
          <p v-if="item.description">{{ item.description }}</p>
        </div>
        <small>可信度 {{ item.confidence }}/5</small>
      </li>
    </ol>
    <p v-else class="sighting-timeline__empty">所选时间范围内暂无目击记录</p>
  </section>
</template>

<style scoped>
.sighting-timeline { padding: 22px; }
.sighting-timeline__head { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-bottom: 18px; }
.sighting-timeline__head span { color: var(--pf-color-primary); font-size: 9px; font-weight: 800; letter-spacing: .12em; }
.sighting-timeline__head h2 { margin: 2px 0 0; font-size: 18px; }
.sighting-timeline select { height: 36px; padding: 0 10px; border: 1px solid var(--pf-color-border); border-radius: 8px; outline: 0; color: var(--pf-color-text-secondary); background: #fff; font-size: 10px; }
.sighting-timeline ol { display: grid; gap: 0; margin: 0; padding: 0; list-style: none; }
.sighting-timeline li { position: relative; display: grid; grid-template-columns: 16px minmax(0, 1fr) auto; gap: 10px; padding: 0 0 22px; }
.sighting-timeline li:not(:last-child)::before { position: absolute; top: 13px; bottom: 0; left: 5px; width: 1px; background: #ebd9cf; content: ''; }
.sighting-timeline__dot { z-index: 1; width: 11px; height: 11px; margin-top: 4px; border: 3px solid #ffe5da; border-radius: 50%; background: var(--pf-color-primary); box-shadow: 0 0 0 3px #fff; }
.sighting-timeline strong { font-size: 12px; }
.sighting-timeline p { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; margin: 3px 0 0; color: var(--pf-color-text-secondary); font-size: 9px; }
.sighting-timeline li > small { color: var(--pf-color-sage-dark); font-size: 9px; }
.sighting-timeline__empty { justify-content: center; padding: 35px 0; color: var(--pf-color-text-tertiary); }
@media (max-width: 520px) { .sighting-timeline__head { align-items: flex-start; flex-direction: column; } .sighting-timeline li { grid-template-columns: 16px 1fr; } .sighting-timeline li > small { grid-column: 2; } }
</style>
