<script setup lang="ts">
import axios from 'axios'
import { Check, CirclePlus, Refresh, Search } from '@element-plus/icons-vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchCase } from '@/api/cases'
import {
  claimSearchTask,
  confirmReunion,
  createSearchArea,
  fetchSearchAreas,
  fetchSearchTasks,
  releaseSearchTask,
  updateSearchTask,
} from '@/api/collaboration'
import CaseMap from '@/components/maps/CaseMap.vue'
import SearchTaskPanel from '@/components/search/SearchTaskPanel.vue'
import { useAuthStore } from '@/stores/auth'
import type { LostCase, SearchArea, SearchTask } from '@/types/domain'
import { toLocalDateTimePayload } from '@/utils/format'

const route = useRoute()
const auth = useAuthStore()
const lostCase = ref<LostCase | null>(null)
const areas = ref<SearchArea[]>([])
const tasks = ref<SearchTask[]>([])
const loading = ref(true)
const failed = ref(false)
const submittingArea = ref(false)
const submittingReunion = ref(false)
const busyTaskId = ref<number | null>(null)
const taskError = ref('')
const formError = ref('')
const showAreaForm = ref(false)
const showReunionForm = ref(false)
const mapKey = import.meta.env.VITE_AMAP_JS_KEY || ''
const caseId = computed(() => Number(route.params.caseId) || null)
const isOwner = computed(() => Boolean(auth.user && lostCase.value && (
  lostCase.value.publisher_id === auth.user.user_id || lostCase.value.pet.owner_id === auth.user.user_id
)))
const title = computed(() => lostCase.value ? `“${lostCase.value.pet.name}”的协作搜寻` : '附近搜寻任务')

const areaForm = reactive({ area_name: '', center_latitude: 30.2741, center_longitude: 120.1551, radius_meters: 500, description: '' })
const reunionForm = reactive({
  reunion_time: new Date(Date.now() - 60_000).toISOString().slice(0, 16),
  address: '',
  latitude: null as number | null,
  longitude: null as number | null,
  method: '',
  note: '',
})

function apiMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError<{ message?: string }>(error)) return error.response?.data?.message || fallback
  return fallback
}

function tasksFromAreas(items: SearchArea[]): SearchTask[] {
  return items.flatMap((area) => area.task ? [{ ...area.task, area }] : [])
}

