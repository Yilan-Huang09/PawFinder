<script setup lang="ts">
import { computed } from 'vue'

import { apiState, clearApiError } from '@/api/client'

const isLoading = computed(() => apiState.pendingRequests > 0)
</script>

<template>
  <div class="app-root">
    <Transition name="request-progress">
      <div
        v-if="isLoading"
        class="app-request-progress"
        role="progressbar"
        aria-label="正在加载"
      />
    </Transition>

    <Transition name="alert-slide">
      <div v-if="apiState.errorMessage" class="app-error-surface" role="alert">
        <el-alert
          :title="apiState.errorMessage"
          type="error"
          show-icon
          closable
          @close="clearApiError"
        />
      </div>
    </Transition>

    <RouterView />
  </div>
</template>
