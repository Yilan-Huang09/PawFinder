<script setup lang="ts">
const props = defineProps<{
  modelValue: number
  total: number
  pageSize: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

function changePage(page: number) {
  if (page !== props.modelValue) emit('update:modelValue', page)
}
</script>

<template>
  <div v-if="total > pageSize" class="app-pagination">
    <el-pagination
      background
      layout="prev, pager, next"
      :current-page="modelValue"
      :page-size="pageSize"
      :total="total"
      @current-change="changePage"
    />
  </div>
</template>

<style scoped>
.app-pagination {
  display: flex;
  justify-content: center;
  padding-top: 30px;
}
</style>
