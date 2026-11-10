<script setup lang="ts">
import { Check, Close, Location, Timer } from '@element-plus/icons-vue'
import { computed } from 'vue'

import type { CaseMatch, MatchReviewStatus } from '@/types/domain'
import { formatDateTime } from '@/utils/format'

const props = defineProps<{ match: CaseMatch; busy?: boolean }>()
const emit = defineEmits<{ review: [status: MatchReviewStatus] }>()

const scoreStyle = computed(() => ({
  background: `conic-gradient(var(--pf-color-primary) ${Math.min(100, props.match.total_score)}%, #f3e4db 0)`,
}))
const statusLabel = computed(() => ({
  PENDING: '待核实',
  CONFIRMED: '已确认',
  REJECTED: '已排除',
}[props.match.review_status]))
</script>

<template>
  <article class="match-score pf-card" :class="`match-score--${match.review_status.toLowerCase()}`">
    <div class="match-score__summary">
      <div class="match-score__ring" :style="scoreStyle"><span><b>{{ match.total_score }}</b><small>综合分</small></span></div>
      <div class="match-score__title">
        <div><span>候选线索 #{{ match.sighting_id }}</span><em>{{ statusLabel }}</em></div>
        <h3>{{ match.sighting.address }}</h3>
        <p><el-icon><Location /></el-icon>{{ match.distance_km.toFixed(2) }} km · <el-icon><Timer /></el-icon>{{ formatDateTime(match.sighting.seen_time) }}</p>
      </div>
    </div>
    <div class="match-score__breakdown">
      <div><span>外观 {{ match.appearance_score }}</span><i><b :style="{ width: `${match.appearance_score}%` }" /></i></div>
      <div><span>距离 {{ match.distance_score }}</span><i><b :style="{ width: `${match.distance_score}%` }" /></i></div>
      <div><span>时间 {{ match.time_score }}</span><i><b :style="{ width: `${match.time_score}%` }" /></i></div>
    </div>
    <p class="match-score__reason">{{ match.match_reason }}</p>
    <div v-if="match.review_status === 'PENDING'" class="match-score__actions">
      <el-button data-test="reject-match" :icon="Close" :disabled="busy" @click="emit('review', 'REJECTED')">排除线索</el-button>
      <el-button data-test="confirm-match" type="primary" :icon="Check" :loading="busy" @click="emit('review', 'CONFIRMED')">确认相关</el-button>
    </div>
  </article>
</template>

<style scoped>
.match-score { padding: 20px; transition: border-color 160ms ease, transform 160ms ease; }
.match-score:hover { border-color: #ecc8b8; transform: translateY(-2px); }
.match-score--confirmed { border-color: #b9d4bf; }
.match-score--rejected { opacity: .67; }
.match-score__summary { display: flex; align-items: center; gap: 15px; }
.match-score__ring { display: grid; width: 78px; height: 78px; flex: 0 0 auto; padding: 7px; place-items: center; border-radius: 50%; }
.match-score__ring > span { display: grid; width: 100%; height: 100%; place-content: center; justify-items: center; border-radius: 50%; background: #fff; line-height: 1.1; }
.match-score__ring b { font-size: 20px; }
.match-score__ring small { margin-top: 4px; color: var(--pf-color-text-tertiary); font-size: 8px; }
.match-score__title { min-width: 0; flex: 1; }
.match-score__title > div { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.match-score__title span { color: var(--pf-color-primary); font-size: 9px; font-weight: 800; letter-spacing: .08em; }
.match-score__title em { padding: 3px 7px; border-radius: 999px; color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); font-size: 9px; font-style: normal; }
.match-score__title h3 { margin: 4px 0 3px; overflow: hidden; font-size: 15px; text-overflow: ellipsis; white-space: nowrap; }
.match-score__title p { display: flex; align-items: center; gap: 4px; margin: 0; color: var(--pf-color-text-tertiary); font-size: 9px; }
.match-score__breakdown { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 17px 0 13px; }
.match-score__breakdown > div { display: grid; gap: 5px; }
.match-score__breakdown span { color: var(--pf-color-text-secondary); font-size: 9px; font-weight: 700; }
.match-score__breakdown i { height: 5px; overflow: hidden; border-radius: 99px; background: #f3e4db; }
.match-score__breakdown b { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--pf-color-primary), #f0a177); }
.match-score__reason { margin: 0; padding: 10px 11px; border-radius: 8px; color: var(--pf-color-text-secondary); background: var(--pf-color-surface-warm); font-size: 10px; }
.match-score__actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 14px; }
@media (max-width: 460px) { .match-score__breakdown { grid-template-columns: 1fr; } .match-score__actions { align-items: stretch; flex-direction: column; } }
</style>
