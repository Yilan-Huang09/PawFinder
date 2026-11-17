<script setup lang="ts">
import { Refresh, Search } from '@element-plus/icons-vue'
import { reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchCases } from '@/api/cases'
import CaseCard from '@/components/cases/CaseCard.vue'
import AppPagination from '@/components/common/AppPagination.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import type { CaseStatus, LostCase, PaginationMeta } from '@/types/domain'

const route = useRoute()
const router = useRouter()
const pageSize = 12
const filters = reactive({
  keyword: '',
  species: '',
  status: 'SEARCHING' as CaseStatus | 'ALL',
})
const cases = ref<LostCase[]>([])
const meta = ref<PaginationMeta>({ page: 1, per_page: pageSize, total: 0, pages: 0 })
const loading = ref(false)
const failed = ref(false)
let requestSequence = 0

function queryString(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

async function loadFromRoute() {
  const sequence = ++requestSequence
  filters.keyword = queryString(route.query.keyword)
  filters.species = queryString(route.query.species).toUpperCase()
  const routeStatus = queryString(route.query.status).toUpperCase()
  filters.status = ['SEARCHING', 'REUNITED', 'CLOSED', 'ALL'].includes(routeStatus)
    ? (routeStatus as CaseStatus | 'ALL')
    : 'SEARCHING'
  const page = Math.max(1, Number.parseInt(queryString(route.query.page) || '1', 10) || 1)

  loading.value = true
  failed.value = false
  try {
    const result = await fetchCases({
      page,
      per_page: pageSize,
      status: filters.status,
      species: filters.species || undefined,
      keyword: filters.keyword || undefined,
    })
    if (sequence !== requestSequence) return
    cases.value = result.items
    meta.value = result.meta
  } catch {
    if (sequence !== requestSequence) return
    cases.value = []
    failed.value = true
  } finally {
    if (sequence === requestSequence) loading.value = false
  }
}

async function applyFilters() {
  const query: Record<string, string> = {}
  if (filters.keyword.trim()) query.keyword = filters.keyword.trim()
  if (filters.species) query.species = filters.species
  if (filters.status !== 'SEARCHING') query.status = filters.status
  await router.push({ name: 'cases', query })
}

async function resetFilters() {
  filters.keyword = ''
  filters.species = ''
  filters.status = 'SEARCHING'
  await router.push({ name: 'cases' })
}

async function changePage(page: number) {
  await router.push({
    name: 'cases',
    query: { ...route.query, page: page > 1 ? String(page) : undefined },
  })
}

watch(() => route.query, loadFromRoute, { immediate: true })
</script>

<template>
  <main class="cases-page">
    <section class="cases-hero">
      <div class="pf-container cases-hero__inner">
        <div>
          <span>PUBLIC DISCOVERY</span>
          <h1>附近正在寻找</h1>
          <p>每张卡片都来自一条结构化走失记录。看到相似宠物时，请及时提交独立目击线索。</p>
        </div>
        <div class="cases-hero__signal" aria-hidden="true">
          <span class="signal-ring signal-ring--outer" />
          <span class="signal-ring signal-ring--inner" />
          <span class="signal-pin"><el-icon><Search /></el-icon></span>
        </div>
      </div>
    </section>

    <section class="pf-container cases-content">
      <form class="case-filters pf-card" @submit.prevent="applyFilters">
        <label class="filter-field filter-field--keyword">
          <span>搜索</span>
          <div>
            <el-icon><Search /></el-icon>
            <input v-model="filters.keyword" name="keyword" placeholder="宠物名字或走失地点" />
          </div>
        </label>
        <label class="filter-field">
          <span>宠物类型</span>
          <select v-model="filters.species" name="species">
            <option value="">全部类型</option>
            <option value="DOG">狗狗</option>
            <option value="CAT">猫咪</option>
            <option value="OTHER">其他</option>
          </select>
        </label>
        <label class="filter-field">
          <span>事件状态</span>
          <select v-model="filters.status" name="status">
            <option value="SEARCHING">寻找中</option>
            <option value="REUNITED">已寻回</option>
            <option value="CLOSED">已关闭</option>
            <option value="ALL">全部状态</option>
          </select>
        </label>
        <div class="case-filters__actions">
          <el-button native-type="submit" type="primary" :icon="Search">筛选</el-button>
          <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
        </div>
      </form>

      <div class="cases-toolbar">
        <div>
          <strong>{{ loading ? '正在查询…' : `共 ${meta.total} 条事件` }}</strong>
          <span>公开联系方式已自动脱敏</span>
        </div>
        <RouterLink to="/sightings/new">看到疑似宠物？提交目击 →</RouterLink>
      </div>

      <div v-if="loading" class="cases-grid" aria-label="正在加载">
        <div v-for="item in 8" :key="item" class="list-skeleton pf-card">
          <el-skeleton animated>
            <template #template>
              <el-skeleton-item variant="image" class="list-skeleton__image" />
              <div class="list-skeleton__body">
                <el-skeleton-item variant="h3" style="width: 55%" />
                <el-skeleton-item variant="text" />
                <el-skeleton-item variant="text" style="width: 72%" />
              </div>
            </template>
          </el-skeleton>
        </div>
      </div>
      <div v-else-if="cases.length" class="cases-grid">
        <CaseCard v-for="item in cases" :key="item.case_id" :lost-case="item" />
      </div>
      <EmptyState
        v-else
        :title="failed ? '案例服务暂时不可用' : '没有找到符合条件的事件'"
        :description="failed ? '请确认后端服务已经启动，或稍后再试。' : '尝试减少筛选条件，或查看其他状态。'"
        :action-label="failed ? '重新加载' : '清除筛选'"
        @action="failed ? loadFromRoute() : resetFilters()"
      />

      <AppPagination
        :model-value="meta.page"
        :total="meta.total"
        :page-size="meta.per_page"
        @update:model-value="changePage"
      />
    </section>
  </main>
</template>

<style scoped>
.cases-page { min-height: 100vh; }
.cases-hero { position: relative; overflow: hidden; border-bottom: 1px solid var(--pf-color-border); background: #ece9e2; }
.cases-hero__inner { display: flex; align-items: center; justify-content: space-between; min-height: 275px; gap: 40px; padding-top: 40px; padding-bottom: 58px; }
.cases-hero__inner > div:first-child { position: relative; z-index: 2; }
.cases-hero__inner > div:first-child > span { color: var(--pf-color-primary); font-size: 10px; font-weight: 800; letter-spacing: .16em; }
.cases-hero h1 { margin: 5px 0 8px; font-size: clamp(36px, 4vw, 52px); line-height: 1.2; letter-spacing: -.045em; }
.cases-hero p { max-width: 620px; margin: 0; color: var(--pf-color-text-secondary); font-size: 13px; }
.cases-hero__signal { position: relative; width: 220px; height: 180px; flex: 0 0 auto; }
.signal-ring { position: absolute; top: 50%; left: 50%; border: 1px solid rgb(232 111 71 / 36%); border-radius: 50%; transform: translate(-50%, -50%); }
.signal-ring--outer { width: 205px; height: 205px; }
.signal-ring--inner { width: 125px; height: 125px; background: rgb(255 255 255 / 24%); }
.signal-pin { position: absolute; top: 50%; left: 50%; display: grid; width: 54px; height: 54px; place-items: center; border: 7px solid rgb(255 255 255 / 55%); border-radius: 50%; color: #fff; background: var(--pf-color-primary); font-size: 21px; transform: translate(-50%, -50%); box-shadow: 0 14px 35px rgb(194 75 43 / 24%); }
.cases-content { position: relative; z-index: 3; padding-bottom: 90px; }
.case-filters { display: grid; grid-template-columns: minmax(260px, 1.5fr) 1fr 1fr auto; align-items: end; gap: 14px; margin-top: -32px; padding: 19px; box-shadow: var(--pf-shadow-md); }
.filter-field { display: grid; gap: 6px; min-width: 0; color: var(--pf-color-text-secondary); font-size: 10px; font-weight: 700; }
.filter-field > div, .filter-field select { height: 42px; border: 1px solid var(--pf-color-border); border-radius: 9px; background: #fff; }
.filter-field > div { display: flex; align-items: center; gap: 8px; padding: 0 12px; }
.filter-field > div .el-icon { color: var(--pf-color-primary); }
.filter-field input { min-width: 0; flex: 1; border: 0; outline: 0; background: transparent; font-size: 12px; }
.filter-field select { width: 100%; padding: 0 10px; outline: 0; color: var(--pf-color-text); font-size: 12px; cursor: pointer; }
.filter-field > div:focus-within, .filter-field select:focus { border-color: var(--pf-color-primary); box-shadow: var(--pf-shadow-focus); }
.case-filters__actions { display: flex; gap: 8px; }
.cases-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 34px 2px 18px; }
.cases-toolbar > div { display: grid; }
.cases-toolbar strong { font-size: 15px; }
.cases-toolbar span { color: var(--pf-color-text-tertiary); font-size: 10px; }
.cases-toolbar a { color: var(--pf-color-primary-dark); font-size: 11px; font-weight: 700; }
.cases-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.list-skeleton { overflow: hidden; }
.list-skeleton__image { width: 100% !important; height: 188px !important; border-radius: 0 !important; }
.list-skeleton__body { display: grid; gap: 11px; padding: 18px; }

@media (max-width: 1060px) {
  .case-filters { grid-template-columns: 1.4fr 1fr 1fr; }
  .case-filters__actions { grid-column: 1 / -1; justify-content: flex-end; }
  .cases-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 780px) {
  .cases-hero__signal { display: none; }
  .case-filters { grid-template-columns: 1fr 1fr; }
  .filter-field--keyword { grid-column: 1 / -1; }
  .cases-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 560px) {
  .cases-hero__inner { min-height: 245px; padding-top: 34px; }
  .case-filters { grid-template-columns: 1fr; }
  .filter-field--keyword, .case-filters__actions { grid-column: auto; }
  .case-filters__actions { justify-content: stretch; }
  .case-filters__actions :deep(.el-button) { flex: 1; }
  .cases-toolbar { align-items: flex-start; flex-direction: column; }
  .cases-grid { grid-template-columns: 1fr; }
}
</style>
