<script setup lang="ts">
import type { AxiosError } from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { createPet, fetchPet, updatePet, uploadPetPhoto } from '@/api/pets'
import PhotoUploader from '@/components/uploads/PhotoUploader.vue'

const route = useRoute()
const router = useRouter()
const petId = computed(() => Number(route.params.petId || 0))
const editing = computed(() => petId.value > 0)
const loading = ref(editing.value)
const submitting = ref(false)
const formError = ref('')
const photos = ref<File[]>([])
const existingPhotoCount = ref(0)
const form = reactive({
  name: '', species: 'DOG', breed: '', primaryColor: '', secondaryColor: '',
  gender: 'UNKNOWN', size: 'UNKNOWN', birthDate: '', distinctiveFeatures: '',
})

onMounted(async () => {
  if (!editing.value) return
  try {
    const pet = await fetchPet(petId.value)
    Object.assign(form, {
      name: pet.name, species: pet.species, breed: pet.breed || '', primaryColor: pet.primary_color,
      secondaryColor: pet.secondary_color || '', gender: pet.gender, size: pet.size,
      birthDate: pet.birth_date || '', distinctiveFeatures: pet.distinctive_features || '',
    })
    existingPhotoCount.value = pet.photos?.length || 0
  } catch { formError.value = '宠物档案加载失败' } finally { loading.value = false }
})

function validate(): string {
  if (!form.name.trim()) return '请填写宠物名字'
  if (!form.species) return '请选择宠物类型'
  if (!form.primaryColor.trim()) return '请填写主要毛色'
  if (form.birthDate && new Date(form.birthDate).getTime() > Date.now()) return '出生日期不能晚于今天'
  return ''
}

async function submitPet() {
  formError.value = validate()
  if (formError.value) return
  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(), species: form.species, breed: form.breed.trim() || null,
      primary_color: form.primaryColor.trim().toUpperCase(), secondary_color: form.secondaryColor.trim().toUpperCase() || null,
      gender: form.gender, size: form.size, birth_date: form.birthDate || null,
      distinctive_features: form.distinctiveFeatures.trim() || null,
    }
    const pet = editing.value ? await updatePet(petId.value, payload) : await createPet(payload)
    for (const photo of photos.value) await uploadPetPhoto(pet.pet_id, photo)
    await router.push('/pets')
  } catch (error) {
    const requestError = error as AxiosError<{ message?: string }>
    formError.value = requestError.response?.data?.message || '保存失败，请稍后重试'
  } finally { submitting.value = false }
}
</script>

<template>
  <main class="workflow-page">
    <div class="pf-container">
      <header class="workflow-heading"><div><span class="workflow-heading__eyebrow">PET PROFILE</span><h1>{{ editing ? '编辑宠物档案' : '创建宠物档案' }}</h1><p>用稳定、不会轻易变化的特征帮助后续辨认。</p></div></header>
      <div class="workflow-layout">
        <form class="workflow-form pf-card" novalidate @submit.prevent="submitPet">
          <section v-if="loading" class="form-section"><el-skeleton animated :rows="8" /></section>
          <template v-else>
            <section class="form-section">
              <div class="form-section__heading"><span class="form-section__index">01</span><div><h2>基础信息</h2><p>名字、类型和毛色为必填项</p></div></div>
              <div class="field-grid field-grid--three">
                <label class="app-form-field"><span>名字 <b>*</b></span><input v-model="form.name" name="name" class="app-form-control" maxlength="80" /></label>
                <label class="app-form-field"><span>类型 <b>*</b></span><select v-model="form.species" name="species" class="app-form-control"><option value="DOG">狗狗</option><option value="CAT">猫咪</option><option value="BIRD">鸟类</option><option value="OTHER">其他</option></select></label>
                <label class="app-form-field"><span>品种</span><input v-model="form.breed" name="breed" class="app-form-control" maxlength="80" placeholder="选填" /></label>
                <label class="app-form-field"><span>主要毛色 <b>*</b></span><input v-model="form.primaryColor" name="primary_color" class="app-form-control" maxlength="50" placeholder="如 BLACK / 黑色" /></label>
                <label class="app-form-field"><span>次要毛色</span><input v-model="form.secondaryColor" class="app-form-control" maxlength="50" placeholder="选填" /></label>
                <label class="app-form-field"><span>出生日期</span><input v-model="form.birthDate" class="app-form-control" type="date" /></label>
                <label class="app-form-field"><span>性别</span><select v-model="form.gender" class="app-form-control"><option value="UNKNOWN">未知</option><option value="MALE">公</option><option value="FEMALE">母</option></select></label>
                <label class="app-form-field"><span>体型</span><select v-model="form.size" class="app-form-control"><option value="UNKNOWN">未知</option><option value="SMALL">小型</option><option value="MEDIUM">中型</option><option value="LARGE">大型</option></select></label>
              </div>
            </section>
            <section class="form-section">
              <div class="form-section__heading"><span class="form-section__index">02</span><div><h2>明显特征</h2><p>优先填写耳朵、尾巴、伤疤和固定配饰</p></div></div>
              <label class="app-form-field"><span>特征描述</span><textarea v-model="form.distinctiveFeatures" name="distinctive_features" class="app-form-control" maxlength="2000" placeholder="例如：左耳有小缺口，胸口有白色心形毛…" /></label>
            </section>
            <section class="form-section">
              <div class="form-section__heading"><span class="form-section__index">03</span><div><h2>清晰照片</h2><p>第一张新照片会在无现有照片时自动成为封面</p></div></div>
              <PhotoUploader v-model="photos" :max-files="Math.max(0, 6 - existingPhotoCount)" />
            </section>
          </template>
          <div class="workflow-form__actions"><p v-if="formError" class="workflow-form__error">{{ formError }}</p><el-button @click="$router.back()">取消</el-button><el-button native-type="submit" type="primary" :loading="submitting">保存档案</el-button></div>
        </form>
        <aside class="workflow-aside"><div class="workflow-tip pf-card"><h3>照片建议</h3><ul><li>至少一张正面全身照</li><li>再补充侧面与明显特征</li><li>避免强滤镜和复杂背景</li></ul></div><div class="workflow-tip pf-card"><h3>为什么先建档？</h3><p>走失发生后情绪紧张，预先保存资料可在几分钟内完成发布。</p></div></aside>
      </div>
    </div>
  </main>
</template>

<style scoped>.workflow-form__actions .workflow-form__error { margin-right: auto; }</style>
