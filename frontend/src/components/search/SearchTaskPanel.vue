<script setup lang="ts">
import { Check, Close, Flag, User } from '@element-plus/icons-vue'
import { reactive } from 'vue'

import type { SearchTask } from '@/types/domain'

defineProps<{ tasks: SearchTask[]; currentUserId?: number | null; busyTaskId?: number | null; errorMessage?: string }>()
const emit = defineEmits<{
  claim: [task: SearchTask]
  release: [task: SearchTask]
  update: [task: SearchTask, status: 'IN_PROGRESS' | 'COMPLETED', report: string | null]
}>()
const reports = reactive<Record<number, string>>({})

function statusLabel(status: SearchTask['status']) {
  return { AVAILABLE: '待认领', CLAIMED: '已认领', IN_PROGRESS: '搜寻中', COMPLETED: '已完成', CANCELLED: '已取消' }[status]
}
</script>

<template>
  <section class="task-panel">
    <p v-if="errorMessage" class="task-panel__error" role="alert">{{ errorMessage }}</p>
    <div v-if="tasks.length" class="task-panel__list">
      <article v-for="task in tasks" :key="task.task_id" class="task-card pf-card">
        <header>
          <span><el-icon><Flag /></el-icon>{{ task.area?.area_name || `搜寻区域 #${task.area_id}` }}</span>
          <em :class="`task-card__status--${task.status.toLowerCase()}`">{{ statusLabel(task.status) }}</em>
        </header>
        <p v-if="task.area?.description">{{ task.area.description }}</p>
        <div class="task-card__meta">
          <span>半径 {{ task.area?.radius_meters || '—' }} m</span>
          <span v-if="task.volunteer_id"><el-icon><User /></el-icon>志愿者 #{{ task.volunteer_id }}</span>
        </div>
        <template v-if="task.volunteer_id === currentUserId && ['CLAIMED', 'IN_PROGRESS'].includes(task.status)">
          <textarea v-model="reports[task.task_id]" :name="`task_report_${task.task_id}`" placeholder="记录巡查路线、时间和发现（完成时必填）" />
          <div class="task-card__actions">
            <el-button :icon="Close" :disabled="busyTaskId === task.task_id" @click="emit('release', task)">释放</el-button>
            <el-button v-if="task.status === 'CLAIMED'" :data-test="`start-task-${task.task_id}`" :loading="busyTaskId === task.task_id" @click="emit('update', task, 'IN_PROGRESS', reports[task.task_id] || null)">开始搜寻</el-button>
            <el-button v-else type="primary" :icon="Check" :data-test="`complete-task-${task.task_id}`" :disabled="!reports[task.task_id]?.trim()" :loading="busyTaskId === task.task_id" @click="emit('update', task, 'COMPLETED', reports[task.task_id].trim())">完成任务</el-button>
          </div>
        </template>
        <div v-else-if="task.status === 'AVAILABLE'" class="task-card__actions">
          <el-button type="primary" :data-test="`claim-task-${task.task_id}`" :loading="busyTaskId === task.task_id" @click="emit('claim', task)">认领此区域</el-button>
        </div>
        <p v-else-if="task.report" class="task-card__report">反馈：{{ task.report }}</p>
      </article>
    </div>
    <p v-else class="task-panel__empty">当前没有可显示的搜寻任务</p>
  </section>
</template>

<style scoped>
.task-panel__error { margin: 0 0 12px; padding: 10px 12px; border: 1px solid #efc7c4; border-radius: 8px; color: var(--pf-color-danger); background: #fff4f3; font-size: 10px; }
.task-panel__list { display: grid; gap: 12px; }
.task-card { padding: 17px; }
.task-card header { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.task-card header > span { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 800; }
.task-card header .el-icon { color: var(--pf-color-primary); }
.task-card em { padding: 3px 7px; border-radius: 999px; color: var(--pf-color-text-secondary); background: #f2e9e3; font-size: 9px; font-style: normal; }
.task-card__status--available { color: var(--pf-color-primary-dark) !important; background: #ffe4d8 !important; }
.task-card__status--in_progress, .task-card__status--completed { color: var(--pf-color-sage-dark) !important; background: var(--pf-color-sage-soft) !important; }
.task-card > p { margin: 9px 0; color: var(--pf-color-text-secondary); font-size: 10px; }
.task-card__meta { display: flex; gap: 13px; color: var(--pf-color-text-tertiary); font-size: 9px; }
.task-card__meta span { display: flex; align-items: center; gap: 4px; }
.task-card textarea { width: 100%; min-height: 70px; margin-top: 12px; padding: 9px 10px; border: 1px solid var(--pf-color-border); border-radius: 8px; outline: 0; font-size: 10px; resize: vertical; }
.task-card textarea:focus { border-color: var(--pf-color-primary); box-shadow: var(--pf-shadow-focus); }
.task-card__actions { display: flex; justify-content: flex-end; gap: 7px; margin-top: 12px; }
.task-card__report { padding: 9px; border-radius: 7px; background: var(--pf-color-surface-warm); }
.task-panel__empty { padding: 45px 15px; text-align: center; color: var(--pf-color-text-tertiary); font-size: 11px; }
</style>
