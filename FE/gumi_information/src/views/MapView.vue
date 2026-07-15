<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow
})

const categoryLabels = {
  tour: '관광지',
  food: '맛집',
  cafe: '카페',
  festival: '축제',
  stay: '숙박'
}

const selectedPlace = ref(null)

const openPlaceDetail = (place) => {
  selectedPlace.value = place
}

const closePlaceDetail = () => {
  selectedPlace.value = null
}

const getTypeLabel = (type) => categoryLabels[type] || '기타'

const categories = [
  { id: 'all', label: '전체' },
  { id: 'tour', label: '관광지' },
  { id: 'food', label: '맛집' },
  { id: 'cafe', label: '카페' },
  { id: 'festival', label: '축제' },
  { id: 'stay', label: '숙박' }
]

const inferRegionInfo = (place) => {
  const text = `${place.addr1 || ''} ${place.addr2 || ''} ${place.title || ''}`.toLowerCase()

  if (text.includes('대구')) {
    return { key: 'daegu', label: '대구광역시' }
  }

  if (text.includes('성주')) {
    return { key: 'seongju', label: '성주군' }
  }

  if (text.includes('고령')) {
    return { key: 'goryeong', label: '고령군' }
  }

  if (text.includes('김천')) {
    return { key: 'kimcheon', label: '김천시' }
  }

  if (text.includes('칠곡')) {
    return { key: 'chilgok', label: '칠곡군' }
  }

  if (text.includes('구미')) {
    return { key: 'gumi', label: '구미시' }
  }

  const areaCode = `${place.areacode || ''}`.toLowerCase()

  if (areaCode.includes('daegu') || areaCode.includes('대구')) {
    return { key: 'daegu', label: '대구광역시' }
  }

  if (areaCode.includes('seongju') || areaCode.includes('성주')) {
    return { key: 'seongju', label: '성주군' }
  }

  if (areaCode.includes('goryeong') || areaCode.includes('고령')) {
    return { key: 'goryeong', label: '고령군' }
  }

  if (areaCode.includes('kimcheon') || areaCode.includes('김천')) {
    return { key: 'kimcheon', label: '김천시' }
  }

  if (areaCode.includes('chilgok') || areaCode.includes('칠곡')) {
    return { key: 'chilgok', label: '칠곡군' }
  }

  if (areaCode.includes('gumi') || areaCode.includes('구미')) {
    return { key: 'gumi', label: '구미시' }
  }

  return null
}

const regions = [
  { id: 'all', label: '전체' },
  { id: 'gumi', label: '구미시' },
  { id: 'daegu', label: '대구광역시' },
  { id: 'chilgok', label: '칠곡군' },
  { id: 'seongju', label: '성주군' },
  { id: 'goryeong', label: '고령군' }
]

const regionCenters = {
  all: [36.1195, 128.3446],
  gumi: [36.1195, 128.3446],
  daegu: [35.8714, 128.6014],
  chilgok: [35.9953, 128.4015],
  seongju: [35.9193, 128.2838],
  goryeong: [35.7264, 128.2620]
}

const places = ref([])
const activeCategory = ref('all')
const activeRegion = ref('all')
const map = ref(null)
const markerGroup = ref(null)
const mapBounds = ref(null)

const pageSize = 10
const currentPage = ref(1)

const displayedPlaces = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredPlaces.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredPlaces.value.length / pageSize))
})

const pageWindow = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i += 1) {
      pages.push(i)
    }
    return pages
  }

  pages.push(1)

  if (current > 4) {
    pages.push('...')
  }

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)

  for (let i = start; i <= end; i += 1) {
    pages.push(i)
  }

  if (current < total - 3) {
    pages.push('...')
  }

  pages.push(total)
  return pages
})

const goToPage = (page) => {
  if (page === '...') return
  currentPage.value = Math.max(1, Math.min(totalPages.value, page))
}

