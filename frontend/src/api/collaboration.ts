import apiClient, { type ApiEnvelope } from './client'
import type {
  CaseMatch,
  MatchReviewStatus,
  ReunionRecord,
  SearchArea,
  SearchTask,
} from '@/types/domain'

export interface SearchAreaPayload {
  area_name: string
  center_latitude: number
  center_longitude: number
  radius_meters: number
  description: string | null
}

export interface ReunionPayload {
  finder_id: number | null
  reunion_time: string
  latitude: number | null
  longitude: number | null
  address: string
  method: string | null
  note: string | null
}

export async function fetchMatches(caseId: number): Promise<CaseMatch[]> {
  const response = await apiClient.get<ApiEnvelope<CaseMatch[]>>(`/cases/${caseId}/matches`)
  return response.data.data
}

export async function recalculateMatches(caseId: number): Promise<void> {
  await apiClient.post(`/cases/${caseId}/recalculate`)
}

export async function reviewMatch(matchId: number, reviewStatus: MatchReviewStatus): Promise<CaseMatch> {
  const response = await apiClient.patch<ApiEnvelope<CaseMatch>>(`/matches/${matchId}/review`, {
    review_status: reviewStatus,
  })
  return response.data.data
}

export async function fetchSearchAreas(caseId: number): Promise<SearchArea[]> {
  const response = await apiClient.get<ApiEnvelope<SearchArea[]>>(`/cases/${caseId}/areas`)
  return response.data.data
}

export async function createSearchArea(caseId: number, payload: SearchAreaPayload): Promise<SearchArea> {
  const response = await apiClient.post<ApiEnvelope<SearchArea>>(`/cases/${caseId}/areas`, payload)
  return response.data.data
}

export async function fetchSearchTasks(scope: 'available' | 'mine' | 'all' = 'available'): Promise<SearchTask[]> {
  const response = await apiClient.get<ApiEnvelope<SearchTask[]>>('/tasks', { params: { scope } })
  return response.data.data
}

export async function claimSearchTask(taskId: number): Promise<SearchTask> {
  const response = await apiClient.post<ApiEnvelope<SearchTask>>(`/tasks/${taskId}/claim`)
  return response.data.data
}

export async function releaseSearchTask(taskId: number): Promise<SearchTask> {
  const response = await apiClient.post<ApiEnvelope<SearchTask>>(`/tasks/${taskId}/release`)
  return response.data.data
}

export async function updateSearchTask(
  taskId: number,
  status: 'IN_PROGRESS' | 'COMPLETED',
  report: string | null,
): Promise<SearchTask> {
  const response = await apiClient.patch<ApiEnvelope<SearchTask>>(`/tasks/${taskId}/progress`, {
    status,
    report,
  })
  return response.data.data
}

export async function confirmReunion(caseId: number, payload: ReunionPayload): Promise<ReunionRecord> {
  const response = await apiClient.post<ApiEnvelope<ReunionRecord>>(`/cases/${caseId}/reunion`, payload)
  return response.data.data
}
