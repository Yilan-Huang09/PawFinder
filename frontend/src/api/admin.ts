import apiClient, { type ApiEnvelope } from './client'
import type { AdminStatistics, LostCase, Sighting, UserProfile } from '@/types/domain'

export async function fetchAdminStatistics(): Promise<AdminStatistics> {
  const response = await apiClient.get<ApiEnvelope<AdminStatistics>>('/admin/statistics')
  return response.data.data
}
export async function fetchAdminUsers(): Promise<UserProfile[]> {
  const response = await apiClient.get<ApiEnvelope<UserProfile[]>>('/admin/users')
  return response.data.data
}
export async function updateAdminUserStatus(userId: number, status: 'ACTIVE' | 'DISABLED'): Promise<UserProfile> {
  const response = await apiClient.patch<ApiEnvelope<UserProfile>>(`/admin/users/${userId}/status`, { status })
  return response.data.data
}
export async function fetchAdminCases(): Promise<LostCase[]> {
  const response = await apiClient.get<ApiEnvelope<LostCase[]>>('/admin/content/cases')
  return response.data.data
}
export async function updateAdminCaseStatus(caseId: number, status: 'SEARCHING' | 'CLOSED'): Promise<LostCase> {
  const response = await apiClient.patch<ApiEnvelope<LostCase>>(`/admin/content/cases/${caseId}/status`, { status })
  return response.data.data
}
export async function fetchAdminSightings(): Promise<Sighting[]> {
  const response = await apiClient.get<ApiEnvelope<Sighting[]>>('/admin/content/sightings')
  return response.data.data
}
export async function updateAdminSightingStatus(sightingId: number, status: 'ACTIVE' | 'HIDDEN' | 'INVALID'): Promise<Sighting> {
  const response = await apiClient.patch<ApiEnvelope<Sighting>>(`/admin/content/sightings/${sightingId}/status`, { status })
  return response.data.data
}
