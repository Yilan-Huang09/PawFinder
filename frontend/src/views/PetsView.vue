<script setup lang="ts">
import { Edit, Plus, Warning } from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'

import { deactivatePet, fetchPets } from '@/api/pets'
import EmptyState from '@/components/common/EmptyState.vue'
import type { PetSummary } from '@/types/domain'
import { breedLabel, resolveUploadUrl, speciesLabel } from '@/utils/format'

const pets = ref<PetSummary[]>([])
const loading = ref(true)
const failed = ref(false)
const failedPhotoIds = ref<number[]>([])

async function loadPets() {
  loading.value = true
  failed.value = false
  try {
    pets.value = await fetchPets(true)
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

function markPhotoFailed(petId: number) {
  if (!failedPhotoIds.value.includes(petId)) failedPhotoIds.value.push(petId)
}

async function deactivate(item: PetSummary) {
  if (!window.confirm(`确定停用“${item.name}”的档案吗？`)) return
  await deactivatePet(item.pet_id)
  await loadPets()
}

onMounted(loadPets)
</script>

<template>
  <main class="pets-page">
    <div class="pets-page__hero">
      <div class="pf-container pets-page__heading">
        <div><span>MY PETS</span><h1>我的宠物档案</h1><p>完整、清晰的日常档案，是紧急发布时最重要的准备。</p></div>
        <el-button type="primary" size="large" :icon="Plus" @click="$router.push('/pets/new')">创建宠物档案</el-button>
      </div>
    </div>

    <section class="pf-container pets-content">
      <div v-if="loading" class="pets-grid">
        <div v-for="item in 3" :key="item" class="pet-card pf-card"><el-skeleton animated :rows="4" /></div>
      </div>
      <div v-else-if="pets.length" class="pets-grid">
        <article v-for="pet in pets" :key="pet.pet_id" class="pet-card pf-card" :class="{ 'pet-card--inactive': pet.status !== 'ACTIVE' }">
          <div class="pet-card__portrait">
            <img
              v-if="pet.cover_photo_url && !failedPhotoIds.includes(pet.pet_id)"
              :src="resolveUploadUrl(pet.cover_photo_url) || ''"
              :alt="pet.name"
              @error="markPhotoFailed(pet.pet_id)"
            />
            <span v-else>{{ pet.name.slice(0, 1) }}</span>
            <small>{{ pet.status === 'ACTIVE' ? '使用中' : '已停用' }}</small>
          </div>
          <div class="pet-card__body">
            <span>{{ speciesLabel(pet.species) }} · {{ breedLabel(pet.breed) }}</span>
            <h2>{{ pet.name }}</h2>
            <p>{{ pet.primary_color }}{{ pet.secondary_color ? ` / ${pet.secondary_color}` : '' }} · {{ pet.size }}</p>
            <p class="pet-card__feature">{{ pet.distinctive_features || '还没有填写明显特征' }}</p>
            <div class="pet-card__actions">
              <RouterLink :to="`/pets/${pet.pet_id}/edit`"><el-icon><Edit /></el-icon> 编辑档案</RouterLink>
              <button v-if="pet.status === 'ACTIVE'" type="button" @click="deactivate(pet)"><el-icon><Warning /></el-icon> 停用</button>
            </div>
          </div>
        </article>
        <RouterLink to="/pets/new" class="new-pet-card"><el-icon :size="28"><Plus /></el-icon><strong>添加另一个宠物</strong><span>最多可维护多个独立档案</span></RouterLink>
      </div>
      <EmptyState v-else title="还没有宠物档案" :description="failed ? '档案服务暂时不可用，请稍后重试。' : '提前记录照片和明显特征，需要时能更快发布。'" :action-label="failed ? '重新加载' : '创建第一个档案'" @action="failed ? loadPets() : $router.push('/pets/new')" />
    </section>
  </main>
</template>

<style scoped>
.pets-page { min-height: calc(100vh - 68px); }
.pets-page__hero { padding: 45px 0 85px; border-bottom: 1px solid var(--pf-color-border); background: #ece9e2; }
.pets-page__heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; }
.pets-page__heading span { color: var(--pf-color-primary); font-size: 10px; font-weight: 800; letter-spacing: .15em; }
.pets-page__heading h1 { margin: 5px 0; font-size: 40px; letter-spacing: -.04em; }
.pets-page__heading p { margin: 0; color: var(--pf-color-text-secondary); font-size: 12px; }
.pets-content { position: relative; z-index: 2; margin-top: -45px; padding-bottom: 80px; }
.pets-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.pet-card { overflow: hidden; }
.pet-card--inactive { opacity: .68; filter: grayscale(.25); }
.pet-card__portrait { position: relative; display: grid; height: 190px; place-items: center; overflow: hidden; color: #765548; background: #ead8cc; font-size: 62px; font-weight: 900; }
.pet-card__portrait img { width: 100%; height: 100%; object-fit: cover; }
.pet-card__portrait small { position: absolute; top: 12px; right: 12px; padding: 4px 8px; border-radius: 999px; color: #fff; background: var(--pf-color-sage); font-size: 9px; }
.pet-card__body { padding: 18px; }
.pet-card__body > span { color: var(--pf-color-text-tertiary); font-size: 10px; }
.pet-card h2 { margin: 2px 0 5px; font-size: 22px; }
.pet-card p { margin: 4px 0; color: var(--pf-color-text-secondary); font-size: 11px; }
.pet-card__feature { min-height: 40px; padding-top: 6px; }
.pet-card__actions { display: flex; justify-content: space-between; margin-top: 14px; padding-top: 13px; border-top: 1px solid #f1e5de; }
.pet-card__actions a, .pet-card__actions button { display: inline-flex; align-items: center; gap: 4px; padding: 0; border: 0; color: var(--pf-color-primary-dark); background: transparent; font-size: 11px; font-weight: 700; cursor: pointer; }
.pet-card__actions button { color: var(--pf-color-text-tertiary); }
.new-pet-card { display: grid; min-height: 390px; align-content: center; justify-items: center; gap: 7px; border: 1px dashed #dfc3b4; border-radius: var(--pf-radius-md); color: var(--pf-color-primary-dark); background: rgb(255 255 255 / 55%); }
.new-pet-card span { color: var(--pf-color-text-tertiary); font-size: 10px; }
@media (max-width: 920px) { .pets-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .pets-page__heading { align-items: flex-start; flex-direction: column; } .pets-page__heading :deep(.el-button) { width: 100%; } .pets-grid { grid-template-columns: 1fr; } }
</style>
