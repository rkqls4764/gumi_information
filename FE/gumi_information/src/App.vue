<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

delete L.Icon.Default.prototype._getIconUrl

L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL(
    'leaflet/dist/images/marker-icon-2x.png',
    import.meta.url
  ).href,

  iconUrl: new URL(
    'leaflet/dist/images/marker-icon.png',
    import.meta.url
  ).href,

  shadowUrl: new URL(
    'leaflet/dist/images/marker-shadow.png',
    import.meta.url
  ).href
})

const categories = [
  { id: 'all', label: '전체' },
  { id: 'tour', label: '관광지' },
  { id: 'food', label: '맛집' },
  { id: 'cafe', label: '카페' },
  { id: 'festival', label: '축제' },
  { id: 'stay', label: '숙박' }
]

const regions = [
  { id: 'all', label: '전체' },
  { id: 'gumi', label: '구미시' },
  { id: 'kimcheon', label: '김천시' },
  { id: 'chilgok', label: '칠곡군' }
]

const places = ref([])
const activeCategory = ref('all')
const activeRegion = ref('all')
const map = ref(null)
const markerGroup = ref(null)
const mapBounds = ref(null)
const displayedPlaces = computed(() => {
  return filteredPlaces.value.slice(0, 100)
})

function mapTypeFromCats(cat1, cat2, cat3) {
  const txt = `${cat1||''} ${cat2||''} ${cat3||''}`
  if (txt.includes('음식') || txt.includes('음식점')) return 'food'
  if (txt.includes('카페')) return 'cafe'
  if (txt.includes('축제') || txt.includes('공연')) return 'festival'
  if (txt.includes('숙박') || txt.includes('호텔') || txt.includes('민박')) return 'stay'
  if (txt.includes('관광') || txt.includes('명소') || txt.includes('레포츠') || txt.includes('문화')) return 'tour'
  return 'tour'
}

const filteredPlaces = computed(() => {
  return places.value.filter(place => {
    const categoryMatch =
      activeCategory.value === 'all' ||
      place.type === activeCategory.value

    const regionMatch =
      activeRegion.value === 'all' ||
      place.area === activeRegion.value

    const boundsMatch =
      !mapBounds.value ||
      mapBounds.value.contains(
        L.latLng(place.lat, place.lng)
      )

    return categoryMatch &&
           regionMatch &&
           boundsMatch
  })
})

const setCategory = (id) => { activeCategory.value = id }
const setRegion = (id) => { activeRegion.value = id }

const updateMarkers = () => {
  if (!map.value || !markerGroup.value) return

  markerGroup.value.clearLayers()

  const visiblePlaces = filteredPlaces.value

const MAX_MARKERS = 100

const placesToShow =
  visiblePlaces.length > MAX_MARKERS
    ? visiblePlaces.slice(0, MAX_MARKERS)
    : visiblePlaces

console.log(
  `현재 지도에 보이는 장소: ${visiblePlaces.length}개`
)

console.log(
  `실제 표시되는 마커: ${placesToShow.length}개`
)

placesToShow.forEach(place => {
  L.marker([place.lat, place.lng])
    .bindPopup(`
      <strong>${place.name}</strong><br/>
      ${place.region || ''}
    `)
    .addTo(markerGroup.value)
})
}

const initMap = () => {
  map.value = L.map('map').setView(
  [36.1195, 128.3446], // 구미시청
  13
)

  L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
      attribution: '&copy; OpenStreetMap contributors'
    }
  ).addTo(map.value)

  markerGroup.value = L.layerGroup().addTo(map.value)

  mapBounds.value = map.value.getBounds()

  map.value.on('moveend zoomend', () => {
  mapBounds.value = map.value.getBounds()

  console.log(
    '현재 지도 범위 내 장소:',
    filteredPlaces.value.length
  )

  updateMarkers()
})
}

async function fetchPlaces() {
  try {
    const API_BASE =
      import.meta.env.VITE_API_BASE || 'http://localhost:8000'

    const url = `${API_BASE}/places`

    console.log('API_BASE =', API_BASE)
    console.log('요청 URL =', url)

    const res = await fetch(url)

    console.log(
      'fetch response:',
      res.status,
      res.statusText,
      'ok=',
      res.ok
    )

    if (!res.ok) {
      const txt = await res.text()
      console.error('places fetch failed status', res.status, txt)
      return
    }

    const data = await res.json()

    console.log(
      'places payload length:',
      Array.isArray(data) ? data.length : 'not-array'
    )

    console.table(data.slice(0, 10))

    places.value = data.map(p => {
  const lat =
    p.mapy !== null &&
    p.mapy !== undefined &&
    p.mapy !== ''
      ? Number(p.mapy)
      : null

  const lng =
    p.mapx !== null &&
    p.mapx !== undefined &&
    p.mapx !== ''
      ? Number(p.mapx)
      : null

  return {
  ...p,   // DB 원본 전부 저장

  id: p.id ?? p.content_id ?? null,
  name: p.title || '',
  region: p.addr1 || '',
  type: mapTypeFromCats(
    p.cat1,
    p.cat2,
    p.cat3
  ),
  area: p.areacode || '',
  rating: '0.0',
  review: 0,
  lat,
  lng
}
}).filter(
  p =>
    Number.isFinite(p.lat) &&
    Number.isFinite(p.lng)
)

console.log(
  'places after filter:',
  places.value.length
)

mapBounds.value = map.value.getBounds()

console.log(
  '초기 지도 범위 내 장소 수:',
  filteredPlaces.value.length
)

updateMarkers()

updateMarkers()
console.log(
  '현재 지도 범위',
  mapBounds.value?.toBBoxString()
)
console.log(
  '현재 지도 범위',
  mapBounds.value?.toBBoxString()
)
  } catch (err) {
    console.error('fetchPlaces error', err)
  }
}

