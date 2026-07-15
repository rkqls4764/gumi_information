<!-- LocalInfoView.vue -->
<template>
  <div class="local-info-container">
    <!-- 상단 요약 & 카테고리 필터 탭 -->
    <div class="filter-header">
      <div class="tag-filters">
        <button 
          v-for="tab in tabs" 
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="['filter-btn', { active: activeTab === tab.value }]"
        >
          {{ tab.label }}
        </button>
      </div>
      <span class="results-count">총 {{ filteredPlaces.length }}개의 장소</span>
    </div>

    <!-- 관광지 카드 리스트 -->
    <div class="places-grid">
      <div 
        v-for="place in filteredPlaces" 
        :key="place.id" 
        class="place-card"
        @click="selectPlace(place)"
      >
        <div class="card-image-placeholder">
          <span class="emoji-icon">{{ place.emoji }}</span>
        </div>
        <div class="card-body">
          <span class="place-tag">{{ place.category }}</span>
          <h3 class="place-title">{{ place.title }}</h3>
          <p class="place-addr">📍 {{ place.address }}</p>
          <p class="place-desc">{{ place.description }}</p>
          <div class="card-footer">
            <span class="like-badge">❤️ {{ place.likes }}</span>
            <span class="detail-btn-text">상세보기 →</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 상세 보기 모달 창 -->
    <div v-if="selectedPlace" class="modal-overlay" @click.self="selectedPlace = null">
      <div class="modal-content">
        <button class="close-btn" @click="selectedPlace = null">✕</button>
        <div class="modal-hero">
          <span class="modal-emoji">{{ selectedPlace.emoji }}</span>
        </div>
        <div class="modal-body">
          <span class="place-tag">{{ selectedPlace.category }}</span>
          <h2>{{ selectedPlace.title }}</h2>
          <p class="modal-addr"><strong>주소:</strong> {{ selectedPlace.address }}</p>
          <p class="modal-tel" v-if="selectedPlace.tel"><strong>문의처:</strong> {{ selectedPlace.tel }}</p>
          <hr class="divider" />
          <p class="modal-desc">{{ selectedPlace.details }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 카테고리 탭 목록
const activeTab = ref('all')
const tabs = [
  { label: '전체 보기', value: 'all' },
  { label: '⛰️ 자연/명소', value: 'nature' },
  { label: '☕ 맛집/카페', value: 'food' },
  { label: '🎨 문화/체험', value: 'culture' }
]

// 선택된 상세 보기 장소 (모달용)
const selectedPlace = ref(null)
const selectPlace = (place) => {
  selectedPlace.value = place
}

// 구미/경북 실제 정보 더미 데이터 
const places = ref([
  {
    id: 1,
    title: '금오산 도립공원',
    category: 'nature',
    emoji: '⛰️',
    address: '경상북도 구미시 금오산로 402-4',
    tel: '054-480-4601',
    description: '아름다운 기암괴석과 폭포, 산책로가 어우러진 구미의 대표 명산입니다.',
    details: '금오산은 해발 976m로 산 정상 아래 현월봉, 약사암 등이 절경을 이룹니다. 산세가 완만하고 잘 정돈된 둘레길과 금오지 올레길이 있어 남녀노소 산책하기 아주 좋으며, 가을철 단풍이 특히 아름다운 경북의 명소입니다.',
    likes: 128
  },
  {
    id: 2,
    title: '금리단길 카페거리',
    category: 'food',
    emoji: '☕',
    address: '경상북도 구미시 원평동 일대',
    tel: '',
    description: '구미역 뒤편 주택가를 개조해 감성 가득한 카페와 소품샵이 모여있는 거리입니다.',
    details: '금오산 올라가는 길목(원평동 일대)에 위치한 힙한 감성의 골목길입니다. 개성 넘치는 개인 로스터리 카페, 감성 일식당, 아기자기한 서점과 소품샵들이 가득해 연인들의 데이트 코스나 친구들과 가벼운 나들이로 사랑받고 있습니다.',
    likes: 95
  },
  {
    id: 3,
    title: '구미 과학관',
    category: 'culture',
    emoji: '🚀',
    address: '경상북도 구미시 3공단1로 244-77',
    tel: '054-476-6501',
    description: '아이들과 함께 우주와 기초과학을 재미있게 체험하고 배울 수 있는 공간입니다.',
    details: '낙동강 체육공원 근처에 위치한 어린이/가족 맞춤형 과학 체험 시설입니다. 플라네타리움(천체투영관)과 4D 시어터가 있어 생생하게 우주를 구경할 수 있으며, 주말마다 흥미로운 만들기 과학교실 프로그램이 운영됩니다.',
    likes: 64
  },
  {
    id: 4,
    title: '낙동강 체육공원',
    category: 'nature',
    emoji: '🚴',
    address: '경상북도 구미시 낙동강변로 820',
    tel: '054-480-6181',
    description: '국내 최대 규모의 둔치 체육공원으로 피크닉, 캠핑, 자전거를 즐기기 좋습니다.',
    details: '엄청난 규모의 잔디밭과 축구장, 야구장, 풋살장 등 체육 인프라가 완비된 공원입니다. 자전거 대여소에서 자전거를 타거나, 가을에는 핑크뮬리와 메밀꽃밭이 만발해 출사지로도 인기가 대단하며 오토캠핑장 시설도 훌륭합니다.',
    likes: 112
  },
  {
    id: 5,
    title: '선산 5일장',
    category: 'culture',
    emoji: '🍎',
    address: '경상북도 구미시 선산읍 남문로 일원',
    tel: '',
    description: '매월 2일, 7일에 열리는 경북에서 손꼽히는 큰 규모의 전통 오일장입니다.',
    details: '조선시대부터 유서 깊은 전통 시장으로, 장날만 되면 선산 일대에 수많은 노점과 먹거리가 가득 들어섭니다. 직접 기른 신선한 야채부터 씨앗호떡, 옛날 통닭, 손칼국수 등 군침 도는 전통 간식 투어를 하기에 완벽한 장소입니다.',
    likes: 82
  }
])

// 탭 필터링 로직
const filteredPlaces = computed(() => {
  if (activeTab.value === 'all') return places.value
  return places.value.filter(place => place.category === activeTab.value)
})
</script>

<style scoped>
.local-info-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 필터 헤더 */
.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  border-bottom: 1.5px solid #f1f3f5;
  padding-bottom: 16px;
}

