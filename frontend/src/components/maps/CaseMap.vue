<script setup lang="ts">
import { Location, MapLocation } from '@element-plus/icons-vue'
import { computed, nextTick, onMounted, ref, watch } from 'vue'

import type { LostCase, SearchArea, Sighting } from '@/types/domain'

const props = withDefaults(defineProps<{
  lostCase?: LostCase | null
  sightings?: Sighting[]
  areas?: SearchArea[]
  mapKey?: string
}>(), { lostCase: null, sightings: () => [], areas: () => [], mapKey: '' })

const mapContainerId = `pawfinder-map-${Math.random().toString(36).slice(2)}`
const mapFailed = ref(false)
const loadingMap = ref(false)
const useProvider = computed(() => Boolean(props.mapKey) && !mapFailed.value)

type AMapApi = {
  Map: new (id: string, options: Record<string, unknown>) => { add: (items: unknown[]) => void }
  Marker: new (options: Record<string, unknown>) => unknown
  Circle: new (options: Record<string, unknown>) => unknown
}

function loadAmapScript(): Promise<AMapApi> {
  const existing = (window as Window & { AMap?: AMapApi }).AMap
  if (existing) return Promise.resolve(existing)
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(props.mapKey)}`
    script.async = true
    script.onload = () => {
      const api = (window as Window & { AMap?: AMapApi }).AMap
      api ? resolve(api) : reject(new Error('地图服务未初始化'))
    }
    script.onerror = () => reject(new Error('地图脚本加载失败'))
    document.head.appendChild(script)
  })
}

async function initializeMap() {
  if (!props.mapKey || !props.lostCase || mapFailed.value) return
  loadingMap.value = true
  await nextTick()
  try {
    const AMap = await loadAmapScript()
    const center = [props.lostCase.longitude, props.lostCase.latitude]
    const map = new AMap.Map(mapContainerId, { zoom: 14, center, resizeEnable: true })
    const overlays: unknown[] = [new AMap.Marker({ position: center, title: `最后出现：${props.lostCase.address}` })]
    props.sightings.forEach((item) => overlays.push(new AMap.Marker({ position: [item.longitude, item.latitude], title: `目击：${item.address}` })))
    props.areas.forEach((item) => overlays.push(new AMap.Circle({ center: [item.center_longitude, item.center_latitude], radius: item.radius_meters, strokeColor: '#e86f47', fillColor: '#ffd9ca', fillOpacity: .25 })))
    map.add(overlays)
  } catch {
    mapFailed.value = true
  } finally {
    loadingMap.value = false
  }
}

onMounted(initializeMap)
watch(() => [props.lostCase?.case_id, props.sightings.length, props.areas.length], initializeMap)
</script>

<template>
  <section class="case-map pf-card">
    <div class="case-map__head">
      <div><span>SEARCH COORDINATES</span><h2>空间线索</h2></div>
      <small v-if="useProvider">高德地图模式</small>
      <small v-else>无密钥坐标模式</small>
    </div>
    <div v-if="useProvider" :id="mapContainerId" class="case-map__provider" data-map-mode="provider">
      <span v-if="loadingMap">地图加载中…</span>
    </div>
    <div v-else class="case-map__fallback" data-map-mode="fallback">
      <div class="case-map__canvas" aria-hidden="true">
        <span class="case-map__road case-map__road--a" />
        <span class="case-map__road case-map__road--b" />
        <span v-if="lostCase" class="case-map__pin case-map__pin--lost"><el-icon><Location /></el-icon></span>
        <span v-for="(item, index) in sightings.slice(0, 5)" :key="item.sighting_id" class="case-map__pin case-map__pin--sighting" :style="{ left: `${22 + (index * 17) % 66}%`, top: `${23 + (index * 29) % 58}%` }"><el-icon><MapLocation /></el-icon></span>
      </div>
      <p v-if="mapFailed" class="case-map__notice">地图服务暂时不可用，已自动切换为坐标列表。</p>
      <ul>
        <li v-if="lostCase"><i class="legend legend--lost" /><div><strong>最后出现 · {{ lostCase.address }}</strong><span>{{ lostCase.latitude.toFixed(6) }}, {{ lostCase.longitude.toFixed(6) }}</span></div></li>
        <li v-for="item in sightings" :key="item.sighting_id"><i class="legend legend--sighting" /><div><strong>目击 · {{ item.address }}</strong><span>{{ item.latitude.toFixed(6) }}, {{ item.longitude.toFixed(6) }}</span></div></li>
        <li v-for="item in areas" :key="item.area_id"><i class="legend legend--area" /><div><strong>搜寻区 · {{ item.area_name }}</strong><span>{{ item.center_latitude.toFixed(6) }}, {{ item.center_longitude.toFixed(6) }} · 半径 {{ item.radius_meters }} m</span></div></li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.case-map { overflow: hidden; }
.case-map__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 19px 21px; border-bottom: 1px solid var(--pf-color-border); }
.case-map__head span { color: var(--pf-color-primary); font-size: 9px; font-weight: 800; letter-spacing: .12em; }
.case-map__head h2 { margin: 2px 0 0; font-size: 18px; }
.case-map__head small { padding: 4px 8px; border-radius: 99px; color: var(--pf-color-sage-dark); background: var(--pf-color-sage-soft); font-size: 9px; }
.case-map__provider { display: grid; min-height: 390px; place-items: center; color: var(--pf-color-text-tertiary); background: #edf1e8; font-size: 11px; }
.case-map__canvas { position: relative; height: 225px; overflow: hidden; background: linear-gradient(135deg, #eaf0e7, #f4eadc); }
.case-map__canvas::before, .case-map__canvas::after { position: absolute; border-radius: 50%; background: rgb(145 177 143 / 20%); content: ''; }
.case-map__canvas::before { width: 180px; height: 150px; top: -40px; right: -20px; }
.case-map__canvas::after { width: 130px; height: 115px; bottom: -35px; left: 8%; }
.case-map__road { position: absolute; height: 18px; border: 5px solid #fff; background: #e3dbcf; box-shadow: 0 0 0 1px #d9d0c5; transform-origin: left center; }
.case-map__road--a { width: 125%; top: 28%; left: -10%; transform: rotate(11deg); }
.case-map__road--b { width: 105%; top: 82%; left: 5%; transform: rotate(-38deg); }
.case-map__pin { position: absolute; z-index: 2; display: grid; width: 31px; height: 31px; place-items: center; border: 4px solid rgb(255 255 255 / 78%); border-radius: 50% 50% 50% 8px; color: #fff; transform: rotate(-45deg); box-shadow: 0 5px 13px rgb(69 48 39 / 22%); }
.case-map__pin .el-icon { transform: rotate(45deg); }
.case-map__pin--lost { top: 43%; left: 46%; background: var(--pf-color-primary); }
.case-map__pin--sighting { background: var(--pf-color-sage-dark); }
.case-map__notice { margin: 0; padding: 8px 18px; color: #866351; background: #fff2df; font-size: 9px; }
.case-map ul { display: grid; max-height: 235px; margin: 0; padding: 4px 20px 12px; overflow: auto; list-style: none; }
.case-map li { display: grid; grid-template-columns: 10px 1fr; align-items: start; gap: 9px; padding: 11px 0; border-bottom: 1px solid #f0e5de; }
.case-map li:last-child { border-bottom: 0; }
.case-map li div { display: grid; }
.case-map li strong { font-size: 10px; }
.case-map li span { color: var(--pf-color-text-tertiary); font-family: ui-monospace, monospace; font-size: 9px; }
.legend { width: 8px; height: 8px; margin-top: 4px; border-radius: 50%; background: var(--pf-color-primary); }
.legend--sighting { background: var(--pf-color-sage-dark); }
.legend--area { border: 2px solid #bc875f; background: transparent; }
</style>
