<script setup lang="ts">
import { ArrowLeft, Refresh, TrendCharts } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchCase } from '@/api/cases'
import { fetchMatches, recalculateMatches, reviewMatch } from '@/api/collaboration'
import EmptyState from '@/components/common/EmptyState.vue'
import MatchScore from '@/components/matches/MatchScore.vue'
import type { CaseMatch, LostCase, MatchReviewStatus } from '@/types/domain'

const route = useRoute()
const lostCase = ref<LostCase | null>(null)
const matches = ref<CaseMatch[]>([])
const loading = ref(true)
const refreshing = ref(false)
const busyMatchId = ref<number | null>(null)
const failed = ref(false)
const caseId = computed(() => Number(route.params.caseId))
const confirmedCount = computed(() => matches.value.filter((item) => item.review_status === 'CONFIRMED').length)

async function load() {
  loading.value = true
  failed.value = false
  try {
    ;[lostCase.value, matches.value] = await Promise.all([fetchCase(caseId.value), fetchMatches(caseId.value)])
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

async function recalculate() {
  refreshing.value = true
  try {
    await recalculateMatches(caseId.value)
    matches.value = await fetchMatches(caseId.value)
  } finally {
    refreshing.value = false
  }
}

async function review(item: CaseMatch, status: MatchReviewStatus) {
  busyMatchId.value = item.match_id
  try {
    const updated = await reviewMatch(item.match_id, status)
    matches.value = matches.value.map((candidate) => candidate.match_id === updated.match_id ? updated : candidate)
  } finally {
    busyMatchId.value = null
  }
}

onMounted(load)
</script>

<template>
  <main class="matches-page workflow-page">
    <div class="pf-container">
      <RouterLink :to="`/cases/${caseId}`" class="matches-back"><el-icon><ArrowLeft /></el-icon>返回案件详情</RouterLink>
      <div class="workflow-heading matches-heading">
        <div><span class="workflow-heading__eyebrow">EXPLAINABLE MATCHING</span><h1>智能线索匹配</h1><p>每个分数都可解释，最终判断始终由宠物主人完成。</p></div>
        <el-button type="primary" :icon="Refresh" :loading="refreshing" @click="recalculate">重新计算</el-button>
      </div>

      <div v-if="loading" class="matches-grid"><div v-for="item in 3" :key="item" class="pf-card matches-skeleton"><el-skeleton animated :rows="5" /></div></div>
      <EmptyState v-else-if="failed" title="无法读取匹配结果" description="请确认你是该事件的主人，并检查后端服务。" action-label="重新加载" @action="load" />
      <template v-else>
        <section class="matches-overview pf-card">
          <div><el-icon><TrendCharts /></el-icon><span><strong>{{ lostCase?.pet.name }}</strong><small>当前匹配对象</small></span></div>
          <div><strong>{{ matches.length }}</strong><small>候选线索</small></div>
          <div><strong>{{ confirmedCount }}</strong><small>已确认相关</small></div>
          <div><strong>rule-v1</strong><small>算法版本</small></div>
        </section>
        <div v-if="matches.length" class="matches-grid">
          <MatchScore v-for="item in matches" :key="item.match_id" :match="item" :busy="busyMatchId === item.match_id" @review="review(item, $event)" />
        </div>
        <EmptyState v-else title="暂无线索达到候选阈值" description="系统会在新目击提交后自动重新计算，也可以手动触发。" action-label="重新计算" @action="recalculate" />
        <section class="matches-explanation pf-card">
          <div><b>45%</b><span>外观相似</span></div><i>+</i><div><b>30%</b><span>空间距离</span></div><i>+</i><div><b>25%</b><span>时间接近</span></div><i>=</i><div class="matches-explanation__total"><b>综合分</b><span>高分只代表值得优先核实</span></div>
        </section>
      </template>
    </div>
  </main>
</template>

<style scoped>
.matches-back { display: inline-flex; align-items: center; gap: 5px; margin-bottom: 12px; color: var(--pf-color-text-secondary); font-size: 10px; font-weight: 700; }
.matches-heading { align-items: center; }
.matches-overview { display: grid; grid-template-columns: 1.8fr repeat(3, 1fr); align-items: stretch; margin-bottom: 18px; overflow: hidden; }
.matches-overview > div { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 18px; border-right: 1px solid var(--pf-color-border); }
.matches-overview > div:first-child { justify-content: flex-start; }
.matches-overview > div:last-child { border-right: 0; }
.matches-overview .el-icon { display: grid; width: 40px; height: 40px; place-items: center; border-radius: 11px; color: var(--pf-color-primary); background: #ffe5da; font-size: 20px; }
.matches-overview span, .matches-overview > div:not(:first-child) { display: grid; justify-items: center; }
.matches-overview > div:first-child span { justify-items: start; }
.matches-overview strong { font-size: 17px; }
.matches-overview small { color: var(--pf-color-text-tertiary); font-size: 9px; }
.matches-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.matches-skeleton { padding: 20px; }
.matches-explanation { display: flex; align-items: center; justify-content: center; gap: 22px; margin-top: 18px; padding: 21px; }
.matches-explanation div { display: grid; justify-items: center; }
.matches-explanation b { font-size: 16px; }
.matches-explanation span { color: var(--pf-color-text-tertiary); font-size: 9px; }
.matches-explanation i { color: #cfb4a6; font-style: normal; }
.matches-explanation__total { padding-left: 18px; border-left: 1px solid var(--pf-color-border); }
.matches-explanation__total b { color: var(--pf-color-primary-dark); }
@media (max-width: 800px) { .matches-grid { grid-template-columns: 1fr; } .matches-overview { grid-template-columns: repeat(3, 1fr); } .matches-overview > div:first-child { grid-column: 1 / -1; border-right: 0; border-bottom: 1px solid var(--pf-color-border); } }
@media (max-width: 580px) { .matches-explanation { align-items: stretch; flex-direction: column; gap: 8px; } .matches-explanation i { display: none; } .matches-explanation__total { padding: 10px 0 0; border-top: 1px solid var(--pf-color-border); border-left: 0; } }
</style>
