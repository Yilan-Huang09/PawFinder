import apiClient, { type ApiEnvelope } from './client'
import type { LostCase, PaginationMeta } from '@/types/domain'

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
