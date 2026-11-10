<script setup lang="ts">
import { Clock, Location } from '@element-plus/icons-vue'
import { computed, ref } from 'vue'

import type { LostCase } from '@/types/domain'
import {
  caseStatusLabel,
  formatRelativeTime,
  resolveUploadUrl,
  speciesLabel,
} from '@/utils/format'

const props = defineProps<{
  lostCase: LostCase
}>()

const imageFailed = ref(false)
const photoUrl = computed(() => resolveUploadUrl(props.lostCase.pet.cover_photo_url))
const showPhoto = computed(() => Boolean(photoUrl.value) && !imageFailed.value)
const statusClass = computed(() => `case-card__status--${props.lostCase.status.toLowerCase()}`)
</script>

<template>
  <article class="case-card pf-card">
    <RouterLink :to="`/cases/${lostCase.case_id}`" class="case-card__visual">
      <img
        v-if="showPhoto"
        :src="photoUrl || ''"
        :alt="`${lostCase.pet.name}的照片`"
        @error="imageFailed = true"
      />
      <div v-else class="case-card__fallback" :data-species="lostCase.pet.species">
        <span class="case-card__pet-letter">{{ lostCase.pet.name.slice(0, 1) }}</span>
        <span>{{ speciesLabel(lostCase.pet.species) }}</span>
      </div>
      <span class="case-card__status" :class="statusClass">
        {{ caseStatusLabel(lostCase.status) }}
      </span>
    </RouterLink>

    <div class="case-card__body">
      <div class="case-card__heading">
        <div>
          <span>{{ speciesLabel(lostCase.pet.species) }} · {{ lostCase.pet.breed || '品种未知' }}</span>
          <h3>寻找“{{ lostCase.pet.name }}”</h3>
        </div>
        <span class="case-card__id">#{{ lostCase.case_id }}</span>
      </div>
      <p class="case-card__meta">
        <el-icon><Location /></el-icon>
        <span>{{ lostCase.address }}</span>
      </p>
      <p class="case-card__meta">
        <el-icon><Clock /></el-icon>
        <span>{{ formatRelativeTime(lostCase.lost_time) }}</span>
      </p>
      <p v-if="lostCase.pet.distinctive_features" class="case-card__feature">
        {{ lostCase.pet.distinctive_features }}
      </p>
      <RouterLink :to="`/cases/${lostCase.case_id}`" class="case-card__detail-link">
        查看详情
        <span aria-hidden="true">→</span>
      </RouterLink>
    </div>
  </article>
</template>

<style scoped>
.case-card {
  overflow: hidden;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.case-card:hover {
  border-color: #eac8b7;
  box-shadow: var(--pf-shadow-md);
  transform: translateY(-4px);
}

.case-card__visual {
  position: relative;
  display: block;
  height: 188px;
  overflow: hidden;
  background: linear-gradient(145deg, var(--pf-color-cream), var(--pf-color-coral-soft));
}

.case-card__visual img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 300ms ease;
}

.case-card:hover .case-card__visual img {
  transform: scale(1.035);
}

.case-card__fallback {
  display: grid;
  height: 100%;
  place-content: center;
  justify-items: center;
  gap: 7px;
  color: #8a5d49;
  background:
    radial-gradient(circle at 20% 15%, rgb(255 255 255 / 58%) 0 9%, transparent 9.5%),
    linear-gradient(145deg, #f8d8b8, #f5bfae);
  font-size: 12px;
  font-weight: 700;
}

.case-card__fallback[data-species='CAT'] {
  color: var(--pf-color-sage-dark);
  background:
    radial-gradient(circle at 80% 18%, rgb(255 255 255 / 55%) 0 10%, transparent 10.5%),
    linear-gradient(145deg, #e5f0e8, #cbded0);
}

.case-card__pet-letter {
  display: grid;
  width: 82px;
  height: 82px;
  place-items: center;
  border: 6px solid rgb(255 255 255 / 62%);
  border-radius: 48% 48% 44% 44%;
  background: rgb(255 255 255 / 42%);
  font-size: 38px;
  font-weight: 900;
}

.case-card__status {
  position: absolute;
  top: 13px;
  left: 13px;
  padding: 5px 10px;
  border-radius: var(--pf-radius-pill);
  color: #ffffff;
  background: var(--pf-color-primary);
  font-size: 11px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgb(67 51 45 / 14%);
}

.case-card__status--reunited {
  background: var(--pf-color-success);
}

.case-card__status--closed {
  background: #8a7d77;
}

.case-card__body {
  padding: 18px;
}

.case-card__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.case-card__heading span {
  color: var(--pf-color-text-tertiary);
  font-size: 11px;
}

.case-card__heading h3 {
  margin: 3px 0 13px;
  font-size: 19px;
  line-height: 1.35;
}

.case-card__id {
  flex: 0 0 auto;
  padding-top: 3px;
  font-variant-numeric: tabular-nums;
}

.case-card__meta {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin: 7px 0;
  color: var(--pf-color-text-secondary);
  font-size: 12px;
}

.case-card__meta .el-icon {
  flex: 0 0 auto;
  margin-top: 3px;
  color: var(--pf-color-primary);
}

.case-card__feature {
  display: -webkit-box;
  min-height: 42px;
  margin: 13px 0 15px;
  overflow: hidden;
  color: var(--pf-color-text-secondary);
  font-size: 12px;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.case-card__detail-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 13px;
  border-top: 1px solid #f3e8e1;
  color: var(--pf-color-primary-dark);
  font-size: 13px;
  font-weight: 700;
}
</style>
