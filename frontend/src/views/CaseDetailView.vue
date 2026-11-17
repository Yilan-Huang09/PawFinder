<script setup lang="ts">
import { ArrowLeft, Check, Location, Phone, Search, Share } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchCase, fetchSightings } from '@/api/cases'
import { fetchSearchAreas } from '@/api/collaboration'
import EmptyState from '@/components/common/EmptyState.vue'
import CaseMap from '@/components/maps/CaseMap.vue'
import SightingTimeline from '@/components/timeline/SightingTimeline.vue'
import { useAuthStore } from '@/stores/auth'
import type { LostCase, SearchArea, Sighting } from '@/types/domain'
import { breedLabel, caseStatusLabel, formatDateTime, resolveUploadUrl, speciesLabel } from '@/utils/format'

const route = useRoute()
const auth = useAuthStore()
const lostCase = ref<LostCase | null>(null)
const sightings = ref<Sighting[]>([])
const areas = ref<SearchArea[]>([])
const loading = ref(true)
const failed = ref(false)
const imageFailed = ref(false)
const mapKey = import.meta.env.VITE_AMAP_JS_KEY || ''
const caseId = computed(() => Number(route.params.caseId))
const isOwner = computed(() => Boolean(auth.user && lostCase.value && (
  lostCase.value.publisher_id === auth.user.user_id || lostCase.value.pet.owner_id === auth.user.user_id
)))
const petPhoto = computed(() => imageFailed.value ? null : resolveUploadUrl(lostCase.value?.pet.cover_photo_url))
const activeTaskCount = computed(() => areas.value.filter((item) => item.task && !['COMPLETED', 'CANCELLED'].includes(item.task.status)).length)

