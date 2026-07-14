<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import L from 'leaflet'

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

const places = [
  { id: 1, name: '금오산 도립공원', region: '구미시 남동동', type: 'tour', area: 'gumi', rating: '4.6', review: 128, lat: 36.1129, lng: 128.3397 },
  { id: 2, name: '원조 선산곱창', region: '구미시 선산읍', type: 'food', area: 'gumi', rating: '4.4', review: 97, lat: 36.1391, lng: 128.2554 },
  { id: 3, name: '카페 소담', region: '구미시 임은동', type: 'cafe', area: 'gumi', rating: '4.3', review: 64, lat: 36.1045, lng: 128.3532 },
  { id: 4, name: '선산 꽃갈 축제장', region: '구미시 선산읍', type: 'festival', area: 'gumi', rating: '4.5', review: 82, lat: 36.1397, lng: 128.2580 },
  { id: 5, name: '낙동강 체육공원', region: '구미시 도량동', type: 'tour', area: 'gumi', rating: '4.2', review: 53, lat: 36.1222, lng: 128.3238 }
]

const activeCategory = ref('all')
const activeRegion = ref('all')
const map = ref(null)
const markerGroup = ref(null)

const filteredPlaces = computed(() => {
  return places.filter(place => {
    const categoryMatch = activeCategory.value === 'all' || place.type === activeCategory.value
    const regionMatch = activeRegion.value === 'all' || place.area === activeRegion.value
    return categoryMatch && regionMatch
  })
})

const setCategory = (id) => {
  activeCategory.value = id
}

const setRegion = (id) => {
  activeRegion.value = id
}

const updateMarkers = () => {
  if (!map.value || !markerGroup.value) return
  markerGroup.value.clearLayers()

  filteredPlaces.value.forEach(place => {
    L.marker([place.lat, place.lng])
      .bindPopup(`
        <strong>${place.name}</strong><br/>
        ${place.region}<br/>
        ★ ${place.rating} (${place.review})
      `)
      .addTo(markerGroup.value)
  })

  if (filteredPlaces.value.length) {
    const bounds = L.latLngBounds(filteredPlaces.value.map(p => [p.lat, p.lng]))
    map.value.fitBounds(bounds, { padding: [40, 40] })
  }
}

const initMap = () => {
  map.value = L.map('map').setView([36.12, 128.34], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map.value)

  markerGroup.value = L.layerGroup().addTo(map.value)
  updateMarkers()
}

onMounted(() => {
  initMap()
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
      <div class="place-cards">
        <article class="place-card" v-for="place in filteredPlaces" :key="place.id">
          <div class="place-icon">🏙️</div>
          <div class="place-info">
            <strong>{{ place.name }}</strong>
            <span>{{ place.region }}</span>
          </div>
          <div class="place-rating">
            <strong>★ {{ place.rating }}</strong>
            <span>({{ place.review }})</span>
          </div>
          <button class="detail-button">상세보기</button>
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
.place-card { display: grid; grid-template-columns: 52px 1fr auto; gap: 16px; align-items: center; padding: 18px 20px; border: 1px solid #e6e6e6; border-radius: 16px; background: #fff; }
.place-icon { width: 52px; height: 52px; border-radius: 16px; background: #f3f4f6; display: grid; place-items: center; font-size: 1.3rem; }
.place-info strong { display: block; font-size: 1rem; margin-bottom: 4px; }
.place-info span { color: #777; font-size: 0.95rem; }
.place-rating { text-align: right; min-width: 90px; }
.place-rating strong { display: block; color: #222; }
.place-rating span { color: #777; font-size: 0.9rem; }
.detail-button { border: 1px solid #d4d4d4; background: #fff; color: #333; padding: 10px 14px; border-radius: 999px; cursor: pointer; }
.current-location-button { width: 100%; margin-top: 24px; border: none; background: #111; color: #fff; padding: 16px; border-radius: 14px; font-size: 1rem; cursor: pointer; }
</style>