<template>
  <div class="selector-wrap">
    <!-- 타이틀 -->
    <div class="title-area">
      <h2 class="title">관심 있는 분야를 선택하세요.</h2>
      <p class="subtitle">선택한 취향에 맞는 맞춤 정보를 추천해드려요!</p>
    </div>

    <!-- 카테고리 그리드 -->
    <div class="category-grid">
      <div 
        v-for="category in categories" 
        :key="category.id"
        @click="toggleCategory(category.id)"
        :class="['category-card', { selected: selectedCategory === category.id }]"
      >
        <!-- 카테고리 이미지 영역 -->
        <div class="card-image-wrapper">
          <img :src="category.imgUrl" :alt="category.title" class="card-image" />
          <div class="card-image-overlay"></div>
        </div>
        
        <!-- 텍스트 영역 -->
        <div class="card-content">
          <h3 class="card-title">{{ category.title }}</h3>
          <p class="card-tags">{{ category.tags }}</p>
          <p class="card-desc">{{ category.desc }}</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 하단 완료 버튼 -->
  <div class="button-area">
    <button @click="submitSelection" class="submit-btn">선택 완료</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// assets 폴더의 이미지 연결
import sportsImg from '../assets/exercise.png'
import foodImg from '../assets/food.png'
import travelImg from '../assets/travel.png'
import shoppingImg from '../assets/shopping.png'

const categories = [
  { id: 'sports', title: '운동', tags: '헬스, 러닝, 등산 등', desc: '건강한 라이프스타일 정보를 받아보세요!', imgUrl: sportsImg },
  { id: 'food', title: '음식', tags: '맛집, 카페, 지역 먹거리 등', desc: '맛있는 정보를 받아보세요!', imgUrl: foodImg },
  { id: 'travel', title: '여행', tags: '관광지, 숨은 명소, 여행 코스 등', desc: '여행 정보를 받아보세요!', imgUrl: travelImg },
  { id: 'shopping', title: '쇼핑', tags: '지역 쇼핑 정보, 핫플, 특산물 등', desc: '쇼핑 정보를 받아보세요!', imgUrl: shoppingImg }
]

// 💡 1개만 선택하므로 배열([]) 대신 초기값 null인 문자열/식별자 상태로 변경
const selectedCategory = ref(null)

// 💡 선택 토글 로직 수정
const toggleCategory = (id) => {
  if (selectedCategory.value === id) {
    // 이미 선택된 것을 다시 누르면 선택 해제
    selectedCategory.value = null
  } else {
    // 다른 것을 누르면 해당 카테고리로 단일 교체
    selectedCategory.value = id
  }
}

const submitSelection = () => {
  if (!selectedCategory.value) {
    alert('카테고리를 선택해 주세요.')
    return
  }
  
  // 현재 선택된 카테고리의 한글 타이틀 찾기
  const targetCategory = categories.find(c => c.id === selectedCategory.value)
  alert(`선택된 카테고리: ${targetCategory ? targetCategory.title : selectedCategory.value}`)
}
</script>

<style scoped>
.selector-wrap {
  flex: 1;
}
.title-area {
  margin-bottom: 32px;
}
.title {
  font-size: 24px;
  font-weight: 800;
  color: #111;
  margin: 0;
  letter-spacing: -0.5px;
}
.subtitle {
  font-size: 15px;
  color: #666;
  margin: 8px 0 0 0;
}
.category-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.category-card {
  border: 1.5px solid #dee2e6;
  border-radius: 16px;
  overflow: hidden;
  background-color: #fff;
  cursor: pointer;
  transition: all 0.25s ease;
  user-select: none;
  display: flex;
  flex-direction: column;
}
.category-card:hover {
  border-color: #868e96;
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.06);
}
.category-card.selected {
  border-color: #111;
  box-shadow: 0 0 0 1.5px #111;
}
.card-image-wrapper {
  position: relative;
  width: 100%;
  height: 140px;
  overflow: hidden;
  background-color: #f1f3f5;
}
.card-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
}
.category-card:hover .card-image {
  transform: scale(1.05);
}
.card-image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0,0,0,0) 50%, rgba(0,0,0,0.05) 100%);
}
.card-content {
  padding: 24px 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.card-title {
  font-size: 18px;
  font-weight: 800;
  color: #111;
  margin: 0 0 6px 0;
}
.card-tags {
  font-size: 12px;
  color: #868e96;
  font-weight: 600;
  margin: 0 0 8px 0;
}
.card-desc {
  font-size: 13px;
  color: #495057;
  line-height: 1.5;
  margin: 0;
}
.button-area {
  margin-top: 40px;
}
.submit-btn {
  width: 100%;
  padding: 16px 0;
  border: 1.5px solid #ced4da;
  background-color: #fff;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  color: #343a40;
  cursor: pointer;
  transition: all 0.2s;
}
.submit-btn:hover {
  background-color: #111;
  color: #fff;
  border-color: #111;
}

/* 📱 모바일 최적화: 한 화면에 4개가 다 보이도록 조절 */
@media (max-width: 640px) {
  .title-area {
    margin-bottom: 16px;
  }
  .title {
    font-size: 18px;
  }
  .subtitle {
    font-size: 12px;
    margin-top: 4px;
  }
  .category-grid {
    grid-template-columns: 1fr 1fr; /* 모바일에서도 2x2 유지 */
    gap: 10px; /* 카드 간격 축소 */
  }
  .card-image-wrapper {
    height: 75px; /* 이미지 영역 대폭 축소 */
  }
  .card-content {
    padding: 10px 8px; /* 패딩 축소 */
  }
  .card-title {
    font-size: 14px; /* 글꼴 크기 축소 */
    margin-bottom: 2px;
  }
  .card-tags {
    font-size: 10px;
    margin-bottom: 4px;
  }
  .card-desc {
    display: none; /* 설명글은 모바일에서 숨겨서 공간 확보 */
  }
  .button-area {
    margin-top: 16px;
  }
  .submit-btn {
    padding: 10px 0;
    font-size: 14px;
    border-radius: 8px;
  }
}
</style>