async function load() {
  loading.value = true
  failed.value = false
  try {
    const item = await fetchCase(caseId.value)
    lostCase.value = item
    const [publicSightings, searchAreas] = await Promise.all([
      fetchSightings(item.pet.species),
      fetchSearchAreas(item.case_id),
    ])
    sightings.value = publicSightings
      .filter((sighting) => new Date(sighting.seen_time) >= new Date(item.lost_time))
      .slice(0, 20)
    areas.value = searchAreas
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <main class="case-detail-page">
    <div v-if="loading" class="pf-container case-detail-loading"><el-skeleton animated :rows="10" /></div>
    <EmptyState v-else-if="failed || !lostCase" title="未找到这条走失事件" description="事件可能已被移除，或服务暂时不可用。" action-label="返回公开列表" @action="$router.push('/cases')" />
    <template v-else>
      <section class="case-detail-hero">
        <div class="pf-container case-detail-hero__inner">
          <RouterLink to="/cases" class="case-detail-back"><el-icon><ArrowLeft /></el-icon>返回公开列表</RouterLink>
          <div class="case-detail-hero__grid">
            <div class="case-detail-photo">
              <img v-if="petPhoto" :src="petPhoto" :alt="lostCase.pet.name" @error="imageFailed = true" />
              <span v-else>{{ lostCase.pet.name.slice(0, 1) }}</span>
              <em :class="`case-detail-status--${lostCase.status.toLowerCase()}`">{{ caseStatusLabel(lostCase.status) }}</em>
            </div>
            <div class="case-detail-summary">
              <span>CASE #{{ lostCase.case_id }} · {{ speciesLabel(lostCase.pet.species) }}</span>
              <h1>寻找“{{ lostCase.pet.name }}”</h1>
              <p class="case-detail-lead">{{ lostCase.pet.distinctive_features || lostCase.description || '主人正在等待更多目击线索。' }}</p>
              <div class="case-detail-facts">
                <p><el-icon><Location /></el-icon><span><small>最后出现</small>{{ lostCase.address }}</span></p>
                <p><el-icon><Search /></el-icon><span><small>走失时间</small>{{ formatDateTime(lostCase.lost_time) }}</span></p>
                <p><el-icon><Phone /></el-icon><span><small>联系号码</small>{{ lostCase.contact_phone || '未公开' }}</span></p>
              </div>
              <div class="case-detail-actions">
                <el-button type="primary" size="large" :icon="Share" @click="$router.push({ path: '/sightings/new', query: { case: lostCase.case_id } })">提交目击线索</el-button>
                <el-button v-if="isOwner" size="large" :icon="Check" @click="$router.push(`/cases/${lostCase.case_id}/matches`)">审核智能匹配</el-button>
                <el-button v-if="auth.isAuthenticated" size="large" :icon="Search" @click="$router.push(`/cases/${lostCase.case_id}/search`)">参与协作搜寻</el-button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="pf-container case-detail-content">
        <div class="case-detail-metrics">
          <div><strong>{{ sightings.length }}</strong><span>同类公开目击</span></div>
          <div><strong>{{ areas.length }}</strong><span>规划搜寻区域</span></div>
          <div><strong>{{ activeTaskCount }}</strong><span>进行中任务</span></div>
          <div><strong>{{ breedLabel(lostCase.pet.breed) }}</strong><span>登记品种</span></div>
        </div>
        <div v-if="lostCase.description" class="case-detail-note pf-card"><span>主人补充</span><p>{{ lostCase.description }}</p></div>
        <div class="case-detail-grid">
          <SightingTimeline :sightings="sightings" />
          <CaseMap :lost-case="lostCase" :sightings="sightings" :areas="areas" :map-key="mapKey" />
        </div>
        <div class="case-detail-safety pf-card">
          <div><span>协作提醒</span><h2>请保持安全、客观和可验证</h2></div>
          <p>不要单独进入危险区域；不要公开未脱敏的个人信息；不确定的目击也可以提交，系统会保留独立线索并计算匹配度。</p>
        </div>
      </section>
    </template>
  </main>
</template>

<style scoped>
.case-detail-page { min-height: 100vh; background: var(--pf-color-background); }
.case-detail-loading { padding: 90px 0; }
.case-detail-hero { padding: 30px 0 75px; border-bottom: 1px solid var(--pf-color-border); background: #ece9e2; }
.case-detail-back { display: inline-flex; align-items: center; gap: 5px; margin-bottom: 23px; color: var(--pf-color-text-secondary); font-size: 11px; font-weight: 700; }
.case-detail-hero__grid { display: grid; grid-template-columns: 335px minmax(0, 1fr); align-items: center; gap: 55px; }
.case-detail-photo { position: relative; display: grid; height: 335px; place-items: center; overflow: hidden; border: 1px solid #c9c3b9; border-radius: var(--pf-radius-lg); color: #765548; background: #ead8cc; box-shadow: var(--pf-shadow-md); font-size: 100px; font-weight: 900; }
.case-detail-photo img { width: 100%; height: 100%; object-fit: cover; }
.case-detail-photo em { position: absolute; top: 25px; left: 27px; padding: 6px 11px; border-radius: 99px; color: #fff; background: var(--pf-color-primary); font-size: 10px; font-style: normal; }
.case-detail-photo .case-detail-status--reunited { background: var(--pf-color-success); }
.case-detail-photo .case-detail-status--closed { background: #82756e; }
.case-detail-summary > span { color: var(--pf-color-primary); font-size: 10px; font-weight: 800; letter-spacing: .13em; }
.case-detail-summary h1 { margin: 5px 0 10px; font-size: clamp(38px, 5vw, 60px); line-height: 1.1; letter-spacing: -.05em; }
.case-detail-lead { max-width: 670px; margin: 0; color: var(--pf-color-text-secondary); font-size: 14px; }
.case-detail-facts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 13px; margin: 27px 0; }
.case-detail-facts p { display: flex; align-items: center; gap: 10px; margin: 0; padding: 12px; border: 1px solid rgb(232 193 175 / 75%); border-radius: 10px; background: rgb(255 255 255 / 47%); font-size: 11px; }
.case-detail-facts .el-icon { flex: 0 0 auto; color: var(--pf-color-primary); font-size: 18px; }
.case-detail-facts p span { display: grid; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.case-detail-facts small { color: var(--pf-color-text-tertiary); font-size: 8px; }
.case-detail-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.case-detail-content { position: relative; margin-top: -34px; padding-bottom: 85px; }
.case-detail-metrics { display: grid; grid-template-columns: repeat(4, 1fr); margin-bottom: 20px; overflow: hidden; border: 1px solid var(--pf-color-border); border-radius: var(--pf-radius-md); background: #fff; box-shadow: var(--pf-shadow-md); }
.case-detail-metrics div { display: grid; justify-items: center; padding: 19px; border-right: 1px solid var(--pf-color-border); }
.case-detail-metrics div:last-child { border-right: 0; }
.case-detail-metrics strong { font-size: 20px; }
.case-detail-metrics span { color: var(--pf-color-text-tertiary); font-size: 9px; }
.case-detail-note { margin-bottom: 20px; padding: 19px 22px; }
.case-detail-note span { color: var(--pf-color-primary); font-size: 9px; font-weight: 800; }
.case-detail-note p { margin: 4px 0 0; color: var(--pf-color-text-secondary); font-size: 12px; }
.case-detail-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(390px, .85fr); align-items: start; gap: 20px; }
.case-detail-safety { display: grid; grid-template-columns: 1fr 1.5fr; align-items: center; gap: 35px; margin-top: 20px; padding: 23px 27px; border-left: 4px solid var(--pf-color-sage); }
.case-detail-safety span { color: var(--pf-color-sage-dark); font-size: 9px; font-weight: 800; }
.case-detail-safety h2 { margin: 2px 0 0; font-size: 16px; }
.case-detail-safety p { margin: 0; color: var(--pf-color-text-secondary); font-size: 10px; }
@media (max-width: 900px) { .case-detail-hero__grid { grid-template-columns: 250px 1fr; gap: 30px; } .case-detail-photo { height: 260px; } .case-detail-facts, .case-detail-grid { grid-template-columns: 1fr; } }
@media (max-width: 620px) { .case-detail-hero__grid { grid-template-columns: 1fr; } .case-detail-photo { width: min(100%, 330px); } .case-detail-metrics { grid-template-columns: repeat(2, 1fr); } .case-detail-metrics div:nth-child(2) { border-right: 0; } .case-detail-metrics div:nth-child(-n+2) { border-bottom: 1px solid var(--pf-color-border); } .case-detail-safety { grid-template-columns: 1fr; gap: 10px; } }
</style>
