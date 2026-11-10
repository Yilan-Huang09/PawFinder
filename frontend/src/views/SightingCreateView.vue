<script setup lang="ts">
import { MagicStick, View } from '@element-plus/icons-vue'
import type { AxiosError } from 'axios'
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createSighting, optimizeDescription, uploadSightingPhoto } from '@/api/workflows'
import LocationFields from '@/components/forms/LocationFields.vue'
import PhotoUploader from '@/components/uploads/PhotoUploader.vue'

const router = useRouter()
const photos = ref<File[]>([])
const submitting = ref(false)
const optimizing = ref(false)
const formError = ref('')
const aiNote = ref('')
const form = reactive({
  species: 'DOG', breedGuess: '', primaryColor: '', secondaryColor: '',
  genderGuess: 'UNKNOWN', sizeGuess: 'UNKNOWN', seenTime: '',
  latitude: null as number | null, longitude: null as number | null, address: '',
  direction: '', confidence: 3, description: '',
})

const maxDateTime = computed(() => {
  const now = new Date(); now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

function validate(): string {
  if (!form.species) return '请选择宠物类型'
  if (!form.primaryColor.trim()) return '请填写主要毛色'
  if (!form.seenTime) return '请选择目击时间'
  if (new Date(form.seenTime).getTime() > Date.now()) return '目击时间不能晚于当前时间'
  if (form.latitude === null || form.latitude < -90 || form.latitude > 90) return '纬度范围应为 -90 到 90'
  if (form.longitude === null || form.longitude < -180 || form.longitude > 180) return '经度范围应为 -180 到 180'
  if (form.address.trim().length < 2) return '请填写清楚的位置描述'
  return ''
}

async function runOptimization() {
  if (!form.description.trim()) { formError.value = '请先填写需要优化的描述'; return }
  optimizing.value = true; formError.value = ''
  try {
    const result = await optimizeDescription(form.description.trim())
    form.description = result.text
    aiNote.value = result.source === 'remote' ? '已使用模型服务整理' : '已使用本地规则整理（无需模型密钥）'
  } catch { formError.value = '描述优化暂不可用，你仍可直接提交' } finally { optimizing.value = false }
}

async function submitSighting() {
  formError.value = validate()
  if (formError.value) return
  submitting.value = true
  try {
    const created = await createSighting({
      species: form.species, breed_guess: form.breedGuess.trim() || null,
      primary_color: form.primaryColor.trim().toUpperCase(), secondary_color: form.secondaryColor.trim().toUpperCase() || null,
      gender_guess: form.genderGuess, size_guess: form.sizeGuess,
      seen_time: new Date(form.seenTime).toISOString(), latitude: form.latitude!, longitude: form.longitude!,
      address: form.address.trim(), direction: form.direction.trim() || null,
      confidence: form.confidence, description: form.description.trim() || null,
    })
    for (const photo of photos.value) await uploadSightingPhoto(created.sighting_id, photo)
    await router.push({ path: '/cases', query: { submitted: 'sighting' } })
  } catch (error) {
    const requestError = error as AxiosError<{ message?: string }>
    formError.value = requestError.response?.data?.message || '线索提交失败，请稍后重试'
  } finally { submitting.value = false }
}
</script>

<template>
  <main class="workflow-page">
    <div class="pf-container">
      <header class="workflow-heading"><div><span class="workflow-heading__eyebrow">REPORT A SIGHTING</span><h1>提交目击线索</h1><p>线索无需绑定某个走失事件，系统会自动与所有寻找中宠物匹配。</p></div></header>
      <div class="workflow-layout">
        <form class="workflow-form pf-card" novalidate @submit.prevent="submitSighting">
          <section class="form-section">
            <div class="form-section__heading"><span class="form-section__index">01</span><div><h2>你看到了什么</h2><p>不确定的信息可以选择“未知”</p></div></div>
            <div class="field-grid field-grid--three">
              <label class="app-form-field"><span>宠物类型 <b>*</b></span><select v-model="form.species" name="species" class="app-form-control"><option value="DOG">狗狗</option><option value="CAT">猫咪</option><option value="BIRD">鸟类</option><option value="OTHER">其他</option></select></label>
              <label class="app-form-field"><span>品种猜测</span><input v-model="form.breedGuess" name="breed_guess" class="app-form-control" maxlength="80" placeholder="选填" /></label>
              <label class="app-form-field"><span>主要毛色 <b>*</b></span><input v-model="form.primaryColor" name="primary_color" class="app-form-control" maxlength="50" /></label>
              <label class="app-form-field"><span>次要毛色</span><input v-model="form.secondaryColor" class="app-form-control" maxlength="50" /></label>
              <label class="app-form-field"><span>性别猜测</span><select v-model="form.genderGuess" class="app-form-control"><option value="UNKNOWN">未知</option><option value="MALE">公</option><option value="FEMALE">母</option></select></label>
              <label class="app-form-field"><span>体型</span><select v-model="form.sizeGuess" class="app-form-control"><option value="UNKNOWN">未知</option><option value="SMALL">小型</option><option value="MEDIUM">中型</option><option value="LARGE">大型</option></select></label>
            </div>
          </section>
          <section class="form-section">
            <div class="form-section__heading"><span class="form-section__index">02</span><div><h2>时间与位置</h2><p>这是时空匹配的核心依据</p></div></div>
            <div class="field-grid"><label class="app-form-field"><span>目击时间 <b>*</b></span><input v-model="form.seenTime" name="seen_time" class="app-form-control" type="datetime-local" :max="maxDateTime" /></label><label class="app-form-field"><span>移动方向</span><input v-model="form.direction" name="direction" class="app-form-control" maxlength="80" placeholder="如：向东、进入地库" /></label></div>
            <LocationFields v-model:latitude="form.latitude" v-model:longitude="form.longitude" v-model:address="form.address" class="location-block" />
          </section>
          <section class="form-section">
            <div class="form-section__heading"><span class="form-section__index">03</span><div><h2>照片与补充描述</h2><p>清晰照片能显著提升外观匹配质量</p></div></div>
            <PhotoUploader v-model="photos" :max-files="4" />
            <label class="app-form-field description-field"><span>目击描述</span><textarea v-model="form.description" name="description" class="app-form-control" maxlength="5000" placeholder="描述行为、项圈、明显特征和当时环境…" /></label>
            <div class="ai-row"><el-button data-test="optimize-description" plain :icon="MagicStick" :loading="optimizing" @click="runOptimization">AI 帮我整理描述</el-button><span v-if="aiNote">{{ aiNote }}</span></div>
            <label class="confidence-field"><span><el-icon><View /></el-icon> 目击可信度</span><input v-model.number="form.confidence" name="confidence" type="range" min="1" max="5" /><strong>{{ form.confidence }} / 5</strong></label>
          </section>
          <div class="workflow-form__actions"><p v-if="formError" class="workflow-form__error">{{ formError }}</p><el-button @click="$router.back()">取消</el-button><el-button native-type="submit" type="primary" :loading="submitting">提交线索并自动匹配</el-button></div>
        </form>
        <aside class="workflow-aside"><div class="workflow-tip pf-card"><h3>线索独立发布</h3><p>你不需要判断它属于哪个事件。系统会根据种类、外观、距离和时间自动筛选候选。</p></div><div class="workflow-tip pf-card"><h3>拍照安全</h3><ul><li>不要为了拍照追赶或惊吓动物</li><li>注意交通与陌生环境风险</li><li>无法拍照时文字线索同样有价值</li></ul></div></aside>
      </div>
    </div>
  </main>
</template>

<style scoped>
.location-block, .description-field { margin-top: 15px; }
.ai-row { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
.ai-row span { color: var(--pf-color-sage-dark); font-size: 10px; }
.confidence-field { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 13px; margin-top: 20px; color: var(--pf-color-text-secondary); font-size: 11px; }
.confidence-field > span { display: flex; align-items: center; gap: 5px; }
.confidence-field input { accent-color: var(--pf-color-primary); }
.confidence-field strong { color: var(--pf-color-primary-dark); }
.workflow-form__actions .workflow-form__error { margin-right: auto; }
@media (max-width: 600px) { .ai-row { align-items: flex-start; flex-direction: column; } .confidence-field { grid-template-columns: 1fr auto; } .confidence-field input { grid-column: 1 / -1; grid-row: 2; } }
</style>
