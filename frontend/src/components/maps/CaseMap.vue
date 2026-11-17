<script setup lang="ts">
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
const osmEmbedUrl = computed(() => {
  const latitude = props.lostCase?.latitude ?? 29.8269
  const longitude = props.lostCase?.longitude ?? 106.4253
  const latitudeDelta = 0.012
  const longitudeDelta = 0.018
  const bbox = [
    longitude - longitudeDelta,
    latitude - latitudeDelta,
    longitude + longitudeDelta,
    latitude + latitudeDelta,
  ].join(',')
  return `https://www.openstreetmap.org/export/embed.html?bbox=${encodeURIComponent(bbox)}&layer=mapnik&marker=${latitude},${longitude}`
})

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
      <div><span>空间坐标</span><h2>真实地图与线索</h2></div>
      <small v-if="useProvider">高德地图</small>
      <small v-else>开放街图</small>
    </div>
    <div v-if="useProvider" :id="mapContainerId" class="case-map__provider" data-map-mode="provider">
      <span v-if="loadingMap">地图加载中…</span>
    </div>
    <div v-else class="case-map__fallback" data-map-mode="fallback">
      <iframe
        class="case-map__osm"
        :src="osmEmbedUrl"
        title="宠物最后出现位置的真实地图"
        loading="lazy"
        referrerpolicy="strict-origin-when-cross-origin"
      />
      <p v-if="mapFailed" class="case-map__notice">高德地图暂时不可用，已自动切换为开放街图。</p>
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
.case-map__osm { display: block; width: 100%; height: 310px; border: 0; background: #e8ece7; }
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
