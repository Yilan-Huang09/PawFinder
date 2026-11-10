<script setup lang="ts">
import { MagicStick, Warning } from '@element-plus/icons-vue'
import type { AxiosError } from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchPets } from '@/api/pets'
import { createCase, optimizeDescription } from '@/api/workflows'
import LocationFields from '@/components/forms/LocationFields.vue'
import type { PetSummary } from '@/types/domain'

const router = useRouter()
const pets = ref<PetSummary[]>([])
const loadingPets = ref(true)
const submitting = ref(false)
const optimizing = ref(false)
const formError = ref('')
const aiNote = ref('')
const form = reactive({
  petId: 0,
  lostTime: '',
  latitude: null as number | null,
  longitude: null as number | null,
  address: '',
  description: '',
  contactPhone: '',
})

const maxDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

onMounted(async () => {
  try {
    pets.value = await fetchPets()
    if (pets.value.length === 1) form.petId = pets.value[0]!.pet_id
  } catch {
    formError.value = '宠物档案加载失败，请稍后重试'
  } finally {
    loadingPets.value = false
  }
})

function validate(): string {
  if (!form.petId) return '请选择走失的宠物'
  if (!form.lostTime) return '请选择最后出现时间'
  if (new Date(form.lostTime).getTime() > Date.now()) return '最后出现时间不能晚于当前时间'
  if (form.latitude === null || form.latitude < -90 || form.latitude > 90) return '纬度范围应为 -90 到 90'
  if (form.longitude === null || form.longitude < -180 || form.longitude > 180) return '经度范围应为 -180 到 180'
  if (form.address.trim().length < 2) return '请填写清楚的位置描述'
  if (form.contactPhone && !/^1\d{10}$/.test(form.contactPhone)) return '联系电话格式不正确'
  return ''
}

async function runOptimization() {
  if (!form.description.trim()) {
    formError.value = '请先填写需要优化的描述'
    return
  }
  optimizing.value = true
  formError.value = ''
  try {
    const result = await optimizeDescription(form.description.trim())
    form.description = result.text
    const sourceLabel = result.source === 'remote' ? '模型服务' : '本地规则'
    aiNote.value = `已使用${sourceLabel}优化。${result.suggestions[0] || ''}`
  } catch {
    formError.value = '描述优化暂不可用，你仍可直接提交原描述'
  } finally {
    optimizing.value = false
  }
}

async function submitCase() {
  formError.value = validate()
  if (formError.value) return
  submitting.value = true
  try {
    const created = await createCase({
      pet_id: form.petId,
      lost_time: new Date(form.lostTime).toISOString(),
      latitude: form.latitude!,
      longitude: form.longitude!,
      address: form.address.trim(),
      description: form.description.trim() || null,
      contact_phone: form.contactPhone.trim() || null,
    })
    await router.push(`/cases/${created.case_id}`)
  } catch (error) {
    const requestError = error as AxiosError<{ message?: string }>
    formError.value = requestError.response?.data?.message || '发布失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="workflow-page">
    <div class="pf-container">
      <header class="workflow-heading">
        <div>
          <span class="workflow-heading__eyebrow">REPORT A LOST PET</span>
          <h1>发布走失信息</h1>
          <p>准确的时间、地点和特征会直接提升候选线索质量。</p>
        </div>
        <el-button plain @click="$router.push('/pets')">先管理宠物档案</el-button>
      </header>

      <div class="workflow-layout">
        <form class="workflow-form pf-card" novalidate @submit.prevent="submitCase">
          <section class="form-section">
            <div class="form-section__heading"><span class="form-section__index">01</span><div><h2>选择宠物与时间</h2><p>每只宠物同时只能有一个寻找中的事件</p></div></div>
            <div class="field-grid">
              <label class="app-form-field">
                <span>宠物档案 <b>*</b></span>
                <select v-model.number="form.petId" name="pet_id" class="app-form-control" :disabled="loadingPets">
                  <option :value="0">{{ loadingPets ? '正在加载…' : '请选择宠物' }}</option>
                  <option v-for="pet in pets" :key="pet.pet_id" :value="pet.pet_id">{{ pet.name }} · {{ pet.species === 'DOG' ? '狗狗' : pet.species === 'CAT' ? '猫咪' : pet.species }}</option>
                </select>
              </label>
              <label class="app-form-field">
                <span>最后出现时间 <b>*</b></span>
                <input v-model="form.lostTime" name="lost_time" class="app-form-control" type="datetime-local" :max="maxDateTime" />
              </label>
            </div>
          </section>

          <section class="form-section">
            <div class="form-section__heading"><span class="form-section__index">02</span><div><h2>最后出现位置</h2><p>无地图密钥时也可直接填写坐标</p></div></div>
            <LocationFields v-model:latitude="form.latitude" v-model:longitude="form.longitude" v-model:address="form.address" />
          </section>

          <section class="form-section">
            <div class="form-section__heading"><span class="form-section__index">03</span><div><h2>补充描述与联系信息</h2><p>公开页面会自动隐藏手机号中间四位</p></div></div>
            <div class="field-grid">
              <label class="app-form-field field-span-2">
                <span>走失经过与特征</span>
                <textarea v-model="form.description" name="description" class="app-form-control" maxlength="5000" placeholder="例如：晨间散步时挣脱牵引绳，胸口有白色心形毛，戴红色项圈…" />
              </label>
              <div class="ai-row field-span-2">
                <el-button data-test="optimize-description" plain :icon="MagicStick" :loading="optimizing" @click="runOptimization">AI 帮我整理描述</el-button>
                <span v-if="aiNote">{{ aiNote }}</span>
              </div>
              <label class="app-form-field">
                <span>联系电话</span>
                <input v-model="form.contactPhone" name="contact_phone" class="app-form-control" inputmode="numeric" maxlength="11" placeholder="选填，公开时脱敏" />
              </label>
            </div>
          </section>

          <div class="workflow-form__actions">
            <p v-if="formError" class="workflow-form__error" role="alert">{{ formError }}</p>
            <el-button @click="$router.back()">取消</el-button>
            <el-button native-type="submit" type="primary" :loading="submitting">发布并开始匹配</el-button>
          </div>
        </form>

        <aside class="workflow-aside">
          <div class="workflow-tip pf-card"><h3>没有宠物档案？</h3><p>请先创建宠物档案并上传清晰照片，再发布走失事件。</p><RouterLink to="/pets/new" class="aside-link">创建档案 →</RouterLink></div>
          <div class="workflow-tip pf-card"><h3><el-icon><Warning /></el-icon> 信息安全</h3><ul><li>不要公开身份证或家庭住址</li><li>坐标用于匹配与地图展示</li><li>联系电话默认脱敏</li></ul></div>
        </aside>
      </div>
    </div>
  </main>
</template>

<style scoped>
.ai-row { display: flex; align-items: center; gap: 11px; }
.ai-row span { color: var(--pf-color-sage-dark); font-size: 10px; }
.workflow-form__actions .workflow-form__error { margin-right: auto; }
.aside-link { display: inline-block; margin-top: 10px; color: var(--pf-color-primary-dark); font-size: 11px; font-weight: 700; }
.workflow-tip h3 { display: flex; align-items: center; gap: 6px; }
@media (max-width: 600px) { .ai-row { align-items: flex-start; flex-direction: column; } .workflow-form__actions .workflow-form__error { margin-right: 0; } }
</style>
