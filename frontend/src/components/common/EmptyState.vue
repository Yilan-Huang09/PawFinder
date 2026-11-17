<script setup lang="ts">
import { Box } from '@element-plus/icons-vue'

withDefaults(
  defineProps<{
    title: string
    description?: string
    actionLabel?: string
  }>(),
  {
    description: '',
    actionLabel: '',
  },
)

defineEmits<{
  action: []
}>()
</script>

<template>
  <div class="empty-state">
    <span class="empty-state__icon" aria-hidden="true">
      <el-icon :size="28"><Box /></el-icon>
    </span>
    <strong>{{ title }}</strong>
    <p v-if="description">{{ description }}</p>
    <el-button v-if="actionLabel" type="primary" plain @click="$emit('action')">
      {{ actionLabel }}
    </el-button>
  </div>
</template>

<style scoped>
.empty-state {
  display: grid;
  justify-items: center;
  padding: 56px 24px;
  border: 1px dashed #e7cfc1;
  border-radius: var(--pf-radius-md);
  color: var(--pf-color-text-secondary);
  background: var(--pf-color-surface-warm);
  text-align: center;
}

.empty-state__icon {
  display: grid;
  width: 58px;
  height: 58px;
  margin-bottom: 14px;
  place-items: center;
  border-radius: 50%;
  color: var(--pf-color-sage-dark);
  background: var(--pf-color-sage-soft);
}

.empty-state strong {
  color: var(--pf-color-text);
  font-size: 17px;
}

.empty-state p {
  max-width: 480px;
  margin: 7px 0 18px;
  font-size: 13px;
}
</style>
