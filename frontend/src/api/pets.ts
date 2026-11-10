import apiClient, { type ApiEnvelope } from './client'
import type { PetPhoto, PetSummary } from '@/types/domain'

export interface PetPayload {
  name: string
  species: string
  breed: string | null
  primary_color: string
  secondary_color: string | null
  gender: string
  size: string
  birth_date: string | null
  distinctive_features: string | null
}

export async function fetchPets(includeInactive = false): Promise<PetSummary[]> {
  const response = await apiClient.get<ApiEnvelope<PetSummary[]>>('/pets', {
    params: includeInactive ? { include_inactive: 1 } : undefined,
  })
  return response.data.data
}

export async function fetchPet(petId: number): Promise<PetSummary> {
  const response = await apiClient.get<ApiEnvelope<PetSummary>>(`/pets/${petId}`)
  return response.data.data
}

export async function createPet(payload: PetPayload): Promise<PetSummary> {
  const response = await apiClient.post<ApiEnvelope<PetSummary>>('/pets', payload)
  return response.data.data
}

export async function updatePet(petId: number, payload: PetPayload): Promise<PetSummary> {
  const response = await apiClient.patch<ApiEnvelope<PetSummary>>(`/pets/${petId}`, payload)
  return response.data.data
}

export async function deactivatePet(petId: number): Promise<void> {
  await apiClient.delete(`/pets/${petId}`)
}

export async function uploadPetPhoto(petId: number, file: File): Promise<PetPhoto> {
  const form = new FormData()
  form.append('photo', file)
  const response = await apiClient.post<ApiEnvelope<PetPhoto>>(
    `/pets/${petId}/photos`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return response.data.data
}
