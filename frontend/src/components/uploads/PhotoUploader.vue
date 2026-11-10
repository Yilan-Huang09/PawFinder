<script setup lang="ts">
import { Close, Plus, Picture } from '@element-plus/icons-vue'
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: File[]
    maxFiles?: number
    maxBytes?: number
  }>(),
  { maxFiles: 6, maxBytes: 5 * 1024 * 1024 },
)

const emit = defineEmits<{
  'update:modelValue': [files: File[]]
}>()

const input = ref<HTMLInputElement | null>(null)
const message = ref('')
const previews = ref<{ file: File; url: string }[]>([])
const allowedTypes = new Set(['image/jpeg', 'image/png', 'image/webp'])

function rebuildPreviews(files: File[]) {
  previews.value.forEach((item) => URL.revokeObjectURL(item.url))
  previews.value = files.map((file) => ({ file, url: URL.createObjectURL(file) }))
}

watch(() => props.modelValue, rebuildPreviews, { immediate: true })
onBeforeUnmount(() => previews.value.forEach((item) => URL.revokeObjectURL(item.url)))

const remaining = computed(() => Math.max(0, props.maxFiles - props.modelValue.length))

function selectFiles(event: Event) {
  message.value = ''
  const selected = Array.from((event.target as HTMLInputElement).files || [])
  const valid: File[] = []
  for (const file of selected) {
    if (!allowedTypes.has(file.type)) {
      message.value = '仅支持 JPG、PNG 和 WebP 图片'
      continue
    }
    if (file.size > props.maxBytes) {
      message.value = '单张图片不能超过 5 MB'
      continue
    }
    valid.push(file)
  }
  const next = [...props.modelValue, ...valid].slice(0, props.maxFiles)
  if (props.modelValue.length + valid.length > props.maxFiles) {
    message.value = `最多选择 ${props.maxFiles} 张图片`
  }
  emit('update:modelValue', next)
  if (input.value) input.value.value = ''
}

function removeFile(index: number) {
  emit('update:modelValue', props.modelValue.filter((_, itemIndex) => itemIndex !== index))
}
</script>

<template>
  <div class="photo-uploader">
    <div class="photo-uploader__grid">
      <figure v-for="(item, index) in previews" :key="`${item.file.name}-${index}`">
        <img :src="item.url" :alt="item.file.name" />
        <figcaption>{{ item.file.name }}</figcaption>
        <button type="button" :aria-label="`移除 ${item.file.name}`" @click="removeFile(index)">
          <el-icon><Close /></el-icon>
        </button>
      </figure>
      <button
        v-if="remaining > 0"
        type="button"
        class="photo-uploader__add"
        @click="input?.click()"
      >
        <el-icon :size="24"><Plus /></el-icon>
        <strong>添加照片</strong>
        <small>还可选择 {{ remaining }} 张</small>
      </button>
    </div>
    <input
      ref="input"
      class="photo-uploader__input"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      multiple
      @change="selectFiles"
    />
    <p class="photo-uploader__hint"><el-icon><Picture /></el-icon> JPG / PNG / WebP，单张不超过 5 MB</p>
    <p v-if="message" class="photo-uploader__error" role="alert">{{ message }}</p>
  </div>
</template>

<style scoped>
.photo-uploader__grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 11px; }
.photo-uploader figure, .photo-uploader__add { position: relative; height: 128px; margin: 0; overflow: hidden; border: 1px solid var(--pf-color-border); border-radius: 11px; background: var(--pf-color-surface-warm); }
.photo-uploader figure img { width: 100%; height: 100%; object-fit: cover; }
.photo-uploader figcaption { position: absolute; right: 0; bottom: 0; left: 0; overflow: hidden; padding: 5px 8px; color: #fff; background: rgb(55 38 31 / 72%); font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.photo-uploader figure button { position: absolute; top: 6px; right: 6px; display: grid; width: 27px; height: 27px; padding: 0; border: 0; place-items: center; border-radius: 50%; color: #fff; background: rgb(55 38 31 / 70%); cursor: pointer; }
.photo-uploader__add { display: grid; align-content: center; justify-items: center; gap: 3px; color: var(--pf-color-primary-dark); border-style: dashed; cursor: pointer; }
.photo-uploader__add strong { font-size: 11px; }
.photo-uploader__add small { color: var(--pf-color-text-tertiary); font-size: 9px; }
.photo-uploader__input { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); }
.photo-uploader__hint, .photo-uploader__error { display: flex; align-items: center; gap: 5px; margin: 8px 0 0; font-size: 10px; }
.photo-uploader__hint { color: var(--pf-color-text-tertiary); }
.photo-uploader__error { color: var(--pf-color-danger); }
@media (max-width: 650px) { .photo-uploader__grid { grid-template-columns: repeat(2, 1fr); } }
</style>
