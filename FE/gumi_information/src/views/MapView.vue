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
  food: '식당',
  cafe: '카페',
  festival: '축제',
  stay: '숙박',
  activity: '액티비티'
}

const selectedPlace = ref(null)
const reviewTargetPlace = ref(null)
const reviewModalOpen = ref(false)
const reviewDraft = ref(0)
const reviewSubmitting = ref(false)

const openPlaceDetail = (place) => {
  selectedPlace.value = place
}

const closePlaceDetail = () => {
  selectedPlace.value = null
}

const openReviewModal = (place) => {
  reviewTargetPlace.value = place
  reviewDraft.value = 0
  reviewModalOpen.value = true
}

const closeReviewModal = () => {
  reviewModalOpen.value = false
  reviewTargetPlace.value = null
  reviewDraft.value = 0
}

const selectReviewScore = (score) => {
  reviewDraft.value = Math.max(0, Math.min(10, score))
}

const selectHalfStar = (event, star) => {
  const rect = event.currentTarget.getBoundingClientRect()
  const x = event.clientX - rect.left

  reviewDraft.value =
    x < rect.width / 2
      ? (star - 0.5) * 2
      : star * 2
}

const getStarFill = (star) => {
  const value = reviewDraft.value / 2

  if (value >= star) return 100
  if (value >= star - 0.5) return 50
  return 0
}

const getTypeLabel = (type) => categoryLabels[type] || '기타'

