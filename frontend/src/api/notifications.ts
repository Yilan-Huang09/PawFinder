import apiClient, { type ApiEnvelope } from './client'
import type { AppNotification } from '@/types/domain'

export async function fetchNotifications(unreadOnly = false): Promise<{ items: AppNotification[]; unreadCount: number }> {
  const response = await apiClient.get<ApiEnvelope<AppNotification[]>>('/notifications', { params: { unread_only: unreadOnly } })
  return { items: response.data.data, unreadCount: Number(response.data.meta?.unread_count || 0) }
}

export async function markNotificationRead(notificationId: number): Promise<AppNotification> {
  const response = await apiClient.patch<ApiEnvelope<AppNotification>>(`/notifications/${notificationId}/read`)
  return response.data.data
}

export async function markAllNotificationsRead(): Promise<number> {
  const response = await apiClient.patch<ApiEnvelope<{ updated_count: number }>>('/notifications/read-all')
  return response.data.data.updated_count
}
