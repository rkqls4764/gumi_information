<!-- src/components/CategorySelector.vue -->
<template>
  <!-- 외부 레이아웃 영향을 받지 않고 카드 높이를 일정하게 꽉 잡아두는 고정용 최상위 컨테이너 -->
  <div class="category-panel-container">
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
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['submit'])

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

const selectedCategory = ref(null)

const toggleCategory = (id) => {
  if (selectedCategory.value === id) {
    selectedCategory.value = null
  } else {
    selectedCategory.value = id
  }
}

const submitSelection = () => {
  console.log('선택값:', selectedCategory.value)

  if (!selectedCategory.value) {
    alert('카테고리를 선택해 주세요.')
    return
  }
  
  // 현재 선택된 카테고리의 한글 타이틀 찾기 (예: "운동")
  const targetCategory = categories.find(c => c.id === selectedCategory.value)
  const categoryTitle = targetCategory ? targetCategory.title : selectedCategory.value
  
  // 💡 [수정] 알림창만 띄우는 대신, 부모(App.vue)로 'submit' 이벤트와 한글 카테고리명을 전달합니다.
  emit('category-selected', selectedCategory.value)
}
</script>

<style scoped>
.category-panel-container {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 100%;
}

.selector-wrap {
  flex: 0 0 auto;
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
  height: auto;
}
.category-card:hover {
  border-color: #b8a4fc;
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(124, 92, 252, 0.12);
}
.category-card.selected {
  border-color: #7c5cfc;
  box-shadow: 0 0 0 1.5px #7c5cfc;
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
  margin-top: 32px;
  flex: 0 0 auto;
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
  background-color: #7c5cfc;
  color: #fff;
  border-color: #7c5cfc;
}

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
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .card-image-wrapper {
    height: 75px;
  }
  .card-content {
    padding: 10px 8px;
  }
  .card-title {
    font-size: 14px;
    margin-bottom: 2px;
  }
  .card-tags {
    font-size: 10px;
    margin-bottom: 4px;
  }
  .card-desc {
    display: none;
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