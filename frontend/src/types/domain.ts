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
  photos?: Array<{
    photo_id: number
    sighting_id: number
    photo_url: string
    sort_order: number
  }>
}

export type MatchReviewStatus = 'PENDING' | 'CONFIRMED' | 'REJECTED'

export interface CaseMatch {
  match_id: number
  case_id: number
  sighting_id: number
  appearance_score: number
  distance_score: number
  time_score: number
  total_score: number
  distance_km: number
  match_reason: string
  algorithm_version: string
  review_status: MatchReviewStatus
  reviewed_by: number | null
  generated_at: string
  reviewed_at: string | null
  sighting: Sighting
}

export type SearchTaskStatus =
  | 'AVAILABLE'
  | 'CLAIMED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED'

export interface SearchArea {
  area_id: number
  case_id: number
  created_by: number
  area_name: string
  center_latitude: number
  center_longitude: number
  radius_meters: number
  description?: string | null
  status: string
  created_at?: string
  updated_at?: string
  task?: SearchTask | null
}

export interface SearchTask {
  task_id: number
  area_id: number
  volunteer_id: number | null
  status: SearchTaskStatus
  accepted_at: string | null
  started_at: string | null
  completed_at: string | null
  report: string | null
  updated_at: string
  area?: SearchArea
}

export interface ReunionRecord {
  reunion_id: number
  case_id: number
  finder_id: number | null
  confirmed_by: number
  reunion_time: string
  latitude: number | null
  longitude: number | null
  address: string
  method: string | null
  note: string | null
  created_at: string
}

export interface AppNotification {
  notification_id: number
  user_id: number
  type: string
  title: string
  content: string
  related_case_id: number | null
  related_match_id: number | null
  related_task_id: number | null
  is_read: boolean
  created_at: string
  read_at: string | null
}

export interface AdminStatistics {
  users: { total: number; active: number; disabled: number }
  cases: { total: number; searching: number; reunited: number; closed: number }
  sightings: { total: number; active: number; hidden: number; invalid: number }
  matches: { total: number; pending: number; high_score: number }
  tasks: { total: number; available: number; in_progress: number; completed: number }
  reunions: { total: number }
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