function mapTypeFromCats(place) {
  const text = [
    place.title || '',
    place.addr1 || '',
    place.addr2 || '',
    place.cat1 || '',
    place.cat2 || '',
    place.cat3 || '',
    place.lcls_systm1 || '',
    place.lcls_systm2 || '',
    place.lcls_systm3 || ''
  ]
    .join(' ')
    .toLowerCase()

  const contentTypeId = Number(
    place.content_type_id ?? place.contentTypeId ?? place.contenttypeid
  )

  if (/(카페|커피|cafe|coffee|디저트|베이커리|브런치)/.test(text)) {
    return 'cafe'
  }

  if (
    contentTypeId === 39 ||
    /(음식점|맛집|식당|한식|중식|일식|양식|분식|술집|주점|백반|국밥|치킨|피자)/.test(text)
  ) {
    return 'food'
  }

  if (/(축제|공연|행사)/.test(text)) {
    return 'festival'
  }

  if (/(숙박|호텔|민박)/.test(text)) {
    return 'stay'
  }

  if (
    contentTypeId === 12 ||
    contentTypeId === 14 ||
    contentTypeId === 15 ||
    contentTypeId === 28 ||
    /(관광|명소|레포츠|문화)/.test(text)
  ) {
    return 'tour'
  }

  return 'tour'
}

