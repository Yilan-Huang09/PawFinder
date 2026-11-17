<script setup lang="ts">
import { Bell, Check, Location, Message } from '@element-plus/icons-vue'

import type { AppNotification } from '@/types/domain'
import { formatRelativeTime } from '@/utils/format'

defineProps<{ items: AppNotification[]; busyId?: number | null }>()
const emit = defineEmits<{ read: [item: AppNotification] }>()

function iconFor(type: string) {
  if (type.includes('TASK')) return Location
  if (type.includes('MATCH')) return Message
  return Bell
}
</script>

<template>
  <div v-if="items.length" class="notification-list">
    <article v-for="item in items" :key="item.notification_id" class="notification-item pf-card" :class="{ 'notification-item--unread': !item.is_read }">
      <span class="notification-item__icon"><el-icon><component :is="iconFor(item.type)" /></el-icon></span>
      <div><header><h3>{{ item.title }}</h3><time>{{ formatRelativeTime(item.created_at) }}</time></header><p>{{ item.content }}</p><RouterLink v-if="item.related_case_id" :to="`/cases/${item.related_case_id}`">查看关联事件 →</RouterLink></div>
      <el-button v-if="!item.is_read" circle :icon="Check" :loading="busyId === item.notification_id" :data-test="`read-notification-${item.notification_id}`" title="标记已读" @click="emit('read', item)" />
      <span v-else class="notification-item__read">已读</span>
    </article>
  </div>
  <div v-else class="notification-list__empty"><el-icon :size="30"><Bell /></el-icon><strong>暂时没有消息</strong><span>新的匹配、任务状态和寻回进展会出现在这里。</span></div>
</template>

<style scoped>
.notification-list { display: grid; gap: 11px; }
.notification-item { position: relative; display: grid; grid-template-columns: 42px minmax(0, 1fr) auto; align-items: start; gap: 13px; padding: 17px; }
.notification-item--unread { border-left: 4px solid var(--pf-color-primary); background: linear-gradient(90deg, #fff8f4, #fff); }
.notification-item__icon { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 12px; color: var(--pf-color-primary-dark); background: #ffe5db; }
.notification-item header { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.notification-item h3 { margin: 0; font-size: 13px; }
.notification-item time { color: var(--pf-color-text-tertiary); font-size: 9px; }
.notification-item p { margin: 4px 0; color: var(--pf-color-text-secondary); font-size: 10px; }
.notification-item a { color: var(--pf-color-primary-dark); font-size: 9px; font-weight: 700; }
.notification-item__read { padding: 3px 7px; border-radius: 99px; color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); font-size: 8px; }
.notification-list__empty { display: grid; min-height: 280px; place-content: center; justify-items: center; gap: 7px; color: var(--pf-color-text-tertiary); text-align: center; }
.notification-list__empty strong { color: var(--pf-color-text); font-size: 14px; }
.notification-list__empty span { font-size: 10px; }
@media (max-width: 560px) { .notification-item { grid-template-columns: 38px 1fr; } .notification-item > :last-child { grid-column: 2; justify-self: end; } .notification-item header { align-items: flex-start; flex-direction: column; gap: 2px; } }
</style>