const createIconImage = (icon) =>
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="72" height="72">
      <rect width="72" height="72" rx="16" fill="#f3f4f6"/>
      <text
        x="36"
        y="48"
        text-anchor="middle"
        font-size="32"
      >
        ${icon}
      </text>
    </svg>
  `)

const categoryDefaultImageMap = {
  tour: createIconImage('📍'),
  food: createIconImage('🍴'),
  cafe: createIconImage('☕'),
  festival: createIconImage('🎉'),
  stay: createIconImage('🏨'),
  activity: createIconImage('🚴')
}

const getDefaultImage = (place) => {
  const type = place?.type || 'tour'
  return categoryDefaultImageMap[type] || categoryDefaultImageMap.tour
}

const categories = [
  { id: 'all', label: '전체' },
  { id: 'tour', label: '관광지' },
  { id: 'food', label: '식당' },
  { id: 'cafe', label: '카페' },
  { id: 'festival', label: '축제' },
  { id: 'stay', label: '숙박' },
  { id: 'activity', label: '액티비티' }
]

const inferRegionInfo = (place) => {
  const text = `${place.addr1 || ''} ${place.addr2 || ''} ${place.title || ''}`.toLowerCase()
  if (text.includes('대구')) return { key: 'daegu', label: '대구광역시' }
  if (text.includes('성주')) return { key: 'seongju', label: '성주군' }
  if (text.includes('고령')) return { key: 'goryeong', label: '고령군' }
  if (text.includes('김천')) return { key: 'kimcheon', label: '김천시' }
  if (text.includes('칠곡')) return { key: 'chilgok', label: '칠곡군' }
  if (text.includes('구미')) return { key: 'gumi', label: '구미시' }

  const areaCode = `${place.areacode || ''}`.toLowerCase()
  if (areaCode.includes('daegu') || areaCode.includes('대구')) return { key: 'daegu', label: '대구광역시' }
  if (areaCode.includes('seongju') || areaCode.includes('성주')) return { key: 'seongju', label: '성주군' }
  if (areaCode.includes('goryeong') || areaCode.includes('고령')) return { key: 'goryeong', label: '고령군' }
  if (areaCode.includes('kimcheon') || areaCode.includes('김천')) return { key: 'kimcheon', label: '김천시' }
  if (areaCode.includes('chilgok') || areaCode.includes('칠곡')) return { key: 'chilgok', label: '칠곡군' }
  if (areaCode.includes('gumi') || areaCode.includes('구미')) return { key: 'gumi', label: '구미시' }

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

// 🌟 장소 목록 노출 개수를 5개로 축소 설정 완료
const pageSize = 5
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

const getPlaceIdentifier = (place) => String(place?.content_id ?? place?.id ?? '')

const getAverageRating = (reviews) => {
  if (!Array.isArray(reviews) || reviews.length === 0) return 0
  const total = reviews.reduce((sum, item) => sum + Number(item.rating || 0), 0)
  return total / reviews.length
}

const formatAverageRating = (place) => {
  const value = Number(place?.averageRating ?? place?.rating ?? 0)
  return value.toFixed(1)
}

const getReviewCount = (place) => Number(place?.reviewCount ?? place?.review ?? 0)

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
    /(레포츠|스포츠|운동|등산|트레킹|캠핑|자전거|골프|스키|수영|헬스|산책|야외활동)/.test(text)
  ) {
    return 'activity'
  }

  if (
    contentTypeId === 12 ||
    contentTypeId === 14 ||
    contentTypeId === 15 ||
    contentTypeId === 28 ||
    /(관광|명소|문화)/.test(text)
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
  if (id === 'all') return

  const center = regionCenters[id] || regionCenters.all
  map.value.flyTo(center, 13, { duration: 0.8 })
}

const updateMarkers = () => {
  if (!map.value || !markerGroup.value) return

  markerGroup.value.clearLayers()

  const visiblePlaces = filteredPlaces.value
  const MAX_MARKERS = 100
  const placesToShow = visiblePlaces.length > MAX_MARKERS ? visiblePlaces.slice(0, MAX_MARKERS) : visiblePlaces

  placesToShow.forEach(place => {
    L.marker([place.lat, place.lng])
      .bindPopup(`<strong>${place.name}</strong><br/>${place.region || ''}`)
      .addTo(markerGroup.value)
  })
}

const initMap = () => {
  map.value = L.map('map').setView(regionCenters.all, 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map.value)

  markerGroup.value = L.layerGroup().addTo(map.value)
  mapBounds.value = map.value.getBounds()

  map.value.on('moveend zoomend', () => {
    mapBounds.value = map.value.getBounds()
    updateMarkers()
  })
}

const syncPlaceReviewState = (place, reviews) => {
  const identifier = getPlaceIdentifier(place)
  const index = places.value.findIndex(item => getPlaceIdentifier(item) === identifier)
  if (index === -1) return

  const average = getAverageRating(reviews)
  const nextValue = {
    ...places.value[index],
    reviews,
    reviewCount: reviews.length,
    averageRating: average,
    rating: average.toFixed(1),
    review: reviews.length
  }

  places.value[index] = nextValue

  if (selectedPlace.value && getPlaceIdentifier(selectedPlace.value) === identifier) {
    selectedPlace.value = nextValue
  }

  if (reviewTargetPlace.value && getPlaceIdentifier(reviewTargetPlace.value) === identifier) {
    reviewTargetPlace.value = nextValue
  }
}

const loadReviewsForPlace = async (place) => {
  const identifier = getPlaceIdentifier(place)
  if (!identifier) return

  try {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
    const res = await fetch(`${API_BASE}/places/${identifier}/reviews`)
    if (!res.ok) throw new Error(`리뷰 조회 실패: ${res.status}`)

    const reviews = await res.json()
    syncPlaceReviewState(place, reviews)
  } catch (err) {
    console.error('리뷰 조회 실패', err)
  }
}

const loadReviewsForPlaces = async () => {
  if (!places.value.length) return
  await Promise.all(places.value.map(place => loadReviewsForPlace(place)))
}

async function fetchPlaces() {
  try {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
    const url = `${API_BASE}/places`

    const res = await fetch(url)
    if (!res.ok) {
      const txt = await res.text()
      console.error('places fetch failed status', res.status, txt)
      return
    }

    const data = await res.json()

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

    await loadReviewsForPlaces()
    mapBounds.value = map.value.getBounds()
    updateMarkers()
  } catch (err) {
    console.error('fetchPlaces error', err)
  }
}

const submitReview = async () => {
  if (!reviewTargetPlace.value) return

  const rating = Number(reviewDraft.value)
  if (!Number.isFinite(rating) || rating < 0 || rating > 10) return

  reviewSubmitting.value = true

  try {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
    const placeId = getPlaceIdentifier(reviewTargetPlace.value)
    const res = await fetch(`${API_BASE}/places/${placeId}/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating })
    })

    if (!res.ok) throw new Error(`리뷰 저장 실패: ${res.status}`)
    await loadReviewsForPlace(reviewTargetPlace.value)
    closeReviewModal()
  } catch (err) {
    console.error('리뷰 저장 실패', err)
  } finally {
    reviewSubmitting.value = false
  }
}

onMounted(() => {
  initMap()
  fetchPlaces()
})

