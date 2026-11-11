<script setup lang="ts">
import { Check, Refresh } from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'

import { fetchNotifications, markAllNotificationsRead, markNotificationRead } from '@/api/notifications'
import NotificationList from '@/components/notifications/NotificationList.vue'
import type { AppNotification } from '@/types/domain'

const items = ref<AppNotification[]>([]); const unreadCount = ref(0); const unreadOnly = ref(false); const loading = ref(true); const failed = ref(false); const busyId = ref<number | null>(null); const markingAll = ref(false)
async function load() { loading.value = true; failed.value = false; try { const data = await fetchNotifications(unreadOnly.value); items.value = data.items; unreadCount.value = data.unreadCount } catch { failed.value = true } finally { loading.value = false } }
async function read(item: AppNotification) { busyId.value = item.notification_id; try { const updated = await markNotificationRead(item.notification_id); items.value = items.value.map((value) => value.notification_id === updated.notification_id ? updated : value); unreadCount.value = Math.max(0, unreadCount.value - 1); if (unreadOnly.value) items.value = items.value.filter((value) => !value.is_read) } finally { busyId.value = null } }
async function readAll() { markingAll.value = true; try { await markAllNotificationsRead(); await load() } finally { markingAll.value = false } }
onMounted(load)
</script>

<template><main class="notifications-page workflow-page"><div class="pf-container"><div class="workflow-heading notifications-heading"><div><span class="workflow-heading__eyebrow">NOTIFICATION CENTER</span><h1>消息中心 <em v-if="unreadCount">{{ unreadCount }}</em></h1><p>匹配进展、任务状态与系统提醒集中在这里。</p></div><div><el-button :icon="Refresh" @click="load">刷新</el-button><el-button type="primary" :icon="Check" :loading="markingAll" :disabled="!unreadCount" @click="readAll">全部已读</el-button></div></div><div class="notification-toolbar pf-card"><label><input v-model="unreadOnly" type="checkbox" @change="load" /> 只看未读</label><span>共 {{ items.length }} 条当前筛选结果</span></div><div v-if="loading" class="notification-loading pf-card"><el-skeleton animated :rows="8" /></div><div v-else-if="failed" class="notification-loading pf-card"><p>消息加载失败，请稍后重试。</p><el-button @click="load">重新加载</el-button></div><NotificationList v-else :items="items" :busy-id="busyId" @read="read" /></div></main></template>

<style scoped>
.notifications-heading { align-items: center; }.notifications-heading h1 { display: flex; align-items: center; gap: 8px; }.notifications-heading h1 em { display: grid; width: 29px; height: 29px; place-items: center; border-radius: 50%; color: #fff; background: var(--pf-color-primary); font-size: 11px; font-style: normal; }.notifications-heading > div:last-child { display: flex; gap: 7px; }.notification-toolbar { display: flex; justify-content: space-between; margin-bottom: 14px; padding: 13px 17px; color: var(--pf-color-text-secondary); font-size: 10px; }.notification-toolbar label { display: flex; align-items: center; gap: 6px; font-weight: 700; }.notification-toolbar input { accent-color: var(--pf-color-primary); }.notification-loading { padding: 25px; text-align: center; }.notification-loading p { color: var(--pf-color-text-secondary); font-size: 11px; }
@media (max-width: 600px) { .notifications-heading { align-items: flex-start; }.notifications-heading > div:last-child { width: 100%; }.notifications-heading :deep(.el-button) { flex: 1; margin-left: 0; } }
</style>
