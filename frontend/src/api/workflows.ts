import apiClient, { type ApiEnvelope } from './client'
import type { LostCase, Sighting } from '@/types/domain'

export interface CaseCreatePayload {
  pet_id: number
  lost_time: string
  latitude: number
  longitude: number
  address: string
  description: string | null
  contact_phone: string | null
}

export interface SightingCreatePayload {
  species: string
  breed_guess: string | null
  primary_color: string
  secondary_color: string | null
  gender_guess: string
  size_guess: string
  seen_time: string
  latitude: number
  longitude: number
  address: string
  direction: string | null
  confidence: number
  description: string | null
}

export interface DescriptionOptimization {
  text: string
  suggestions: string[]
  source: 'local' | 'remote' | 'local_fallback'
}

export async function createCase(payload: CaseCreatePayload): Promise<LostCase> {
  const response = await apiClient.post<ApiEnvelope<LostCase>>('/cases', payload)
  return response.data.data
}

export async function createSighting(payload: SightingCreatePayload): Promise<Sighting> {
  const response = await apiClient.post<ApiEnvelope<Sighting>>('/sightings', payload)
  return response.data.data
}

export async function uploadSightingPhoto(sightingId: number, file: File): Promise<void> {
  const form = new FormData()
  form.append('photo', file)
  await apiClient.post(`/sightings/${sightingId}/photos`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export async function optimizeDescription(text: string): Promise<DescriptionOptimization> {
  const response = await apiClient.post<ApiEnvelope<DescriptionOptimization>>(
    '/ai/optimize-description',
    { text },
  )
  return response.data.data
}
