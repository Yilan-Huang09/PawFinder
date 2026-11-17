import apiClient, { type ApiEnvelope } from './client'
import type { LostCase, PaginationMeta, Sighting } from '@/types/domain'

export interface CaseQuery {
  page?: number
  per_page?: number
  status?: 'SEARCHING' | 'REUNITED' | 'CLOSED' | 'ALL'
  species?: string
  keyword?: string
}

export async function fetchCases(
  query: CaseQuery,
): Promise<{ items: LostCase[]; meta: PaginationMeta }> {
  const response = await apiClient.get<ApiEnvelope<LostCase[]>>('/cases', {
    params: query,
  })
  return {
    items: response.data.data,
    meta: response.data.meta as unknown as PaginationMeta,
  }
}

export async function fetchCase(caseId: number): Promise<LostCase> {
  const response = await apiClient.get<ApiEnvelope<LostCase>>(`/cases/${caseId}`)
  return response.data.data
}

export async function fetchSightings(species?: string): Promise<Sighting[]> {
  const response = await apiClient.get<ApiEnvelope<Sighting[]>>('/sightings', {
    params: { species, page: 1, per_page: 100 },
  })
  return response.data.data
}
