export type UserRole = 'USER' | 'ADMIN'
export type UserStatus = 'ACTIVE' | 'DISABLED'
export type CaseStatus = 'SEARCHING' | 'REUNITED' | 'CLOSED'

export interface UserProfile {
  user_id: number
  username: string
  phone?: string | null
  email?: string | null
  avatar_url?: string | null
  role: UserRole
  status: UserStatus
  created_at?: string
  updated_at?: string
}

export interface PetSummary {
  pet_id: number
  owner_id: number
  name: string
  species: string
  breed?: string | null
  primary_color: string
  secondary_color?: string | null
  gender: string
  size: string
  birth_date?: string | null
  distinctive_features?: string | null
  status: string
  cover_photo_url?: string | null
  created_at?: string
  updated_at?: string
  photos?: PetPhoto[]
}

export interface PetPhoto {
  photo_id: number
  pet_id: number
  photo_url: string
  is_cover: boolean
  sort_order: number
}

export interface Sighting {
  sighting_id: number
  reporter_id: number
  species: string
  breed_guess?: string | null
  primary_color: string
  secondary_color?: string | null
  gender_guess: string
  size_guess: string
  seen_time: string
  latitude: number
  longitude: number
  address: string
  direction?: string | null
  confidence: number
  description?: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface LostCase {
  case_id: number
  pet_id: number
  publisher_id: number
  lost_time: string
  latitude: number
  longitude: number
  address: string
  description?: string | null
  contact_phone?: string | null
  status: CaseStatus
  closed_at?: string | null
  created_at: string
  updated_at: string
  pet: PetSummary
}

export interface PaginationMeta {
  page: number
  per_page: number
  total: number
  pages: number
}
