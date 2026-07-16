<template>
  <div class="recommend-wrap">
    <h2>이런 장소는 어때요?</h2>

    <div class="place-grid">
      <div
        v-for="place in places"
        :key="place.content_id"
        class="place-card"
      >
        <img
          :src="place.firstimage || getDefaultImage(place)"
          class="place-img"
        />

        <div class="place-content">
          <h3 class="place-title">
            {{ place.title }}
          </h3>

          <p class="place-address">
            {{ place.addr1 }}
          </p>

          <div class="place-rating">
            ⭐ {{ place.avg_rating || 0 }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const allPlaces = ref([])
const isLoaded = ref(false)

const props = defineProps({
  category: String
})

const places = ref([])

watch(
  () => props.category,
  async (newCategory) => {

    // 최초 한번만 API 호출
    if (!isLoaded.value) {
      const { data } = await axios.get(
        'https://gumi-information.onrender.com/places'
      )

      allPlaces.value = data
      isLoaded.value = true
    }


    let filtered = [...allPlaces.value]


    // 관심사 선택 안함
    if (!newCategory) {

      places.value = filtered
        .sort(
          (a,b)=>
          (b.avg_rating || 0) -
          (a.avg_rating || 0)
        )
        .slice(0,6)

      return
    }


    const categoryMap = {
      sports:[28],
      food:[39],
      travel:[12,14,15,25],
      shopping:[38]
    }


    const targetTypes =
      categoryMap[newCategory] || []


    places.value = filtered
      .filter(place =>
        targetTypes.includes(
          Number(place.content_type_id)
        )
      )
      .sort(
        (a,b)=>
        (b.avg_rating || 0) -
        (a.avg_rating || 0)
      )
      .slice(0,6)

  },
  { immediate:true }
)

const sortedPlaces = places

const getMaxItems = () => {
  if (window.innerWidth <= 768) return 2
  if (window.innerWidth <= 1024) return 4
  return 6
}

const createIconImage = (icon) =>
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="250">
      <rect width="400" height="250" fill="#f3f4f6"/>
      <text
        x="200"
        y="145"
        text-anchor="middle"
        font-size="80"
      >
        ${icon}
      </text>
    </svg>
  `)

const getDefaultImage = (place) => {
  const type = Number(place.content_type_id)

  if (type === 39) return createIconImage('🍴')
  if ([12, 14, 15, 25].includes(type))
    return createIconImage('📍')
  if (type === 28)
    return createIconImage('🚴')
  if (type === 38)
    return createIconImage('🛍️')

  return createIconImage('📌')
}
</script>

<style scoped>
.recommend-wrap {
  padding: 10px;
}

.recommend-wrap h2 {
  font-size: 22px;
  font-weight: 800;
  color: #111;
  letter-spacing: -0.5px;
  margin: 0 0 20px;
}

.place-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* 태블릿 */
@media (max-width: 1200px) {
  .place-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 모바일 */
@media (max-width: 768px) {
  .place-grid {
    grid-template-columns: 1fr;
  }
}

.place-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  margin-bottom: 20px;
  transition: 0.2s;
}

.place-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(124, 92, 252, 0.15);
}

.place-img {
  width: 100%;
  height: 220px;
  object-fit: cover;
  display: block;
}

.place-content {
  padding: 14px;
}

.place-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #222;
}

.place-address {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 10px;
}

.place-rating {
  font-size: 15px;
  font-weight: 600;
  color: #ff9800;
}

.rating{
  font-weight:bold;
}
</style>