const filteredPlaces = computed(() => {
  return places.value.filter(place => {
    const categoryMatch =
      activeCategory.value === 'all' ||
      place.type === activeCategory.value

    const regionMatch =
  activeRegion.value === 'all' ||
  place.regionKey === activeRegion.value

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
const setRegion = (id) => {
  activeRegion.value = id

  if (!map.value) return

  const center = regionCenters[id] || regionCenters.all
  map.value.flyTo(center, 13, { duration: 0.8 })
}

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
  map.value = L.map('map').setView(regionCenters.all, 13)

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

   places.value = data
  .map(p => {
    const lat =
      p.mapy !== null && p.mapy !== undefined && p.mapy !== ''
        ? Number(p.mapy)
        : null
    const lng =
      p.mapx !== null && p.mapx !== undefined && p.mapx !== ''
        ? Number(p.mapx)
        : null

    const type = mapTypeFromCats({
      ...p,
      content_type_id: p.content_type_id ?? p.contenttypeid,
      title: p.title || '',
      addr1: p.addr1 || '',
      addr2: p.addr2 || '',
      cat1: p.cat1 || '',
      cat2: p.cat2 || '',
      cat3: p.cat3 || '',
      lcls_systm1: p.lcls_systm1 || '',
      lcls_systm2: p.lcls_systm2 || '',
      lcls_systm3: p.lcls_systm3 || ''
    })

    const regionInfo = inferRegionInfo({
      addr1: p.addr1 || '',
      addr2: p.addr2 || '',
      title: p.title || '',
      areacode: p.areacode || ''
    })

return {
  ...p,
  id: p.id ?? p.content_id ?? null,
  name: p.title || '',
  region: p.addr1 || '',
  address: p.addr1 || p.addr2 || '',
  type,
  area: p.areacode || '',
  regionKey: regionInfo?.key || null,
  regionLabel: regionInfo?.label || '',
  rating: '0.0',
  review: 0,
  lat,
  lng,
  image: p.firstimage || p.firstimage2 || ''
}
  })
  .filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lng))

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

watch(
  regions,
  (nextRegions) => {
    if (
      activeRegion.value !== 'all' &&
      !nextRegions.some(item => item.id === activeRegion.value)
    ) {
      activeRegion.value = 'all'
    }
  },
  { immediate: true }
)

watch(filteredPlaces, () => {
  currentPage.value = 1
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
  <div class="place-image-wrap">
    <img
      v-if="place.image"
      :src="place.image"
      :alt="place.name"
      class="place-image"
    />
    <div v-else class="place-icon">🏙️</div>
  </div>

  <div class="place-info">
    <strong>{{ place.name }}</strong>
    <span>{{ place.region }}</span>
  </div>

  <div class="place-meta">
    <div class="place-rating">
      <strong>★ {{ place.rating }}</strong>
      <span>({{ place.review }})</span>
    </div>

    <button class="detail-button" type="button" @click="openPlaceDetail(place)">
  상세보기
</button>
  </div>
</article>
</div>
    </section>

    <div v-if="filteredPlaces.length > 0" class="pagination">
  <button
    class="page-nav"
    type="button"
    :disabled="currentPage === 1"
    @click="goToPage(currentPage - 1)"
  >
    이전
  </button>

  <div class="page-numbers">
    <button
      v-for="page in pageWindow"
      :key="page"
      class="page-number"
      :class="{ selected: currentPage === page, ellipsis: page === '...' }"
      type="button"
      @click="goToPage(page)"
    >
      {{ page }}
    </button>
  </div>

  <button
    class="page-nav"
    type="button"
    :disabled="currentPage === totalPages"
    @click="goToPage(currentPage + 1)"
  >
    다음
  </button>
</div>

    <button class="current-location-button" type="button">
      현재 위치로 이동
    </button>

    <div v-if="selectedPlace" class="detail-modal-overlay" @click.self="closePlaceDetail">
  <div class="detail-modal">
    <button class="detail-modal-close" type="button" @click="closePlaceDetail">×</button>

    <div class="detail-modal-content">
      <div class="detail-modal-image-wrap">
        <img
          v-if="selectedPlace.image"
          :src="selectedPlace.image"
          :alt="selectedPlace.name"
          class="detail-modal-image"
        />
        <div v-else class="detail-modal-image-placeholder">🏙️</div>
      </div>

      <div class="detail-modal-info">
        <span class="detail-chip">{{ getTypeLabel(selectedPlace.type) }}</span>
        <h3>{{ selectedPlace.name }}</h3>
        <p class="detail-address">{{ selectedPlace.address || selectedPlace.region }}</p>

        <div class="detail-meta-row">
          <span>평점: ★ {{ selectedPlace.rating }}</span>
          <span>리뷰: {{ selectedPlace.review }}</span>
        </div>
      </div>
    </div>
  </div>
</div>
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
  grid-template-columns: 72px 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border: 1px solid #e6e6e6;
  border-radius: 16px;
  background: #fff;
}
.place-image-wrap {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  overflow: hidden;
  background: #f3f4f6;
  display: grid;
  place-items: center;
}
.place-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
.detail-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 1000;
}
.detail-modal {
  width: min(720px, 100%);
  background: #fff;
  border-radius: 22px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  position: relative;
}
.detail-modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  border: none;
  background: #f3f4f6;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 1.2rem;
  padding: 0;
}
.detail-modal-content {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
  align-items: start;
}
.detail-modal-image-wrap {
  width: 100%;
  height: 220px;
  border-radius: 18px;
  overflow: hidden;
  background: #f3f4f6;
  display: grid;
  place-items: center;
}
.detail-modal-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.detail-chip {
  display: inline-block;
  padding: 6px 10px;
  background: #111;
  color: #fff;
  border-radius: 999px;
  font-size: 0.85rem;
  margin-bottom: 10px;
}
.detail-modal-info h3 {
  margin: 0 0 8px;
  font-size: 1.25rem;
}
.detail-address {
  margin: 0 0 12px;
  color: #6b7280;
}
.detail-meta-row {
  display: flex;
  gap: 16px;
  color: #374151;
  font-weight: 600;
  margin-bottom: 12px;
}
.detail-description {
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
}
.page-nav,
.page-number {
  border: 1px solid #d1d5db;
  background: #fff;
  color: #111;
  padding: 8px 12px;
  border-radius: 999px;
  min-width: 40px;
}
.page-nav:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-number.selected {
  background: #111;
  color: #fff;
  border-color: #111;
}
.page-numbers {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: nowrap;
}
.page-number.ellipsis {
  border: none;
  background: transparent;
  cursor: default;
  pointer-events: none;
}
</style>