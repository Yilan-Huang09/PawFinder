<script setup lang="ts">
import { Location } from '@element-plus/icons-vue'

defineProps<{
  latitude: number | null
  longitude: number | null
  address: string
}>()

const emit = defineEmits<{
  'update:latitude': [value: number | null]
  'update:longitude': [value: number | null]
  'update:address': [value: string]
}>()

function numberValue(event: Event): number | null {
  const value = (event.target as HTMLInputElement).value
  return value === '' ? null : Number(value)
}
</script>

<template>
  <div class="location-fields">
    <label class="form-field location-fields__address">
      <span>位置描述 <b>*</b></span>
      <div class="form-control">
        <el-icon><Location /></el-icon>
        <input
          name="address"
          :value="address"
          maxlength="255"
          placeholder="例如：文三路地铁站 A 口附近"
          @input="emit('update:address', ($event.target as HTMLInputElement).value)"
        />
      </div>
    </label>
    <label class="form-field">
      <span>纬度 <b>*</b></span>
      <input
        class="form-control"
        name="latitude"
        type="number"
        step="0.0000001"
        min="-90"
        max="90"
        :value="latitude ?? ''"
        placeholder="30.2741000"
        @input="emit('update:latitude', numberValue($event))"
      />
    </label>
    <label class="form-field">
      <span>经度 <b>*</b></span>
      <input
        class="form-control"
        name="longitude"
        type="number"
        step="0.0000001"
        min="-180"
        max="180"
        :value="longitude ?? ''"
        placeholder="120.1551000"
        @input="emit('update:longitude', numberValue($event))"
      />
    </label>
    <p class="location-fields__hint">课程演示可从地图软件复制经纬度；地图接入失败时仍可完整提交。</p>
  </div>
</template>

<style scoped>
.location-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.location-fields__address { grid-column: 1 / -1; }
.form-field { display: grid; gap: 7px; min-width: 0; color: var(--pf-color-text); font-size: 12px; font-weight: 700; }
.form-field b { color: var(--pf-color-primary); }
.form-control { width: 100%; height: 44px; padding: 0 12px; border: 1px solid var(--pf-color-border); border-radius: 9px; outline: 0; color: var(--pf-color-text); background: #fff; font-size: 12px; transition: border-color 160ms ease, box-shadow 160ms ease; }
div.form-control { display: flex; align-items: center; gap: 8px; }
div.form-control input { min-width: 0; flex: 1; border: 0; outline: 0; background: transparent; }
.form-control:focus, .form-control:focus-within { border-color: var(--pf-color-primary); box-shadow: var(--pf-shadow-focus); }
.form-control .el-icon { color: var(--pf-color-primary); }
.location-fields__hint { grid-column: 1 / -1; margin: -6px 0 0; color: var(--pf-color-text-tertiary); font-size: 10px; }
@media (max-width: 560px) { .location-fields { grid-template-columns: 1fr; } .location-fields__address, .location-fields__hint { grid-column: auto; } }
</style>
