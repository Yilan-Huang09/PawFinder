const SPECIES_LABELS: Record<string, string> = {
  DOG: '狗狗',
  CAT: '猫咪',
  BIRD: '鸟类',
  RABBIT: '兔子',
  OTHER: '其他',
}

const STATUS_LABELS: Record<string, string> = {
  SEARCHING: '寻找中',
  REUNITED: '已寻回',
  CLOSED: '已关闭',
}

const BREED_LABELS: Record<string, string> = {
  'Border Collie': '边境牧羊犬',
  'Shiba Inu': '柴犬',
  'Domestic Shorthair': '中华田园猫',
  'Golden Retriever': '金毛寻回犬',
  'British Shorthair': '英国短毛猫',
  'Bichon Frise': '比熊犬',
  'Ragdoll': '布偶猫',
  'Labrador Retriever': '拉布拉多犬',
  'Corgi': '柯基犬',
  'Poodle': '贵宾犬',
  'Siamese': '暹罗猫',
  'Mixed': '混种犬',
  'Unknown': '品种未知',
}

export function speciesLabel(value: string): string {
  return SPECIES_LABELS[value] || value
}

export function caseStatusLabel(value: string): string {
  return STATUS_LABELS[value] || value
}

export function breedLabel(value?: string | null): string {
  if (!value) return '品种未知'
  return BREED_LABELS[value] || value
}

export function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function formatRelativeTime(value: string): string {
  const timestamp = new Date(value).getTime()
  if (Number.isNaN(timestamp)) return formatDateTime(value)
  const minutes = Math.max(0, Math.round((Date.now() - timestamp) / 60_000))
  if (minutes < 60) return `${Math.max(1, minutes)} 分钟前`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.round(hours / 24)
  if (days < 7) return `${days} 天前`
  return formatDateTime(value)
}

export function resolveUploadUrl(path?: string | null): string | null {
  if (!path) return null
  if (/^https?:\/\//i.test(path)) return path
  return `/api/v1/uploads/${path.replace(/^\/+/, '')}`
}