watch(regions, (nextRegions) => {
  if (activeRegion.value !== 'all' && !nextRegions.some(item => item.id === activeRegion.value)) {
    activeRegion.value = 'all'
  }
}, { immediate: true })

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

    <!-- 필터 컨트롤 영역 -->
    <div class="controls">
      <div class="filter-row">
        <span class="filter-label">카테고리</span>
        <div class="filter-buttons">
          <button
            v-for="item in categories"
            :key="item.id"
            :class="{ selected: activeCategory === item.id }"
            @click="setCategory(item.id)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>

      <div class="filter-row">
        <span class="filter-label">권역</span>
        <div class="filter-buttons">
          <button
            v-for="item in regions"
            :key="item.id"
            :class="{ selected: activeRegion === item.id }"
            @click="setRegion(item.id)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 대화형 컨텐츠 섹션 (지도 & 리스트) -->
    <div class="main-content-layout">
      <!-- 🗺️ 왼쪽/상단: 지도 영역 -->
      <div class="map-section">
        <div class="map-card">
          <div class="map-header">
            <span class="map-title">구미시 인근 지도 영역</span>
          </div>
          <div id="map" class="map-view"></div>
        </div>
        <button class="current-location-button" type="button">
          현재 위치로 이동
        </button>
      </div>

      <!-- 📋 오른쪽/하단: 리스트 영역 (5개 고정 뷰) -->
      <section class="place-list">
        <h3>지도 내 장소 목록</h3>

        <div v-if="filteredPlaces.length === 0" class="empty-message">
          현재 지도 범위에 표시할 장소가 없습니다.
        </div>

        <div v-else class="place-cards">
          <article class="place-card" v-for="place in displayedPlaces" :key="place.id">
            <div class="place-image-wrap">
              <img
                :src="place.image || getDefaultImage(place)"
                :alt="place.name"
                :class="['place-image', { 'is-default': !place.image }]"
              />
            </div>

            <div class="place-info">
              <strong>{{ place.name }}</strong>
              <span>{{ place.region }}</span>
            </div>

            <div class="place-meta">
              <div class="place-rating">
                <strong>★ {{ formatAverageRating(place) }}</strong>
                <span>({{ getReviewCount(place) }}명)</span>
              </div>

              <div class="place-actions">
                <button class="detail-button" type="button" @click="openPlaceDetail(place)">
                  상세보기
                </button>
                <button class="review-button" type="button" @click="openReviewModal(place)">
                  리뷰 작성
                </button>
              </div>
            </div>
          </article>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="filteredPlaces.length > 0" class="pagination">
          <button class="page-nav" type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
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

          <button class="page-nav" type="button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
            다음
          </button>
        </div>
      </section>
    </div>

    <!-- 모달 창 영역들 -->
    <div v-if="selectedPlace" class="detail-modal-overlay" @click.self="closePlaceDetail">
      <div class="detail-modal">
        <button class="detail-modal-close" type="button" @click="closePlaceDetail">×</button>
        <div class="detail-modal-content">
          <div class="detail-modal-image-wrap">
            <img
              :src="selectedPlace.image || getDefaultImage(selectedPlace)"
              :alt="selectedPlace.name"
              class="detail-modal-image"
            />
          </div>
          <div class="detail-modal-info">
            <span class="detail-chip">{{ getTypeLabel(selectedPlace.type) }}</span>
            <h3>{{ selectedPlace.name }}</h3>
            <p class="detail-address">{{ selectedPlace.address || selectedPlace.region }}</p>
            <div class="detail-meta-row">
              <span>평점: ★ {{ formatAverageRating(selectedPlace) }}</span>
              <span>리뷰수: {{ getReviewCount(selectedPlace) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="reviewModalOpen && reviewTargetPlace" class="detail-modal-overlay" @click.self="closeReviewModal">
      <div class="detail-modal review-modal">
        <button class="detail-modal-close" type="button" @click="closeReviewModal">×</button>
        <div class="review-modal-body">
          <h3>{{ reviewTargetPlace.name }}</h3>
          <p class="detail-address">0~10점까지 별점으로 입력할 수 있습니다.</p>
          <div class="review-stars">
            <div
              v-for="star in 5"
              :key="star"
              class="star-wrapper"
              @click="selectHalfStar($event, star)"
            >
              <span class="star-empty">★</span>
              <span
                class="star-filled"
                :style="{ width: getStarFill(star) + '%' }"
              >
                ★
              </span>
            </div>
          </div>
          <div class="review-score-text">선택한 점수: {{ reviewDraft }}/10</div>
          <div class="review-actions">
            <button class="review-submit" type="button" :disabled="reviewSubmitting" @click="submitReview">
              {{ reviewSubmitting ? '저장 중...' : '리뷰 저장' }}
            </button>
            <button class="ghost-button" type="button" @click="closeReviewModal">취소</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 전체 여백 최소화 및 가로 폭 확장 */
.map-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 16px;
}

.topbar h1 {
  margin-bottom: 24px;
  font-size: 1.8rem;
  font-weight: 800;
}

/* 필터 행 */
.controls {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 24px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-label {
  min-width: 70px;
  font-weight: 700;
  font-size: 0.95rem;
  color: #1a1a1a;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

button {
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: #fff;
  color: #4b5563;
  transition: all 0.2s ease;
}

button:hover {
  background: #f9fafb;
}

button.selected {
  background: #7c5cfc;
  color: #fff;
  border-color: #7c5cfc;
}

/* 🌟 반응형 2단 레이아웃 (지도 좌측 고정 높이, 리스트 우측 배치 유지) */
.main-content-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 28px;
  align-items: start; /* 높이가 달라도 상단 정렬을 일치시킴 */
}

@media (min-width: 1024px) {
  .main-content-layout {
    grid-template-columns: 1.2fr 1fr;
    align-items: start;
  }
}

/* 지도 영역 */
.map-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.map-card {
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.map-header {
  padding: 14px 20px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.map-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: #111827;
}

.map-view {
  width: 100%;
  height: 500px;
  position: relative;
  z-index: 1;
}

.current-location-button {
  width: 100%;
  border: none;
  background: #7c5cfc;
  color: #fff;
  padding: 14px;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.current-location-button:hover {
  background: #6a48e8;
}

/* 📋 우측 장소 목록 영역 */
.place-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: flex-start;
}

.place-list h3 {
  margin: 0 0 16px;
  font-size: 1.2rem;
  font-weight: 700;
  color: #111827;
  text-align: left;
}

.place-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.place-card {
  display: grid;
  grid-template-columns: 64px 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 12px 16px; /* 5개 컴팩트 카드에 맞춘 내부 마진 조절 */
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.place-card:hover {
  border-color: #9ca3af;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.place-image-wrap {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  overflow: hidden;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.place-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.place-image.is-default {
  padding: 8px;
  box-sizing: border-box;
}

.place-info {
  text-align: left;
}

.place-info strong {
  display: block;
  font-size: 0.95rem;
  color: #111827;
  margin-bottom: 2px;
}

.place-info span {
  color: #6b7280;
  font-size: 0.85rem;
}

.place-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.place-rating {
  text-align: right;
  min-width: 80px;
}

.place-rating strong {
  display: block;
  color: #eab308;
  font-size: 0.9rem;
}

.place-rating span {
  color: #9ca3af;
  font-size: 0.8rem;
}

.place-actions {
  display: flex;
  gap: 6px;
}

.detail-button,
.review-button {
  font-size: 0.8rem;
  padding: 6px 12px;
  border-radius: 8px;
}

.review-button {
  background: #111;
  color: #fff;
  border-color: #111;
}

.review-button:hover {
  background: #1f2937;
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 20px;
}

.page-nav,
.page-number {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #374151;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  min-width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.page-number.selected {
  background: #7c5cfc;
  color: #fff;
  border-color: #7c5cfc;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.empty-message {
  padding: 40px;
  text-align: center;
  border: 1px dashed #d1d5db;
  border-radius: 14px;
  background: #f9fafb;
  color: #9ca3af;
  font-size: 0.9rem;
}

/* 모달 레이아웃 */
.detail-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 1000;
}

.detail-modal {
  width: min(640px, 100%);
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  position: relative;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.detail-modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  border: none;
  background: #f3f4f6;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 1.1rem;
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 0;
}

.detail-modal-content {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 20px;
  align-items: start;
  text-align: left;
}

@media (max-width: 640px) {
  .detail-modal-content {
    grid-template-columns: 1fr;
  }
}

.detail-modal-image-wrap {
  width: 100%;
  height: 180px;
  border-radius: 12px;
  overflow: hidden;
  background: #f3f4f6;
}

.detail-modal-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-chip {
  display: inline-block;
  padding: 4px 10px;
  background: #111;
  color: #fff;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.detail-modal-info h3 {
  margin: 0 0 6px 0;
  font-size: 1.3rem;
  font-weight: 800;
}

.detail-address {
  margin: 0 0 12px;
  color: #6b7280;
  font-size: 0.9rem;
}

.detail-meta-row {
  display: flex;
  gap: 16px;
  color: #374151;
  font-weight: 700;
  font-size: 0.9rem;
}

/* 별점 모달 */
.detail-modal.review-modal {
  width: min(440px, 100%);
}

.review-modal-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 16px 0 0 0;
}

.review-stars {
  display: flex;
  gap: 4px;
}

.star-wrapper {
  position: relative;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 36px;
}

.star-empty {
  color: #e5e7eb;
}

.star-filled {
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  color: #f59e0b;
}

.review-score-text {
  font-size: 1.1rem;
  font-weight: 700;
}

.review-actions {
  display: flex;
  gap: 10px;
  width: 100%;
}

.review-submit {
  flex: 1;
  background: #111;
  color: white;
  border-color: #111;
}

.ghost-button {
  flex: 1;
  background: #f3f4f6;
  color: #374151;
  border-color: #e5e7eb;
}
</style>