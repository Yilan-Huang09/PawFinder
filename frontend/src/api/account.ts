import apiClient, { type ApiEnvelope } from './client'
import type { UserProfile } from '@/types/domain'

export async function updateProfile(payload: { phone: string | null; email: string | null; avatar_url: string | null }): Promise<UserProfile> {
  const response = await apiClient.patch<ApiEnvelope<UserProfile>>('/users/me', payload)
  return response.data.data
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await apiClient.put('/auth/password', { current_password: currentPassword, new_password: newPassword })
}