onMounted(() => {
  initMap()
  fetchPlaces()
})

watch(filteredPlaces, () => {
  updateMarkers()
})
</script>

<template>
  <div class="map-page">
    <div class="topbar">
      <h1>구미/경북 지도</h1>
    </div>

    <div class="controls">
      <div class="filter-row">
        <span>카테고리</span>
        <button
          v-for="item in categories"
          :key="item.id"
          :class="{ selected: activeCategory === item.id }"
          @click="setCategory(item.id)"
        >{{ item.label }}</button>
      </div>

      <div class="filter-row">
        <span>권역</span>
        <button
          v-for="item in regions"
          :key="item.id"
          :class="{ selected: activeRegion === item.id }"
          @click="setRegion(item.id)"
        >{{ item.label }}</button>
      </div>
    </div>

    <div class="map-card">
      <div class="map-header">
        <span class="map-title">구미시</span>
      </div>
      <div id="map" class="map-view"></div>
    </div>

    <section class="place-list">
  <h3>지도 내 장소 목록</h3>

  <div v-if="filteredPlaces.length === 0" class="empty-message">
    현재 지도 범위에 표시할 장소가 없습니다.
  </div>

  <div v-else class="place-cards">
  <article
    class="place-card"
    v-for="place in displayedPlaces"
    :key="place.id"
  >
    <div class="place-icon">🏙️</div>

    <div class="place-info">
      <strong>{{ place.name }}</strong>
      <span>{{ place.region }}</span>
    </div>

    <div class="place-meta">
      <div class="place-rating">
        <strong>★ {{ place.rating }}</strong>
        <span>({{ place.review }})</span>
      </div>

      <button class="detail-button">상세보기</button>
    </div>
  </article>
</div>
    </section>

    <button class="current-location-button" type="button">
      현재 위치로 이동
    </button>
  </div>
</template>

<style scoped>
.map-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.topbar h1 { margin-bottom: 20px; font-size: 1.8rem; }
.controls { display: grid; gap: 16px; margin-bottom: 16px; }
.filter-row { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.filter-row span { min-width: 70px; font-weight: 600; }
button { border: 1px solid #ccc; border-radius: 999px; padding: 10px 16px; cursor: pointer; background: #fff; }
button.selected { background: #111; color: #fff; border-color: #111; }
.map-card { border: 1px solid #e0e0e0; border-radius: 18px; overflow: hidden; margin-bottom: 24px; background: #fafafa; }
.map-header { padding: 16px 20px; border-bottom: 1px solid #ececec; display: flex; align-items: center; justify-content: space-between; }
.map-title { font-weight: 700; font-size: 1rem; }
.map-view { width: 100%; height: 560px; }
.place-list h3 { margin: 0 0 16px; font-size: 1.1rem; }
.place-cards { display: grid; gap: 16px; }
.place-card {
  display: grid;
  grid-template-columns: 52px 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border: 1px solid #e6e6e6;
  border-radius: 16px;
  background: #fff;
}
.place-icon { width: 52px; height: 52px; border-radius: 16px; background: #f3f4f6; display: grid; place-items: center; font-size: 1.3rem; }
.place-info strong { display: block; font-size: 1rem; margin-bottom: 4px; }
.place-info span { color: #777; font-size: 0.95rem; }
.place-rating { text-align: right; min-width: 90px; }
.place-rating strong { display: block; color: #222; }
.place-rating span { color: #777; font-size: 0.9rem; }
.place-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.detail-button {
  white-space: nowrap;
}
.current-location-button { width: 100%; margin-top: 24px; border: none; background: #111; color: #fff; padding: 16px; border-radius: 14px; font-size: 1rem; cursor: pointer; }
.empty-message {
  padding: 40px;
  text-align: center;
  border: 1px dashed #d1d5db;
  border-radius: 16px;
  background: #fafafa;
  color: #6b7280;
  font-size: 0.95rem;
}
</style>