<script setup lang="ts">
import { Location } from '@element-plus/icons-vue'
import { computed, ref } from 'vue'

const props = defineProps<{
  latitude: number | null
  longitude: number | null
  address: string
}>()

const emit = defineEmits<{
  'update:latitude': [value: number | null]
  'update:longitude': [value: number | null]
  'update:address': [value: string]
}>()

const locating = ref(false)
const locationMessage = ref('')
const coordinatesLikelySwapped = computed(() => (
  props.latitude !== null
  && props.longitude !== null
  && Math.abs(props.latitude) > 90
  && Math.abs(props.longitude) <= 90
))

function numberValue(event: Event): number | null {
  const value = (event.target as HTMLInputElement).value
  return value === '' ? null : Number(value)
}

function useSouthwestUniversity() {
  emit('update:latitude', 29.8269)
  emit('update:longitude', 106.4253)
  if (!props.address.trim()) emit('update:address', '西南大学北门天生路附近')
  locationMessage.value = '已填入西南大学北碚校区坐标'
}

function useCurrentLocation() {
  if (!navigator.geolocation) {
    locationMessage.value = '当前浏览器不支持定位，请使用西南大学坐标或手动填写'
    return
  }
  locating.value = true
  locationMessage.value = '正在获取当前位置…'
  navigator.geolocation.getCurrentPosition(
    (position) => {
      emit('update:latitude', Number(position.coords.latitude.toFixed(7)))
      emit('update:longitude', Number(position.coords.longitude.toFixed(7)))
      locationMessage.value = '已获取当前位置，请补充具体地点描述'
      locating.value = false
    },
    () => {
      locationMessage.value = '无法获取当前位置，请检查浏览器定位权限'
      locating.value = false
    },
    { enableHighAccuracy: true, timeout: 10_000, maximumAge: 30_000 },
  )
}

function swapCoordinates() {
  if (props.latitude === null || props.longitude === null) return
  emit('update:latitude', props.longitude)
  emit('update:longitude', props.latitude)
  locationMessage.value = '已交换经纬度，请再次核对位置'
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
          placeholder="例如：西南大学北门附近"
          @input="emit('update:address', ($event.target as HTMLInputElement).value)"
        />
      </div>
    </label>
    <label class="form-field">
      <span>纬度（北纬） <b>*</b></span>
      <input
        class="form-control"
        name="latitude"
        type="number"
        inputmode="decimal"
        step="0.0000001"
        min="-90"
        max="90"
        :value="latitude ?? ''"
        placeholder="29.8269000"
        @input="emit('update:latitude', numberValue($event))"
      />
    </label>
    <label class="form-field">
      <span>经度（东经） <b>*</b></span>
      <input
        class="form-control"
        name="longitude"
        type="number"
        inputmode="decimal"
        step="0.0000001"
        min="-180"
        max="180"
        :value="longitude ?? ''"
        placeholder="106.4253000"
        @input="emit('update:longitude', numberValue($event))"
      />
    </label>
    <div class="location-fields__actions">
      <button type="button" data-test="use-swu-location" @click="useSouthwestUniversity">使用西南大学坐标</button>
      <button type="button" data-test="use-current-location" :disabled="locating" @click="useCurrentLocation">{{ locating ? '正在定位…' : '使用当前位置' }}</button>
      <button v-if="coordinatesLikelySwapped" type="button" data-test="swap-coordinates" class="location-fields__swap" @click="swapCoordinates">检测到可能填反，交换经纬度</button>
    </div>
    <p class="location-fields__hint">填写顺序是纬度 29.x、经度 106.x；也可直接使用上方快捷选择。</p>
    <p v-if="locationMessage" class="location-fields__message" role="status">{{ locationMessage }}</p>
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
.location-fields__actions { display: flex; grid-column: 1 / -1; flex-wrap: wrap; gap: 8px; }
.location-fields__actions button { min-height: 32px; padding: 0 11px; border: 1px solid var(--pf-color-border); border-radius: 7px; color: var(--pf-color-text-secondary); background: #fff; font-size: 10px; font-weight: 700; cursor: pointer; }
.location-fields__actions button:hover { border-color: var(--pf-color-primary); color: var(--pf-color-primary-dark); }
.location-fields__actions button:disabled { cursor: wait; opacity: .6; }
.location-fields__actions .location-fields__swap { border-color: #e3aa83; color: var(--pf-color-primary-dark); background: #fff3ea; }
.location-fields__hint, .location-fields__message { grid-column: 1 / -1; margin: -4px 0 0; font-size: 10px; }
.location-fields__hint { color: var(--pf-color-text-tertiary); }
.location-fields__message { color: var(--pf-color-sage-dark); font-weight: 700; }
@media (max-width: 560px) { .location-fields { grid-template-columns: 1fr; } .location-fields__address, .location-fields__actions, .location-fields__hint, .location-fields__message { grid-column: auto; } }
</style>