async function load() {
  loading.value = true
  failed.value = false
  taskError.value = ''
  try {
    if (caseId.value) {
      const [caseData, areaData] = await Promise.all([fetchCase(caseId.value), fetchSearchAreas(caseId.value)])
      lostCase.value = caseData
      areas.value = areaData
      tasks.value = tasksFromAreas(areaData)
      areaForm.center_latitude = caseData.latitude
      areaForm.center_longitude = caseData.longitude
      reunionForm.address = caseData.address
      reunionForm.latitude = caseData.latitude
      reunionForm.longitude = caseData.longitude
    } else {
      const taskData = await fetchSearchTasks('all')
      tasks.value = taskData
      const seen = new Set<number>()
      areas.value = taskData.flatMap((task) => {
        if (!task.area || seen.has(task.area.area_id)) return []
        seen.add(task.area.area_id)
        return [task.area]
      })
    }
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

async function addArea() {
  if (!caseId.value || !areaForm.area_name.trim()) return
  submittingArea.value = true
  formError.value = ''
  try {
    const area = await createSearchArea(caseId.value, {
      area_name: areaForm.area_name.trim(),
      center_latitude: Number(areaForm.center_latitude),
      center_longitude: Number(areaForm.center_longitude),
      radius_meters: Number(areaForm.radius_meters),
      description: areaForm.description.trim() || null,
    })
    areas.value.push(area)
    tasks.value = tasksFromAreas(areas.value)
    areaForm.area_name = ''
    areaForm.description = ''
    showAreaForm.value = false
  } catch (error) {
    formError.value = apiMessage(error, '搜寻区域创建失败')
  } finally {
    submittingArea.value = false
  }
}

async function refreshCaseTasks() {
  if (!caseId.value) {
    await load()
    return
  }
  areas.value = await fetchSearchAreas(caseId.value)
  tasks.value = tasksFromAreas(areas.value)
}

async function claim(task: SearchTask) {
  busyTaskId.value = task.task_id
  taskError.value = ''
  try {
    await claimSearchTask(task.task_id)
    await refreshCaseTasks()
  } catch (error) {
    taskError.value = apiMessage(error, '任务认领失败，可能已被其他志愿者抢先认领')
  } finally {
    busyTaskId.value = null
  }
}

async function release(task: SearchTask) {
  busyTaskId.value = task.task_id
  taskError.value = ''
  try {
    await releaseSearchTask(task.task_id)
    await refreshCaseTasks()
  } catch (error) {
    taskError.value = apiMessage(error, '任务释放失败')
  } finally {
    busyTaskId.value = null
  }
}

async function update(task: SearchTask, status: 'IN_PROGRESS' | 'COMPLETED', report: string | null) {
  busyTaskId.value = task.task_id
  taskError.value = ''
  try {
    await updateSearchTask(task.task_id, status, report)
    await refreshCaseTasks()
  } catch (error) {
    taskError.value = apiMessage(error, '任务进度更新失败')
  } finally {
    busyTaskId.value = null
  }
}

async function reunite() {
  if (!caseId.value || !reunionForm.address.trim()) return
  submittingReunion.value = true
  formError.value = ''
  try {
    await confirmReunion(caseId.value, {
      finder_id: null,
      reunion_time: toLocalDateTimePayload(reunionForm.reunion_time),
      latitude: reunionForm.latitude,
      longitude: reunionForm.longitude,
      address: reunionForm.address.trim(),
      method: reunionForm.method.trim() || null,
      note: reunionForm.note.trim() || null,
    })
    await load()
    showReunionForm.value = false
  } catch (error) {
    formError.value = apiMessage(error, '寻回确认失败')
  } finally {
    submittingReunion.value = false
  }
}

onMounted(load)
</script>

<template>
  <main class="search-page workflow-page">
    <div class="pf-container">
      <div class="workflow-heading search-heading">
        <div><span class="workflow-heading__eyebrow">COLLABORATIVE SEARCH</span><h1>{{ title }}</h1><p>将行动拆成明确区域，由志愿者认领、反馈并完成闭环。</p></div>
        <div class="search-heading__actions">
          <el-button :icon="Refresh" @click="load">刷新</el-button>
          <el-button v-if="isOwner && lostCase?.status === 'SEARCHING'" :icon="CirclePlus" @click="showAreaForm = !showAreaForm">规划区域</el-button>
          <el-button v-if="isOwner && lostCase?.status === 'SEARCHING'" type="primary" :icon="Check" @click="showReunionForm = !showReunionForm">确认寻回</el-button>
        </div>
      </div>

      <div v-if="loading" class="search-loading pf-card"><el-skeleton animated :rows="10" /></div>
      <div v-else-if="failed" class="search-failed pf-card"><h2>协作任务加载失败</h2><p>请确认服务已启动，然后重新加载。</p><el-button type="primary" @click="load">重新加载</el-button></div>
      <template v-else>
        <form v-if="showAreaForm" class="search-inline-form pf-card" @submit.prevent="addArea">
          <div class="search-inline-form__head"><div><span>NEW SEARCH AREA</span><h2>创建搜寻区域</h2></div><small>仅事件主人可创建</small></div>
          <div class="field-grid field-grid--three">
            <label class="app-form-field"><span>区域名称 <b>*</b></span><input v-model="areaForm.area_name" class="app-form-control" name="area_name" required placeholder="例如：公园东区" /></label>
            <label class="app-form-field"><span>中心纬度 <b>*</b></span><input v-model.number="areaForm.center_latitude" class="app-form-control" name="center_latitude" type="number" min="-90" max="90" step="0.0000001" required /></label>
            <label class="app-form-field"><span>中心经度 <b>*</b></span><input v-model.number="areaForm.center_longitude" class="app-form-control" name="center_longitude" type="number" min="-180" max="180" step="0.0000001" required /></label>
            <label class="app-form-field"><span>搜寻半径（米） <b>*</b></span><input v-model.number="areaForm.radius_meters" class="app-form-control" name="radius_meters" type="number" min="1" max="20000" required /></label>
            <label class="app-form-field field-span-2"><span>行动说明</span><input v-model="areaForm.description" class="app-form-control" name="area_description" placeholder="建议路线、入口或注意事项" /></label>
          </div>
          <p v-if="formError" class="workflow-form__error">{{ formError }}</p>
          <div class="search-inline-form__actions"><el-button @click="showAreaForm = false">取消</el-button><el-button native-type="submit" type="primary" :loading="submittingArea">创建区域与任务</el-button></div>
        </form>

        <form v-if="showReunionForm" class="search-inline-form search-inline-form--reunion pf-card" @submit.prevent="reunite">
          <div class="search-inline-form__head"><div><span>REUNION TRANSACTION</span><h2>确认宠物已寻回</h2></div><small>提交后将关闭事件和未完成任务</small></div>
          <div class="field-grid field-grid--three">
            <label class="app-form-field"><span>寻回时间 <b>*</b></span><input v-model="reunionForm.reunion_time" class="app-form-control" type="datetime-local" required /></label>
            <label class="app-form-field field-span-2"><span>寻回地点 <b>*</b></span><input v-model="reunionForm.address" class="app-form-control" required /></label>
            <label class="app-form-field"><span>纬度</span><input v-model.number="reunionForm.latitude" class="app-form-control" type="number" min="-90" max="90" step="0.0000001" /></label>
            <label class="app-form-field"><span>经度</span><input v-model.number="reunionForm.longitude" class="app-form-control" type="number" min="-180" max="180" step="0.0000001" /></label>
            <label class="app-form-field"><span>寻回方式</span><input v-model="reunionForm.method" class="app-form-control" placeholder="例如：志愿者发现" /></label>
            <label class="app-form-field field-span-2"><span>补充说明</span><textarea v-model="reunionForm.note" class="app-form-control" /></label>
          </div>
          <p v-if="formError" class="workflow-form__error">{{ formError }}</p>
          <div class="search-inline-form__actions"><el-button @click="showReunionForm = false">取消</el-button><el-button native-type="submit" type="primary" :loading="submittingReunion">确认寻回并归档</el-button></div>
        </form>

        <div class="search-workspace">
          <CaseMap :lost-case="lostCase" :areas="areas" :map-key="mapKey" />
          <section class="search-task-column">
            <div class="search-task-column__head"><div><span>ACTIVE TASKS</span><h2>区域任务</h2></div><b>{{ tasks.length }}</b></div>
            <SearchTaskPanel :tasks="tasks" :current-user-id="auth.user?.user_id" :busy-task-id="busyTaskId" :error-message="taskError" @claim="claim" @release="release" @update="update" />
          </section>
        </div>
        <div class="search-guidance pf-card"><el-icon><Search /></el-icon><div><strong>行动前先确认环境安全</strong><p>建议两人同行，穿着醒目标识，不进入封闭施工区或私人区域。发现疑似宠物时先记录位置和方向。</p></div></div>
      </template>
    </div>
  </main>
</template>

<style scoped>
.search-heading { align-items: center; }
.search-heading__actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 7px; }
.search-loading, .search-failed { padding: 28px; }
.search-failed { text-align: center; }
.search-failed h2 { margin: 0; }
.search-failed p { color: var(--pf-color-text-secondary); font-size: 11px; }
.search-inline-form { margin-bottom: 18px; padding: 22px; }
.search-inline-form--reunion { border-top: 4px solid var(--pf-color-sage); }
.search-inline-form__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 17px; }
.search-inline-form__head span { color: var(--pf-color-primary); font-size: 9px; font-weight: 800; letter-spacing: .12em; }
.search-inline-form__head h2 { margin: 2px 0 0; font-size: 17px; }
.search-inline-form__head small { color: var(--pf-color-text-tertiary); font-size: 9px; }
.search-inline-form__actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 17px; }
.search-workspace { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(340px, .8fr); align-items: start; gap: 18px; }
.search-task-column { min-height: 520px; padding: 18px; border: 1px solid var(--pf-color-border); border-radius: var(--pf-radius-md); background: rgb(255 255 255 / 60%); }
.search-task-column__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 13px; }
.search-task-column__head span { color: var(--pf-color-primary); font-size: 9px; font-weight: 800; letter-spacing: .11em; }
.search-task-column__head h2 { margin: 2px 0 0; font-size: 18px; }
.search-task-column__head b { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 50%; color: var(--pf-color-primary-dark); background: #ffe3d7; font-size: 12px; }
.search-guidance { display: flex; align-items: center; gap: 13px; margin-top: 18px; padding: 17px 20px; }
.search-guidance > .el-icon { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border-radius: 11px; color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); }
.search-guidance strong { font-size: 11px; }
.search-guidance p { margin: 1px 0 0; color: var(--pf-color-text-secondary); font-size: 9px; }
@media (max-width: 900px) { .search-workspace { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .search-heading { align-items: flex-start; } .search-heading__actions { width: 100%; justify-content: stretch; } .search-heading__actions :deep(.el-button) { flex: 1; margin-left: 0; } .search-inline-form__head { align-items: flex-start; flex-direction: column; } }
</style>