.tag-filters {
  display: flex;
  gap: 8px;
}

.filter-btn {
  background-color: #f1f3f5;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background-color: #e9ecef;
}

.filter-btn.active {
  background-color: #111;
  color: #fff;
}

.results-count {
  font-size: 14px;
  color: #868e96;
  font-weight: 500;
}

/* 관광지 카드 그리드 */
.places-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.place-card {
  background-color: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.place-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.06);
}

.card-image-placeholder {
  background-color: #f1f3f5;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e9ecef;
}

.emoji-icon {
  font-size: 48px;
}

.card-body {
  padding: 16px;
}

.place-tag {
  font-size: 11px;
  color: #2b8a3e;
  background-color: #e8f5e9;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
}

.place-title {
  font-size: 18px;
  font-weight: 800;
  margin: 10px 0 6px 0;
  color: #212529;
}

.place-addr {
  font-size: 12px;
  color: #868e96;
  margin: 0 0 10px 0;
}

.place-desc {
  font-size: 13px;
  color: #495057;
  line-height: 1.4;
  margin: 0 0 16px 0;
  /* 말줄임표 처리 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
}

.like-badge {
  color: #e03131;
}

.detail-btn-text {
  color: #111;
}

/* 모달 상세 창 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-content {
  background-color: #ffffff;
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  animation: modalShow 0.25s ease-out;
}

@keyframes modalShow {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(0, 0, 0, 0.4);
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.6);
}

.modal-hero {
  background-color: #e9ecef;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-emoji {
  font-size: 72px;
}

.modal-body {
  padding: 24px;
}

.modal-body h2 {
  font-size: 24px;
  font-weight: 800;
  margin: 10px 0 16px 0;
}

.modal-addr, .modal-tel {
  font-size: 14px;
  color: #495057;
  margin: 6px 0;
}

.divider {
  border: 0;
  border-top: 1px solid #dee2e6;
  margin: 16px 0;
}

.modal-desc {
  font-size: 15px;
  color: #343a40;
  line-height: 1.6;
}
</style>