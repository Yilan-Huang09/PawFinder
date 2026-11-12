<script setup lang="ts">
import { ArrowRight, Location, Plus } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const meta = computed(() => route.meta)
</script>

<template>
  <main class="placeholder-page">
    <div class="pf-container placeholder-page__inner">
      <span class="placeholder-page__eyebrow">{{ meta.eyebrow }}</span>
      <h1>{{ meta.title }}</h1>
      <p>{{ meta.description }}</p>
      <div v-if="route.name === 'home'" class="placeholder-page__actions">
        <el-button type="primary" size="large" :icon="Plus">发布走失</el-button>
        <el-button size="large" :icon="Location">提交目击</el-button>
        <RouterLink to="/cases" class="placeholder-page__text-link">
          浏览寻找中事件
          <el-icon><ArrowRight /></el-icon>
        </RouterLink>
      </div>
    </div>
  </main>
</template>

<style scoped>
.placeholder-page {
  min-height: calc(100vh - var(--pf-header-height));
  padding: 92px 0;
  background: var(--pf-color-background);
}

.placeholder-page__inner {
  max-width: 820px;
}

.placeholder-page__eyebrow {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: var(--pf-radius-pill);
  color: var(--pf-color-primary-dark);
  background: rgb(255 255 255 / 72%);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

h1 {
  max-width: 720px;
  margin: 20px 0 14px;
  font-size: clamp(38px, 6vw, 64px);
  line-height: 1.12;
  letter-spacing: -0.04em;
  overflow-wrap: anywhere;
}

p {
  max-width: 620px;
  margin: 0;
  color: var(--pf-color-text-secondary);
  font-size: 18px;
}

.placeholder-page__actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 32px;
}

.placeholder-page__text-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-left: 8px;
  color: var(--pf-color-primary-dark);
  font-weight: 700;
}

@media (max-width: 640px) {
  .placeholder-page {
    padding: 68px 0;
  }

  .placeholder-page__actions {
    align-items: stretch;
    flex-direction: column;
  }

  .placeholder-page__actions :deep(.el-button) {
    width: 100%;
    margin-left: 0;
  }

  .placeholder-page__text-link {
    justify-content: center;
    margin: 8px 0 0;
  }
}
</style>
